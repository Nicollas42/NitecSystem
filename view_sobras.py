# view_sobras.py
import customtkinter as ctk
from tkinter import ttk, messagebox
import database

class SobrasFrame(ctk.CTkFrame):
    def __init__(self, master, usuario_dados, callback_voltar):
        super().__init__(master)
        self.voltar_menu = callback_voltar
        self.usuario = usuario_dados
        self.produtos = database.PRODUTOS

        # Cria um mapa reverso: Nome -> Código (Para facilitar a busca)
        self.mapa_nomes = {dados['nome']: cod for cod, dados in self.produtos.items()}
        self.lista_nomes = sorted(list(self.mapa_nomes.keys())) # Lista alfabética

        self.montar_layout()
        self.atualizar_tabela()

    def montar_layout(self):
        # 1. CABEÇALHO
        top = ctk.CTkFrame(self, height=50, corner_radius=0)
        top.pack(fill="x", side="top")
        
        ctk.CTkButton(top, text="🔙 Voltar", width=100, fg_color="#555", 
                      command=self.voltar_menu).pack(side="left", padx=(10, 5), pady=10)
        
        ctk.CTkButton(top, text="?", width=30, fg_color="#333", hover_color="#444", 
                      command=self.mostrar_ajuda).pack(side="left", padx=5)

        ctk.CTkLabel(top, text="REGISTRO DE PERDAS (SOBRAS)", font=("Arial", 16, "bold")).pack(side="left", padx=20)

        # 2. FORMULÁRIO
        form = ctk.CTkFrame(self)
        form.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(form, text="Lançar Nova Perda", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=10)

        # --- CAMPO 1: CÓDIGO ---
        ctk.CTkLabel(form, text="Código:").grid(row=1, column=0, padx=10, sticky="w")
        self.entry_cod = ctk.CTkEntry(form, placeholder_text="Ex: 101", width=100)
        self.entry_cod.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        # Evento: Se digitar código e sair, atualiza o Select de nomes
        self.entry_cod.bind("<FocusOut>", self.ao_digitar_codigo)

        # --- CAMPO 2: PRODUTO (AGORA É UM SELECT) ---
        ctk.CTkLabel(form, text="Selecione o Produto:").grid(row=1, column=1, padx=10, sticky="w")
        
        self.combo_prod = ctk.CTkComboBox(form, values=self.lista_nomes, width=300, 
                                          command=self.ao_selecionar_produto)
        self.combo_prod.set("Selecione...") # Começa vazio/neutro
        self.combo_prod.grid(row=2, column=1, padx=10, pady=(0, 10), sticky="ew")

        # --- CAMPO 3: QUANTIDADE ---
        ctk.CTkLabel(form, text="Qtd Perdida:").grid(row=1, column=2, padx=10, sticky="w")
        self.entry_qtd = ctk.CTkEntry(form, placeholder_text="0.00", width=100)
        self.entry_qtd.grid(row=2, column=2, padx=10, pady=(0, 10), sticky="ew")

        # --- CAMPO 4: MOTIVO (VAZIO POR PADRÃO) ---
        ctk.CTkLabel(form, text="Motivo / Justificativa:").grid(row=1, column=3, padx=10, sticky="w")
        
        # Adicionei opção de digitar motivo personalizado se quiser
        self.combo_motivo = ctk.CTkComboBox(form, width=200,
                                            values=["Venceu", "Queimou", "Caiu no chão", "Defeito", "Consumo Interno"])
        self.combo_motivo.set("") # <--- AGORA COMEÇA VAZIO COMO PEDIDO
        self.combo_motivo.grid(row=2, column=3, padx=10, pady=(0, 10))

        # BOTÃO REGISTRAR
        ctk.CTkButton(form, text="REGISTRAR PERDA", fg_color="#C0392B", 
                      command=self.registrar).grid(row=2, column=4, padx=20)

        # 3. HISTÓRICO (TABELA)
        ctk.CTkLabel(self, text="Histórico de Perdas", font=("Arial", 14, "bold")).pack(pady=(10,0))
        
        lista_frame = ctk.CTkFrame(self)
        lista_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Estilo da Tabela (Aumentando a altura da linha para caber mais texto)
        self.style = ttk.Style()
        self.style.configure("Treeview", rowheight=35) # <--- Altura maior para facilitar leitura

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
        self.tree.column("motivo", width=300) # <--- Coluna mais larga para justificativas
        self.tree.column("resp", width=100, anchor="center")

        self.tree.pack(fill="both", expand=True)

    # --- LÓGICA DE AUTO-COMPLETE ---

    def ao_selecionar_produto(self, escolha):
        """Quando seleciona no Select, preenche o Código"""
        if escolha in self.mapa_nomes:
            cod = self.mapa_nomes[escolha]
            self.entry_cod.delete(0, "end")
            self.entry_cod.insert(0, cod)

    def ao_digitar_codigo(self, event=None):
        """Quando digita o Código, seleciona no Select"""
        cod = self.entry_cod.get().strip()
        if cod in self.produtos:
            nome_real = self.produtos[cod]['nome']
            self.combo_prod.set(nome_real)
        else:
            self.combo_prod.set("Produto não encontrado")

    # --- REGISTRO ---

    def registrar(self):
        cod = self.entry_cod.get().strip()
        qtd_txt = self.entry_qtd.get().replace(",", ".")
        motivo = self.combo_motivo.get() # Pega o texto (selecionado ou digitado)

        # Validações
        if cod not in self.produtos:
            messagebox.showerror("Erro", "Selecione um produto válido!")
            return

        if not motivo:
            messagebox.showwarning("Atenção", "Informe o Motivo da perda.")
            self.combo_motivo.focus_set()
            return

        try:
            qtd = float(qtd_txt)
            if qtd <= 0: raise ValueError
        except:
            messagebox.showerror("Erro", "Quantidade inválida!")
            return

        nome = self.produtos[cod]['nome']
        database.registrar_sobra(cod, nome, qtd, motivo, self.usuario['nome'])
        
        messagebox.showinfo("Sucesso", "Perda registrada.")
        
        # Limpar campos
        self.entry_cod.delete(0, "end")
        self.entry_qtd.delete(0, "end")
        self.combo_prod.set("Selecione...")
        self.combo_motivo.set("") # Reseta para vazio
        
        self.atualizar_tabela()

    def atualizar_tabela(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        historico = database.carregar_sobras()
        for h in historico[::-1]:
            self.tree.insert("", "end", values=(h['data'], h['nome'], h['qtd'], h['motivo'], h['operador']))

    def mostrar_ajuda(self):
        msg = """
        🗑️ CONTROLE DE PERDAS

        1. Selecione o Produto na lista (ou digite o código).
        2. Informe a Quantidade.
        3. Escolha ou Digite um Motivo detalhado.
           Ex: "Pão queimou no forno 3" ou "Venceu dia 20".

        * O campo Motivo começa vazio para evitar erros.
        * A tabela abaixo mostra as últimas perdas.
        """
        messagebox.showinfo("Ajuda - Sobras", msg)