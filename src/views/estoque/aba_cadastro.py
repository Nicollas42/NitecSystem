import customtkinter as ctk
from tkinter import ttk, messagebox
from src.utils.formata_numeros_br import formata_numeros_br
from .sub_cadastro.forms_cadastro import FormRevenda, FormInsumo, FormInterno

class AbaCadastro(ctk.CTkFrame):
    def __init__(self, master, controller, callback_atualizar):
        super().__init__(master)
        self.controller = controller
        self.atualizar_sistema = callback_atualizar
        self.produtos = {} 
        self.cats = ["Panificação", "Confeitaria", "Bebidas", "Frios", "Insumos", "Embalagens", "Outros", "Laticínios", "Hortifruti"]
        self.expandido = False 
        
        self.montar_layout()

    def montar_layout(self):
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=10, pady=10)
        self.container.columnconfigure(0, weight=3); self.container.columnconfigure(1, weight=5)
        self.container.rowconfigure(0, weight=1)

        # ESQUERDA: FORMULÁRIO
        self.left_frame = ctk.CTkFrame(self.container, border_width=1, border_color="#444")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        ctk.CTkLabel(self.left_frame, text="Cadastro / Edição", font=("Arial", 16, "bold"), text_color="#2CC985").pack(pady=10)

        # Seletor de Tipo
        self.tipo_var = ctk.StringVar(value="PRODUTO")
        f_radios = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        f_radios.pack(fill="x", pady=5)
        
        ctk.CTkRadioButton(f_radios, text="Revenda", variable=self.tipo_var, value="PRODUTO", 
                           command=self.trocar_form).pack(side="left", padx=10)
        ctk.CTkRadioButton(f_radios, text="Interno", variable=self.tipo_var, value="INTERNO", 
                           command=self.trocar_form).pack(side="left", padx=10)
        ctk.CTkRadioButton(f_radios, text="Insumo", variable=self.tipo_var, value="INSUMO", 
                           command=self.trocar_form).pack(side="left", padx=10)

        self.form_container = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.form_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.forms = {
            "PRODUTO": FormRevenda(self.form_container, self.cats),
            "INTERNO": FormInterno(self.form_container, self.cats),
            "INSUMO": FormInsumo(self.form_container, self.cats)
        }
        self.form_atual = self.forms["PRODUTO"]
        self.form_atual.pack(fill="both", expand=True)

        ctk.CTkButton(self.left_frame, text="💾 SALVAR", fg_color="#27AE60", height=45, 
                      command=self.salvar).pack(fill="x", padx=20, pady=20)

        # DIREITA: LISTA
        self.montar_lista(self.container)

    def montar_lista(self, parent):
        self.list_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.list_frame.grid(row=0, column=1, sticky="nsew")
        
        cols = ("cod", "tipo", "nome", "custo", "venda")
        self.tree = ttk.Treeview(self.list_frame, columns=cols, show="headings")
        self.tree.heading("cod", text="ID"); self.tree.column("cod", width=50, anchor="center")
        self.tree.heading("tipo", text="TIPO"); self.tree.column("tipo", width=80, anchor="center")
        self.tree.heading("nome", text="NOME"); self.tree.column("nome", width=200)
        self.tree.heading("custo", text="CUSTO"); self.tree.column("custo", width=80, anchor="center")
        self.tree.heading("venda", text="VENDA"); self.tree.column("venda", width=80, anchor="center")
        
        vsb = ctk.CTkScrollbar(self.list_frame, command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscroll=vsb.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        
        # BIND IMPORTANTE PARA EDIÇÃO
        self.tree.bind("<<TreeviewSelect>>", self.perguntar_edicao)

    def trocar_form(self):
        tipo = self.tipo_var.get()
        self.form_atual.pack_forget()
        self.form_atual = self.forms[tipo]
        self.form_atual.pack(fill="both", expand=True)

    def salvar(self):
        dados = self.form_atual.get_dados()
        if not dados["id"] or not dados["nome"]:
            messagebox.showwarning("Erro", "ID e Nome são obrigatórios")
            return

        sucesso, msg = self.controller.salvar_produto(dados)
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            self.form_atual.limpar_comuns()
            self.atualizar_sistema()
        else:
            messagebox.showerror("Erro", msg)

    def atualizar_lista(self, produtos_dict):
        self.produtos = produtos_dict
        for i in self.tree.get_children(): self.tree.delete(i)
        
        for cod, p in produtos_dict.items():
            t_map = {"PRODUTO": "REV", "INSUMO": "INS", "INTERNO": "FAB"}
            vals = (cod, t_map.get(p.get('tipo', 'PRODUTO'), "?"), p['nome'], 
                    formata_numeros_br(p.get('custo', 0), True),
                    formata_numeros_br(p.get('preco', 0), True))
            self.tree.insert("", "end", values=vals)

    def perguntar_edicao(self, event):
        sel = self.tree.selection()
        if not sel: return
        
        cod = self.tree.item(sel[0], "values")[0]
        p = self.produtos.get(cod)
        if not p: return

        # Troca automaticamente para o formulário correto
        tipo_item = p.get('tipo', 'PRODUTO')
        self.tipo_var.set(tipo_item)
        self.trocar_form()
        
        # Preenche os dados
        self.form_atual.preencher(p)