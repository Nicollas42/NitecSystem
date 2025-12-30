# src/views/estoque/aba_producao.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from src.utils.textos_ajuda import abrir_ajuda
from src.utils.formata_numeros_br import formata_numeros_br

class AbaProducao(ctk.CTkFrame):
    def __init__(self, master, controller, produtos_ref, callback_atualizar):
        super().__init__(master)
        self.controller = controller
        self.produtos = produtos_ref
        self.callback_atualizar = callback_atualizar
        self.receitas_cache = {}
        self.id_selecionado = None 
        
        self.montar_layout()

    def montar_layout(self):
        self.columnconfigure(0, weight=1); self.columnconfigure(1, weight=1); self.rowconfigure(0, weight=1)

        # ESQUERDA: O QUE PRODUZIR
        frame_esq = ctk.CTkFrame(self, fg_color="#2b2b2b")
        frame_esq.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        header_esq = ctk.CTkFrame(frame_esq, fg_color="transparent")
        header_esq.pack(fill="x", pady=15)
        ctk.CTkLabel(header_esq, text="1. O que será produzido?", font=("Arial", 16, "bold"), text_color="#2CC985").pack(side="left", padx=(10, 5))
        ctk.CTkButton(header_esq, text="?", width=25, height=25, fg_color="#2980B9", command=self.mostrar_ajuda).pack(side="left")
        
        self.tree_prod = ttk.Treeview(frame_esq, columns=("nome",), show="headings")
        self.tree_prod.heading("nome", text="Produtos com Ficha Técnica")
        self.tree_prod.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree_prod.bind("<<TreeviewSelect>>", self.selecionar_produto)

        # DIREITA: DETALHES
        frame_dir = ctk.CTkFrame(self)
        frame_dir.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.lbl_titulo = ctk.CTkLabel(frame_dir, text="Selecione um produto...", font=("Arial", 20, "bold"))
        self.lbl_titulo.pack(pady=(20, 10))

        self.lbl_subtitulo = ctk.CTkLabel(frame_dir, text="", font=("Arial", 12, "bold"), text_color="#aaa")
        self.lbl_subtitulo.pack(pady=(0, 5))

        self.scroll_ingredientes = ctk.CTkScrollableFrame(frame_dir, height=150, fg_color="#333", border_width=1, border_color="#444")
        self.scroll_ingredientes.pack(fill="x", padx=40, pady=5)

        self.frame_qtd = ctk.CTkFrame(frame_dir, fg_color="transparent")
        self.frame_qtd.pack(pady=20)
        ctk.CTkLabel(self.frame_qtd, text="Quantidade Produzida Hoje:").pack(pady=(0, 5))
        
        f_input_row = ctk.CTkFrame(self.frame_qtd, fg_color="transparent")
        f_input_row.pack()
        self.ent_qtd = ctk.CTkEntry(f_input_row, width=150, font=("Arial", 24), justify="center")
        self.ent_qtd.pack(side="left", padx=5)
        self.lbl_unidade_input = ctk.CTkLabel(f_input_row, text="UN", font=("Arial", 18, "bold"), text_color="#aaa")
        self.lbl_unidade_input.pack(side="left", padx=5)
        
        self.btn_produzir = ctk.CTkButton(frame_dir, text="🏭 REGISTRAR PRODUÇÃO", height=60, fg_color="#E67E22",
                                          state="disabled", command=self.confirmar_producao)
        self.btn_produzir.pack(pady=20, padx=40, fill="x")

    def mostrar_ajuda(self):
        abrir_ajuda(self, "producao")

    def atualizar(self):
        self.tree_prod.delete(*self.tree_prod.get_children())
        self.receitas_cache = self.controller.carregar_receitas()
        for id_prod, receita in self.receitas_cache.items():
            self.tree_prod.insert("", "end", values=(receita.get('nome', '???'),), tags=(str(id_prod),))

    def selecionar_produto(self, event):
        sel = self.tree_prod.selection()
        if not sel: return
        id_prod = str(self.tree_prod.item(sel[0])['tags'][0])
        receita = self.receitas_cache.get(id_prod)
        if receita:
            unidade_prod = self.produtos.get(id_prod, {}).get('unidade', 'UN')
            self.id_selecionado = id_prod
            self.lbl_titulo.configure(text=receita['nome'])
            
            # Formatação do rendimento da receita
            rendimento_fmt = formata_numeros_br(receita.get('rendimento', 1), moeda=False)
            
            self.lbl_subtitulo.configure(text=f"Receita Base para: {rendimento_fmt} {unidade_prod}")
            self.lbl_unidade_input.configure(text=unidade_prod)
            self.btn_produzir.configure(state="normal")
            self.renderizar_ingredientes(receita.get('ingredientes', []))

    def renderizar_ingredientes(self, ingredientes):
        for w in self.scroll_ingredientes.winfo_children(): w.destroy()
        
        if not ingredientes:
            ctk.CTkLabel(self.scroll_ingredientes, text="Nenhum ingrediente cadastrado.", text_color="gray").pack()
            return

        for ing in ingredientes:
            id_ing = str(ing.get('id'))
            
            # 1. Tenta buscar dados completos no banco de produtos
            produto_db = self.produtos.get(id_ing, {})
            
            # 2. Define a unidade (Prioridade: Banco -> Receita -> Padrão)
            un = produto_db.get('unidade') or ing.get('un') or 'UN'
            
            # 3. Define o nome (Prioridade: Receita -> Banco -> Erro)
            # Isso corrige o "Nome Indisponível"
            nome_ing = ing.get('nome')
            if not nome_ing:
                nome_ing = produto_db.get('nome', f"Item {id_ing} (Não encontrado)")

            # Formatação da quantidade
            try:
                qtd_val = float(ing.get('qtd', 0))
                qtd_ing_fmt = formata_numeros_br(qtd_val, moeda=False)
            except:
                qtd_ing_fmt = "0"
            
            ctk.CTkLabel(self.scroll_ingredientes, text=f"• {qtd_ing_fmt} {un} - {nome_ing}", anchor="w").pack(fill="x", padx=5)

    def confirmar_producao(self):
        qtd = self.ent_qtd.get().replace(",", ".")
        if not qtd or float(qtd) <= 0: return
        
        msg = f"Confirma a produção de {qtd} {self.lbl_unidade_input.cget('text')} de {self.lbl_titulo.cget('text')}?"
        if messagebox.askyesno("Confirmar", msg):
            ok, resp = self.controller.registrar_producao(self.id_selecionado, qtd, "Admin")
            if ok:
                messagebox.showinfo("Sucesso", resp); self.callback_atualizar()
            else:
                messagebox.showerror("Erro", resp)