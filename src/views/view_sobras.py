# src/views/view_sobras.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from src.controllers.estoque_controller import EstoqueController
from src.models import database

class SobrasFrame(ctk.CTkFrame):
    def __init__(self, master, usuario_dados, callback_voltar):
        super().__init__(master)
        self.voltar_menu = callback_voltar
        self.usuario = usuario_dados
        
        # Conecta com o cérebro do sistema
        self.controller = EstoqueController()
        self.produtos = database.carregar_produtos()

        # Mapa para buscar ID pelo Nome
        self.mapa_nomes = {dados['nome']: cod for cod, dados in self.produtos.items()}
        self.lista_nomes = sorted(list(self.mapa_nomes.keys()))

        self.estilizar_tabelas()
        self.montar_layout()
        self.atualizar_tabela()

    def estilizar_tabelas(self):
        """Aplica o tema escuro na tabela (Igual ao Estoque)"""
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("Treeview",
                        background="#2b2b2b",
                        foreground="white",
                        fieldbackground="#2b2b2b",
                        rowheight=30,
                        font=("Arial", 11),
                        borderwidth=0)
        
        style.configure("Treeview.Heading",
                        background="#1f1f1f",
                        foreground="white",
                        font=("Arial", 12, "bold"),
                        relief="flat")
        
        style.map("Treeview",
                  background=[("selected", "#C0392B")], # Vermelho para combinar com Perda
                  foreground=[("selected", "white")])

    def montar_layout(self):
        # --- CABEÇALHO ---
        top = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color="#222")
        top.pack(fill="x", side="top")
        
        ctk.CTkButton(top, text="🔙 Voltar", width=100, fg_color="#444", hover_color="#555",
                      command=self.voltar_menu).pack(side="left", padx=15, pady=10)
        
        ctk.CTkLabel(top, text="🗑️ REGISTRO DE PERDAS", font=("Arial", 20, "bold"), text_color="#E74C3C").pack(side="left", padx=10)

        # --- FORMULÁRIO ---
        form_frame = ctk.CTkFrame(self, fg_color="#2b2b2b", border_width=1, border_color="#444")
        form_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(form_frame, text="Lançar Nova Perda", font=("Arial", 14, "bold"), text_color="#E74C3C").grid(row=0, column=0, pady=15, padx=15, sticky="w")

        # Linha 1: Produto
        ctk.CTkLabel(form_frame, text="Selecione o Produto:", text_color="#ccc").grid(row=1, column=0, padx=15, sticky="w")
        self.combo_prod = ctk.CTkComboBox(form_frame, width=300, values=self.lista_nomes, command=self.ao_selecionar_produto)
        self.combo_prod.set("Selecione...") 
        self.combo_prod.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="w")

        # Campo ID (Escondido visualmente ou apenas informativo)
        ctk.CTkLabel(form_frame, text="Código:", text_color="#ccc").grid(row=1, column=1, padx=15, sticky="w")
        self.entry_cod = ctk.CTkEntry(form_frame, width=100, placeholder_text="Auto")
        self.entry_cod.grid(row=2, column=1, padx=15, pady=(0, 15), sticky="w")
        self.entry_cod.bind("<FocusOut>", self.ao_digitar_codigo)

        # Linha 2: Quantidade e Motivo
        ctk.CTkLabel(form_frame, text="Qtd Perdida:", text_color="#ccc").grid(row=3, column=0, padx=15, sticky="w")
        
        qtd_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        qtd_frame.grid(row=4, column=0, padx=15, pady=(0, 15), sticky="w")
        
        self.entry_qtd = ctk.CTkEntry(qtd_frame, width=120, placeholder_text="0.00")
        self.entry_qtd.pack(side="left")
        self.lbl_un = ctk.CTkLabel(qtd_frame, text="UN", text_color="gray")
        self.lbl_un.pack(side="left", padx=5)

        ctk.CTkLabel(form_frame, text="Motivo (Obrigatório):", text_color="#ccc").grid(row=3, column=1, padx=15, sticky="w")
        self.combo_motivo = ctk.CTkComboBox(form_frame, width=250, values=["Venceu", "Queimou", "Caiu no chão", "Defeito", "Consumo Interno", "Avaria Transporte"])
        self.combo_motivo.set("")
        self.combo_motivo.grid(row=4, column=1, padx=15, pady=(0, 15), sticky="w")

        # Botão
        ctk.CTkButton(form_frame, text="REGISTRAR PERDA", fg_color="#C0392B", hover_color="#A93226", height=40, font=("Arial", 14, "bold"),
                      command=self.registrar).grid(row=2, column=2, rowspan=3, padx=30, sticky="ew")

        # --- TABELA DE HISTÓRICO ---
        ctk.CTkLabel(self, text="Histórico Recente", font=("Arial", 14, "bold")).pack(anchor="w", padx=20)

        lista_frame = ctk.CTkFrame(self)
        lista_frame.pack(fill="both", expand=True, padx=20, pady=(5, 20))

        cols = ("data", "prod", "qtd", "motivo", "resp")
        self.tree = ttk.Treeview(lista_frame, columns=cols, show="headings", selectmode="none")
        
        self.tree.heading("data", text="DATA/HORA")
        self.tree.heading("prod", text="PRODUTO")
        self.tree.heading("qtd", text="QTD")
        self.tree.heading("motivo", text="MOTIVO")
        self.tree.heading("resp", text="RESPONSÁVEL")

        self.tree.column("data", width=120, anchor="center")
        self.tree.column("prod", width=250)
        self.tree.column("qtd", width=80, anchor="center")
        self.tree.column("motivo", width=250)
        self.tree.column("resp", width=100, anchor="center")

        self.tree.pack(fill="both", expand=True)

    # --- LÓGICA ---

    def ao_selecionar_produto(self, escolha):
        if escolha in self.mapa_nomes:
            cod = self.mapa_nomes[escolha]
            self.entry_cod.delete(0, "end")
            self.entry_cod.insert(0, cod)
            
            # Atualiza a unidade visualmente
            un = self.produtos[cod].get('unidade', 'UN')
            self.lbl_un.configure(text=un)

    def ao_digitar_codigo(self, event=None):
        cod = self.entry_cod.get().strip()
        if cod in self.produtos:
            nome = self.produtos[cod]['nome']
            self.combo_prod.set(nome)
            un = self.produtos[cod].get('unidade', 'UN')
            self.lbl_un.configure(text=un)

    def registrar(self):
        cod = self.entry_cod.get().strip()
        qtd = self.entry_qtd.get().replace(",", ".")
        motivo = self.combo_motivo.get()

        if not cod or cod not in self.produtos:
            messagebox.showwarning("Erro", "Selecione um produto válido.")
            return

        if not motivo:
            messagebox.showwarning("Erro", "Informe o motivo da perda.")
            return

        # Usa o Controller (o mesmo do estoque) para garantir a integridade
        # tipo="PERDA" faz o sistema entender que é para subtrair e registrar log
        sucesso, msg = self.controller.movimentar_estoque(
            cod=cod,
            qtd=qtd, # O controller sabe que PERDA deve subtrair
            tipo="PERDA",
            motivo=motivo,
            usuario=self.usuario['nome']
        )

        if sucesso:
            messagebox.showinfo("Sucesso", "Perda registrada!")
            self.limpar()
            self.atualizar_tabela()
        else:
            messagebox.showerror("Erro", msg)

    def limpar(self):
        self.entry_cod.delete(0, "end")
        self.entry_qtd.delete(0, "end")
        self.combo_prod.set("Selecione...")
        self.combo_motivo.set("")

    def atualizar_tabela(self):
        # Limpa tabela
        for i in self.tree.get_children(): self.tree.delete(i)
        
        # Busca histórico de movimentos
        historico = database.carregar_json(database.ARQ_MOVIMENTOS)
        
        # Filtra só o que for PERDA
        perdas = [h for h in historico if h['tipo'] == 'PERDA']

        # Mostra do mais recente pro mais antigo
        for h in perdas[::-1]:
            # Como a qtd é salva negativa no banco (ex: -5), usamos abs() pra mostrar 5 na tela
            qtd_visual = abs(float(h['qtd']))
            self.tree.insert("", "end", values=(h['data'], h['nome'], qtd_visual, h['motivo'], h['usuario']))