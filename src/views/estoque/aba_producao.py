# src/views/estoque/aba_producao.py
import customtkinter as ctk
from tkinter import ttk, messagebox

class AbaProducao(ctk.CTkFrame):
    def __init__(self, master, controller, produtos_ref, callback_atualizar):
        super().__init__(master)
        self.controller = controller
        self.produtos = produtos_ref
        self.callback_atualizar = callback_atualizar
        self.receitas_cache = {}
        
        self.montar_layout()

    def montar_layout(self):
        # Layout de 2 colunas
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # --- ESQUERDA: LISTA DE O QUE PRODUZIR ---
        frame_esq = ctk.CTkFrame(self, fg_color="#2b2b2b")
        frame_esq.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(frame_esq, text="1. O que foi produzido?", font=("Arial", 16, "bold"), text_color="#2CC985").pack(pady=15)
        ctk.CTkLabel(frame_esq, text="(Mostrando apenas produtos com Ficha Técnica)", font=("Arial", 10), text_color="gray").pack()

        self.tree_prod = ttk.Treeview(frame_esq, columns=("nome",), show="headings")
        self.tree_prod.heading("nome", text="Produtos Prontos para Produção")
        self.tree_prod.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tree_prod.bind("<<TreeviewSelect>>", self.selecionar_produto)

        # --- DIREITA: DETALHES E AÇÃO ---
        frame_dir = ctk.CTkFrame(self)
        frame_dir.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.lbl_titulo = ctk.CTkLabel(frame_dir, text="Selecione um produto...", font=("Arial", 20, "bold"))
        self.lbl_titulo.pack(pady=(40, 20))

        self.lbl_info = ctk.CTkLabel(frame_dir, text="", font=("Arial", 12))
        self.lbl_info.pack(pady=5)

        # Campo de Quantidade
        self.frame_qtd = ctk.CTkFrame(frame_dir, fg_color="transparent")
        self.frame_qtd.pack(pady=30)
        
        ctk.CTkLabel(self.frame_qtd, text="Quantidade Produzida:").pack()
        self.ent_qtd = ctk.CTkEntry(self.frame_qtd, width=150, font=("Arial", 24), justify="center")
        self.ent_qtd.pack(pady=10)
        self.ent_qtd.bind("<Return>", lambda e: self.confirmar_producao())
        
        self.btn_produzir = ctk.CTkButton(frame_dir, text="🏭 REGISTRAR PRODUÇÃO", height=60, fg_color="#E67E22",
                                          state="disabled", command=self.confirmar_producao)
        self.btn_produzir.pack(pady=20, padx=40, fill="x")

        # Aviso
        ctk.CTkLabel(frame_dir, text="⚠️ Isso irá baixar os insumos do estoque automaticamente.", 
                     text_color="#E74C3C", font=("Arial", 11)).pack(side="bottom", pady=20)

    def atualizar(self):
        # Recarrega receitas disponíveis
        self.tree_prod.delete(*self.tree_prod.get_children())
        self.receitas_cache = self.controller.carregar_receitas()
        
        for id_prod, receita in self.receitas_cache.items():
            nome = receita.get('nome', '???')
            self.tree_prod.insert("", "end", values=(nome,), tags=(id_prod,))

    def selecionar_produto(self, event):
        sel = self.tree_prod.selection()
        if not sel: return
        
        item = self.tree_prod.item(sel[0])
        id_prod = item['tags'][0]
        nome = item['values'][0]
        
        self.id_selecionado = id_prod
        self.lbl_titulo.configure(text=nome)
        
        # Mostra resumo da receita
        receita = self.receitas_cache.get(id_prod, {})
        qtd_ing = len(receita.get('ingredientes', []))
        rend = receita.get('rendimento', 1)
        
        self.lbl_info.configure(text=f"Receita Base: Rende {rend} un | Usa {qtd_ing} insumos")
        
        self.btn_produzir.configure(state="normal")
        self.ent_qtd.focus_set()

    def confirmar_producao(self):
        if not hasattr(self, 'id_selecionado'): return
        
        qtd_str = self.ent_qtd.get().replace(",", ".")
        try:
            qtd = float(qtd_str)
            if qtd <= 0: raise ValueError
        except:
            messagebox.showerror("Erro", "Digite uma quantidade válida.")
            return

        # Confirmação visual
        nome = self.lbl_titulo.cget("text")
        if not messagebox.askyesno("Confirmar", f"Confirma a produção de {qtd} {nome}?\n\nOs estoques de farinha/insumos serão descontados."):
            return

        # Chama o controller
        ok, msg = self.controller.registrar_producao(self.id_selecionado, qtd, "Admin")
        
        if ok:
            messagebox.showinfo("Sucesso", msg)
            self.ent_qtd.delete(0, "end")
            self.callback_atualizar() # Atualiza estoques na tela
        else:
            messagebox.showerror("Erro", msg)