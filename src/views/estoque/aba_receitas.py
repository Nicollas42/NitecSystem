# src/views/estoque/aba_receitas.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from src.utils.componentes_estilizados import CTkFloatingDropdown
from src.utils.textos_ajuda import abrir_ajuda

class AbaReceitas(ctk.CTkFrame):
    def __init__(self, master, controller, produtos_ref, callback_atualizar):
        super().__init__(master)
        self.controller = controller
        self.produtos = produtos_ref
        self.callback_atualizar = callback_atualizar
        self.ingredientes_temp = [] 
        self.id_produto_atual = None
        self.lista_insumos_nomes = []
        
        self.montar_layout()

    def montar_layout(self):
        self.columnconfigure(0, weight=1); self.columnconfigure(1, weight=2); self.rowconfigure(0, weight=1)

        # ESQUERDA: LISTA
        frame_esq = ctk.CTkFrame(self, fg_color="#2b2b2b")
        frame_esq.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        header_esq = ctk.CTkFrame(frame_esq, fg_color="transparent")
        header_esq.pack(fill="x", pady=10)
        ctk.CTkLabel(header_esq, text="1. Escolha o Produto Final", font=("Arial", 14, "bold"), text_color="#2CC985").pack(side="left", padx=(10, 5))
        ctk.CTkButton(header_esq, text="?", width=25, height=25, fg_color="#2980B9", command=self.mostrar_ajuda).pack(side="left")
        
        self.lista_produtos = ttk.Treeview(frame_esq, columns=("nome",), show="headings")
        self.lista_produtos.heading("nome", text="Produtos (Venda)")
        self.lista_produtos.pack(fill="both", expand=True, padx=10, pady=10)
        self.lista_produtos.bind("<<TreeviewSelect>>", self.carregar_receita_existente)

        # DIREITA: EDITOR
        frame_dir = ctk.CTkFrame(self)
        frame_dir.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        f_head = ctk.CTkFrame(frame_dir, fg_color="transparent")
        f_head.pack(fill="x", padx=10, pady=10)
        self.lbl_produto_selecionado = ctk.CTkLabel(f_head, text="Nenhum Produto Selecionado", font=("Arial", 18, "bold"))
        self.lbl_produto_selecionado.pack(anchor="w")

        f_rend = ctk.CTkFrame(f_head, fg_color="transparent")
        f_rend.pack(fill="x", pady=5)
        ctk.CTkLabel(f_rend, text="Rendimento desta Receita:").pack(side="left")
        self.ent_rendimento = ctk.CTkEntry(f_rend, width=80); self.ent_rendimento.pack(side="left", padx=10)
        self.lbl_unidade_rend = ctk.CTkLabel(f_rend, text="UN"); self.lbl_unidade_rend.pack(side="left")

        f_add = ctk.CTkFrame(frame_dir, border_width=1, border_color="#444")
        f_add.pack(fill="x", padx=10, pady=10)
        self.ent_insumo = ctk.CTkEntry(f_add, width=250, placeholder_text="Digite o insumo...")
        self.ent_insumo.pack(side="left", padx=10, pady=10)
        self.dropdown_insumos = CTkFloatingDropdown(self.ent_insumo, [], width=350, command=self.verificar_unidade)
        self.ent_qtd_ing = ctk.CTkEntry(f_add, width=80); self.ent_qtd_ing.pack(side="left", padx=5)
        self.lbl_un_ing = ctk.CTkLabel(f_add, text="UN"); self.lbl_un_ing.pack(side="left", padx=5)
        ctk.CTkButton(f_add, text="Adicionar (+)", fg_color="#27AE60", command=self.adicionar_ingrediente).pack(side="left", padx=10)

        f_list_container = ctk.CTkFrame(frame_dir, fg_color="transparent")
        f_list_container.pack(fill="both", expand=True, padx=10)
        self.scroll_ing = ctk.CTkScrollableFrame(f_list_container, fg_color="transparent")
        self.scroll_ing.pack(fill="both", expand=True)

        f_footer = ctk.CTkFrame(frame_dir, height=60, fg_color="#333")
        f_footer.pack(fill="x", side="bottom")
        self.lbl_custo_total = ctk.CTkLabel(f_footer, text="Custo Total: R$ 0.00", font=("Arial", 14, "bold"))
        self.lbl_custo_total.pack(side="left", padx=20, pady=15)
        ctk.CTkButton(f_footer, text="💾 SALVAR", fg_color="#2980B9", command=self.salvar_receita).pack(side="right", padx=10)

    def mostrar_ajuda(self):
        abrir_ajuda(self, "receitas")

    def atualizar(self):
        self.lista_produtos.delete(*self.lista_produtos.get_children())
        self.lista_insumos_nomes = [p['nome'] for p in self.produtos.values() if p.get('tipo') == 'INSUMO']
        for cod, p in self.produtos.items():
            if p.get('tipo') == 'PRODUTO': self.lista_produtos.insert("", "end", values=(p['nome'],), tags=(cod,))
        self.dropdown_insumos.atualizar_dados(self.lista_insumos_nomes)

    def verificar_unidade(self, item=None):
        nome = item if item else self.ent_insumo.get()
        for p in self.produtos.values():
            if p['nome'] == nome: self.lbl_un_ing.configure(text=p.get('unidade', 'UN')); return

    def carregar_receita_existente(self, event):
        sel = self.lista_produtos.selection()
        if not sel: return
        cod_prod = str(self.lista_produtos.item(sel[0])['tags'][0])
        self.id_produto_atual = cod_prod
        self.lbl_produto_selecionado.configure(text=f"Editando: {self.produtos[cod_prod]['nome']}")
        self.renderizar_ingredientes()

    def adicionar_ingrediente(self):
        nome = self.ent_insumo.get()
        id_insumo = next((k for k, v in self.produtos.items() if v['nome'] == nome), None)
        if id_insumo:
            self.ingredientes_temp.append({"id": id_insumo, "nome": nome, "qtd": self.ent_qtd_ing.get()})
            self.renderizar_ingredientes()

    def renderizar_ingredientes(self):
        for w in self.scroll_ing.winfo_children(): w.destroy()
        for i, ing in enumerate(self.ingredientes_temp):
            ctk.CTkLabel(self.scroll_ing, text=ing['nome']).grid(row=i, column=0, sticky="w")
            ctk.CTkButton(self.scroll_ing, text="🗑️", width=30, command=lambda idx=i: self.remover(idx)).grid(row=i, column=1)

    def remover(self, idx):
        del self.ingredientes_temp[idx]; self.renderizar_ingredientes()

    def salvar_receita(self):
        if self.id_produto_atual:
            self.controller.salvar_receita(self.id_produto_atual, self.ent_rendimento.get(), self.ingredientes_temp)
            messagebox.showinfo("Sucesso", "Ficha salva!"); self.callback_atualizar()