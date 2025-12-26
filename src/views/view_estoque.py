# src/views/view_estoque.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from src.controllers.estoque_controller import EstoqueController
from src.models import database

class EstoqueFrame(ctk.CTkFrame):
    def __init__(self, master, callback_voltar):
        super().__init__(master)
        self.voltar_menu = callback_voltar
        self.controller = EstoqueController()
        
        # Dados em Memória
        self.produtos = database.carregar_produtos()
        
        # Configura estilo visual das tabelas para o Modo Escuro
        self.estilizar_tabelas()
        
        self.montar_layout()
        self.atualizar_tabelas()

    def estilizar_tabelas(self):
        """Força o Treeview a ter cores escuras compatíveis com o tema"""
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
                  background=[("selected", "#2CC985")],
                  foreground=[("selected", "black")])

    def montar_layout(self):
        # --- CABEÇALHO ---
        top = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color="#222")
        top.pack(fill="x", side="top")
        
        ctk.CTkButton(top, text="🔙 Voltar", width=100, fg_color="#444", hover_color="#555",
                      command=self.voltar_menu).pack(side="left", padx=15, pady=10)
        
        ctk.CTkLabel(top, text="📦 GESTÃO DE ESTOQUE 2.0", font=("Arial", 20, "bold"), text_color="#eee").pack(side="left", padx=10)

        # --- SISTEMA DE ABAS ---
        self.tabview = ctk.CTkTabview(self, anchor="nw")
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)

        self.tab_cadastro = self.tabview.add("📝 Cadastro / Edição")
        self.tab_mov = self.tabview.add("🔄 Movimentação (Entrada/Saída)")
        self.tab_lista = self.tabview.add("📋 Visão Geral")

        self.montar_aba_cadastro()
        self.montar_aba_movimentacao()
        self.montar_aba_lista()

    def montar_aba_cadastro(self):
        container = ctk.CTkFrame(self.tab_cadastro, fg_color="transparent")
        container.pack(fill="both", expand=True)

        # --- ESQUERDA: FORMULÁRIO ---
        form_frame = ctk.CTkFrame(container, border_width=1, border_color="#444")
        form_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)
        
        ctk.CTkLabel(form_frame, text="Dados do Produto", font=("Arial", 16, "bold"), text_color="#2CC985").grid(row=0, column=0, columnspan=2, pady=15, padx=15, sticky="w")

        # Linha 1: Código e Unidade (Sem Metro)
        self.criar_label_input(form_frame, "Código (Barras/Interno):", 1, 0)
        self.ent_cod = ctk.CTkEntry(form_frame, placeholder_text="Ex: 1001")
        self.ent_cod.grid(row=2, column=0, padx=15, pady=(0, 10), sticky="ew")

        self.criar_label_input(form_frame, "Unidade:", 1, 1)
        self.combo_un = ctk.CTkComboBox(form_frame, values=["UN", "KG", "L", "PCT", "CX"], width=100)
        self.combo_un.grid(row=2, column=1, padx=15, pady=(0, 10), sticky="w")

        # Linha 2: Nome
        self.criar_label_input(form_frame, "Nome do Produto:", 3, 0)
        self.ent_nome = ctk.CTkEntry(form_frame, placeholder_text="Ex: Farinha de Trigo Especial")
        self.ent_nome.grid(row=4, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="ew")

        # Linha 3: Categoria e Tipo
        self.criar_label_input(form_frame, "Categoria:", 5, 0)
        self.combo_cat = ctk.CTkComboBox(form_frame, values=["Panificação", "Confeitaria", "Bebidas", "Frios", "Insumos", "Embalagens", "Outros"])
        self.combo_cat.grid(row=6, column=0, padx=15, pady=(0, 10), sticky="ew")

        self.criar_label_input(form_frame, "Tipo:", 5, 1)
        self.combo_tipo = ctk.CTkComboBox(form_frame, values=["VENDA (Produto Final)", "INSUMO (Matéria Prima)", "AMBOS"])
        self.combo_tipo.grid(row=6, column=1, padx=15, pady=(0, 10), sticky="ew")

        # Linha 4: Preço e Estoque Mínimo
        self.criar_label_input(form_frame, "Preço Venda (R$):", 7, 0)
        self.ent_preco = ctk.CTkEntry(form_frame, placeholder_text="0.00")
        self.ent_preco.grid(row=8, column=0, padx=15, pady=(0, 10), sticky="ew")

        self.criar_label_input(form_frame, "Estoque Mínimo:", 7, 1)
        self.ent_minimo = ctk.CTkEntry(form_frame, placeholder_text="Ex: 10")
        self.ent_minimo.grid(row=8, column=1, padx=15, pady=(0, 10), sticky="ew")

        # --- CORREÇÃO DO SWITCH (Removido on_value/off_value) ---
        self.switch_controla = ctk.CTkSwitch(form_frame, text="Controlar Estoque deste item")
        self.switch_controla.select()
        self.switch_controla.grid(row=9, column=0, columnspan=2, padx=15, pady=20, sticky="w")

        ctk.CTkButton(form_frame, text="💾 SALVAR / ATUALIZAR", fg_color="#27AE60", height=45, font=("Arial", 14, "bold"),
                      command=self.salvar_cadastro).grid(row=10, column=0, columnspan=2, padx=15, pady=10, sticky="ew")

        form_frame.grid_columnconfigure(0, weight=2)
        form_frame.grid_columnconfigure(1, weight=1)

        # --- DIREITA: LISTA RÁPIDA (Fundo Dark) ---
        list_frame = ctk.CTkFrame(container, width=300)
        list_frame.pack(side="right", fill="y", pady=10)
        
        ctk.CTkLabel(list_frame, text="Produtos Cadastrados", font=("Arial", 14, "bold")).pack(pady=10)
        
        self.tree_resumo = ttk.Treeview(list_frame, columns=("cod", "nome"), show="headings")
        self.tree_resumo.heading("cod", text="ID"); self.tree_resumo.column("cod", width=50, anchor="center")
        self.tree_resumo.heading("nome", text="Nome"); self.tree_resumo.column("nome", width=200)
        
        scroll = ctk.CTkScrollbar(list_frame, command=self.tree_resumo.yview)
        self.tree_resumo.configure(yscroll=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree_resumo.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.tree_resumo.bind("<<TreeviewSelect>>", self.carregar_para_edicao)

    def criar_label_input(self, parent, texto, r, c):
        ctk.CTkLabel(parent, text=texto, text_color="#ccc").grid(row=r, column=c, sticky="w", padx=15, pady=(5,0))

    def montar_aba_movimentacao(self):
        center = ctk.CTkFrame(self.tab_mov, fg_color="transparent")
        center.pack(fill="both", expand=True, padx=50, pady=20)

        ctk.CTkLabel(center, text="REGISTRO DE ENTRADA E SAÍDA", font=("Arial", 18, "bold")).pack(pady=10)

        ctk.CTkLabel(center, text="1. Selecione o Produto:", font=("Arial", 14)).pack(anchor="w")
        self.combo_mov_prod = ctk.CTkComboBox(center, height=40, font=("Arial", 14), values=self.listar_nomes_produtos())
        self.combo_mov_prod.pack(fill="x", pady=5)

        self.tipo_mov_var = ctk.StringVar(value="ENTRADA")
        radio_frame = ctk.CTkFrame(center)
        radio_frame.pack(fill="x", pady=15)
        
        ctk.CTkRadioButton(radio_frame, text="🔼 ENTRADA", variable=self.tipo_mov_var, value="ENTRADA", fg_color="#27AE60").pack(side="left", padx=20, pady=10)
        ctk.CTkRadioButton(radio_frame, text="🔽 SAÍDA", variable=self.tipo_mov_var, value="SAIDA", fg_color="#E67E22").pack(side="left", padx=20, pady=10)
        ctk.CTkRadioButton(radio_frame, text="🗑️ PERDA", variable=self.tipo_mov_var, value="PERDA", fg_color="#C0392B").pack(side="left", padx=20, pady=10)

        detalhes_frame = ctk.CTkFrame(center, fg_color="transparent")
        detalhes_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(detalhes_frame, text="Quantidade:").pack(side="left", padx=(0,10))
        self.ent_mov_qtd = ctk.CTkEntry(detalhes_frame, width=120)
        self.ent_mov_qtd.pack(side="left")

        ctk.CTkLabel(detalhes_frame, text="Motivo:").pack(side="left", padx=(20,10))
        self.ent_mov_motivo = ctk.CTkEntry(detalhes_frame)
        self.ent_mov_motivo.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(center, text="✅ CONFIRMAR", height=50, fg_color="#2980B9", command=self.realizar_movimento).pack(pady=30, fill="x")

    def montar_aba_lista(self):
        filter_frame = ctk.CTkFrame(self.tab_lista)
        filter_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(filter_frame, text="🔄 Atualizar", width=120, command=self.atualizar_tabelas).pack(side="right")

        cols = ("cod", "nome", "cat", "tipo", "un", "min", "est")
        self.tree_full = ttk.Treeview(self.tab_lista, columns=cols, show="headings")
        
        for col in cols: self.tree_full.heading(col, text=col.upper())
        self.tree_full.column("nome", width=250)
        self.tree_full.pack(fill="both", expand=True, padx=10, pady=10)

    def salvar_cadastro(self):
        dados = {
            "id": self.ent_cod.get().strip(),
            "nome": self.ent_nome.get().strip(),
            "categoria": self.combo_cat.get(),
            "tipo": self.combo_tipo.get(),
            "unidade": self.combo_un.get(),
            "preco": self.ent_preco.get().replace(",", ".") or "0",
            "minimo": self.ent_minimo.get().replace(",", ".") or "0",
            "controla_estoque": bool(self.switch_controla.get()),
            "estoque": 0 
        }

        if not dados["id"] or not dados["nome"]:
            messagebox.showwarning("Erro", "Campos obrigatórios vazios")
            return

        if self.controller.salvar_produto(dados):
            messagebox.showinfo("Sucesso", "Produto Salvo!")
            self.limpar_form_cadastro()
            self.atualizar_tabelas()

    def realizar_movimento(self):
        nome = self.combo_mov_prod.get()
        qtd = self.ent_mov_qtd.get().replace(",", ".")
        motivo = self.ent_mov_motivo.get()
        tipo = self.tipo_mov_var.get()

        for cod, d in self.produtos.items():
            if d['nome'] == nome:
                ok, msg = self.controller.movimentar_estoque(cod, qtd, tipo, motivo, "Admin")
                if ok:
                    messagebox.showinfo("Sucesso", msg)
                    self.atualizar_tabelas()
                else:
                    messagebox.showerror("Erro", msg)
                return

    def atualizar_tabelas(self):
        self.produtos = database.carregar_produtos()
        for tree in [self.tree_resumo, self.tree_full]:
            for i in tree.get_children(): tree.delete(i)
        
        nomes = []
        for cod, p in self.produtos.items():
            nomes.append(p['nome'])
            self.tree_resumo.insert("", "end", values=(cod, p['nome']))
            self.tree_full.insert("", "end", values=(cod, p['nome'], p.get('categoria','-'), p.get('tipo','-'), p.get('unidade','-'), p.get('estoque_minimo',0), p.get('estoque',0)))
        
        self.combo_mov_prod.configure(values=sorted(nomes))

    def listar_nomes_produtos(self):
        return sorted([p['nome'] for p in self.produtos.values()])

    def limpar_form_cadastro(self):
        for entry in [self.ent_cod, self.ent_nome, self.ent_preco, self.ent_minimo]:
            entry.delete(0, "end")

    def carregar_para_edicao(self, event):
        sel = self.tree_resumo.selection()
        if not sel: return
        cod = self.tree_resumo.item(sel[0], "values")[0]
        p = self.produtos[cod]
        self.limpar_form_cadastro()
        self.ent_cod.insert(0, cod)
        self.ent_nome.insert(0, p['nome'])
        self.ent_preco.insert(0, p.get('preco', 0))
        self.ent_minimo.insert(0, p.get('estoque_minimo', 0))
        self.combo_un.set(p.get('unidade', 'UN'))