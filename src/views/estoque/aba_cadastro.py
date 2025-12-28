# src/views/estoque/aba_cadastro.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from src.utils.componentes_estilizados import CTkFloatingDropdown
from src.utils.textos_ajuda import abrir_ajuda

class AbaCadastro(ctk.CTkFrame):
    def __init__(self, master, controller, callback_atualizar):
        super().__init__(master)
        self.controller = controller
        self.atualizar_sistema = callback_atualizar
        self.produtos = {} 
        self.lista_categorias = ["Panificação", "Confeitaria", "Bebidas", "Frios", "Insumos", "Embalagens", "Outros", "Laticínios", "Hortifruti"]

        self.montar_layout()

    def montar_layout(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        container.columnconfigure(0, weight=3)
        container.columnconfigure(1, weight=2)
        container.rowconfigure(0, weight=1)

        # ESQUERDA: FORMULÁRIO
        form = ctk.CTkFrame(container, border_width=1, border_color="#444")
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        title_frame = ctk.CTkFrame(form, fg_color="transparent")
        title_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=15, pady=15)
        ctk.CTkLabel(title_frame, text="Dados do Item", font=("Arial", 16, "bold"), text_color="#2CC985").pack(side="left")
        ctk.CTkButton(title_frame, text="?", width=25, height=25, fg_color="#2980B9", hover_color="#1F618D",
                      command=self.mostrar_ajuda).pack(side="left", padx=10)

        ctk.CTkLabel(form, text="Tipo do Item:", text_color="#ccc").grid(row=1, column=0, columnspan=2, sticky="w", padx=15)
        self.tipo_var = ctk.StringVar(value="PRODUTO")
        radio_frame = ctk.CTkFrame(form, fg_color="transparent")
        radio_frame.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 15))
        ctk.CTkRadioButton(radio_frame, text="🍞 PRODUTO (Venda)", variable=self.tipo_var, value="PRODUTO", fg_color="#2980B9").pack(side="left", padx=5)
        ctk.CTkRadioButton(radio_frame, text="📦 INSUMO (Matéria)", variable=self.tipo_var, value="INSUMO", fg_color="#E67E22").pack(side="left", padx=15)

        self.criar_input(form, "Código:", 3, 0)
        self.ent_cod = ctk.CTkEntry(form, placeholder_text="Ex: 1001")
        self.ent_cod.grid(row=4, column=0, padx=15, pady=(0, 10), sticky="ew")

        self.criar_input(form, "Unidade:", 3, 1)
        self.combo_un = ctk.CTkComboBox(form, values=["UN", "KG", "L", "PCT", "CX", "G", "ML"])
        self.combo_un.grid(row=4, column=1, padx=15, pady=(0, 10), sticky="ew")

        self.criar_input(form, "Nome:", 5, 0)
        self.ent_nome = ctk.CTkEntry(form, placeholder_text="Ex: Farinha de Trigo")
        self.ent_nome.grid(row=6, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="ew")

        self.criar_input(form, "Categoria:", 7, 0)
        self.ent_cat = ctk.CTkEntry(form, placeholder_text="Selecione ou Digite...")
        self.ent_cat.grid(row=8, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="ew")
        self.dropdown_cat = CTkFloatingDropdown(self.ent_cat, self.lista_categorias, width=400)

        self.criar_input(form, "Custo (R$):", 9, 0)
        self.ent_custo = ctk.CTkEntry(form, placeholder_text="0.00")
        self.ent_custo.grid(row=10, column=0, padx=15, pady=(0, 10), sticky="ew")

        self.criar_input(form, "Venda (R$):", 9, 1)
        self.ent_preco = ctk.CTkEntry(form, placeholder_text="0.00")
        self.ent_preco.grid(row=10, column=1, padx=15, pady=(0, 10), sticky="ew")

        self.criar_input(form, "Estoque Mínimo:", 11, 0)
        self.ent_minimo = ctk.CTkEntry(form, placeholder_text="Ex: 10")
        self.ent_minimo.grid(row=12, column=0, padx=15, pady=(0, 10), sticky="ew")

        self.switch_controla = ctk.CTkSwitch(form, text="Controlar Estoque")
        self.switch_controla.select()
        self.switch_controla.grid(row=12, column=1, padx=15, pady=(20, 10), sticky="w")

        ctk.CTkButton(form, text="💾 SALVAR ITEM", fg_color="#27AE60", height=50, font=("Arial", 14, "bold"),
                      command=self.salvar).grid(row=14, column=0, columnspan=2, padx=15, pady=20, sticky="ew")

        # DIREITA: LISTA
        list_frame = ctk.CTkFrame(container, fg_color="transparent")
        list_frame.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(list_frame, text="Itens Cadastrados", font=("Arial", 14, "bold")).pack(pady=(15, 10))
        
        tree_container = ctk.CTkFrame(list_frame, fg_color="transparent")
        tree_container.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(tree_container, columns=("cod", "tipo", "nome"), show="headings")
        self.tree.heading("cod", text="ID"); self.tree.column("cod", width=50, anchor="center")
        self.tree.heading("tipo", text="Tipo"); self.tree.column("tipo", width=70, anchor="center")
        self.tree.heading("nome", text="Nome"); self.tree.column("nome", width=200)
        
        scroll = ctk.CTkScrollbar(tree_container, command=self.tree.yview)
        self.tree.configure(yscroll=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.carregar_edicao)

    def criar_input(self, p, t, r, c):
        ctk.CTkLabel(p, text=t, text_color="#ccc").grid(row=r, column=c, sticky="w", padx=15, pady=(5,0))

    def mostrar_ajuda(self):
        abrir_ajuda(self, "cadastro")

    def salvar(self):
        dados = {
            "id": self.ent_cod.get().strip(), "nome": self.ent_nome.get().strip(),
            "categoria": self.ent_cat.get(), "unidade": self.combo_un.get(),
            "tipo": self.tipo_var.get(), "custo": self.ent_custo.get().replace(",", ".") or "0",
            "preco": self.ent_preco.get().replace(",", ".") or "0",
            "minimo": self.ent_minimo.get().replace(",", ".") or "0",
            "controla_estoque": bool(self.switch_controla.get())
        }
        if not dados["id"] or not dados["nome"]:
            messagebox.showwarning("Erro", "Campos obrigatórios vazios")
            return
        if self.controller.salvar_produto(dados):
            messagebox.showinfo("Sucesso", "Item Salvo!")
            self.limpar_form()
            self.atualizar_sistema()

    def limpar_form(self):
        for e in [self.ent_cod, self.ent_nome, self.ent_preco, self.ent_custo, self.ent_minimo, self.ent_cat]: 
            e.delete(0, "end")
        self.tipo_var.set("PRODUTO")
        self.dropdown_cat.fechar_lista()

    def atualizar_lista(self, produtos_dict):
        self.produtos = produtos_dict
        for i in self.tree.get_children(): self.tree.delete(i)
        for cod, p in produtos_dict.items():
            tipo_display = "📦 INS" if p.get('tipo') == "INSUMO" else "🍞 PROD"
            self.tree.insert("", "end", values=(cod, tipo_display, p['nome']))

    def carregar_edicao(self, event):
        sel = self.tree.selection()
        if not sel: return
        cod = self.tree.item(sel[0], "values")[0]
        p = self.produtos.get(cod)
        if p:
            self.limpar_form()
            self.ent_cod.insert(0, cod); self.ent_nome.insert(0, p['nome'])
            self.ent_preco.insert(0, p.get('preco', 0)); self.ent_custo.insert(0, p.get('custo', 0))
            self.ent_minimo.insert(0, p.get('estoque_minimo', 0)); self.combo_un.set(p.get('unidade', 'UN'))
            self.ent_cat.insert(0, p.get('categoria', 'Outros')); self.tipo_var.set(p.get('tipo', 'PRODUTO'))
            if p.get('controla_estoque', True): self.switch_controla.select()
            else: self.switch_controla.deselect()