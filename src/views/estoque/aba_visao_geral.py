import customtkinter as ctk
from tkinter import ttk

class AbaVisaoGeral(ctk.CTkFrame):
    def __init__(self, master, callback_atualizar):
        super().__init__(master)
        self.callback_atualizar = callback_atualizar
        self.montar_layout()

    def montar_layout(self):
        filter_f = ctk.CTkFrame(self)
        filter_f.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(filter_f, text="Raio-X do Estoque", font=("Arial", 14, "bold")).pack(side="left", padx=10)
        ctk.CTkButton(filter_f, text="🔄 Atualizar", width=150, command=self.callback_atualizar).pack(side="right", padx=10)

        cols = ("cod", "nome", "cat", "un", "min", "est_fundo", "est_frente")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        
        titulos = ["ID", "PRODUTO", "CATEGORIA", "UN", "MÍNIMO", "NO FUNDO", "NA FRENTE"]
        for c, t in zip(cols, titulos): self.tree.heading(c, text=t)
        
        self.tree.column("cod", width=60, anchor="center")
        self.tree.column("nome", width=250); self.tree.column("un", width=50, anchor="center")
        self.tree.column("min", width=80, anchor="center")
        self.tree.column("est_fundo", width=100, anchor="center")
        self.tree.column("est_frente", width=100, anchor="center")
        self.tree.column("cat", width=120, anchor="center")

        scroll = ctk.CTkScrollbar(self, command=self.tree.yview)
        self.tree.configure(yscroll=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.tree.tag_configure('baixo_estoque', background='#5c1d1d', foreground='white')
        self.tree.tag_configure('atencao', background='#5c531d', foreground='white')

    def atualizar(self, produtos):
        for i in self.tree.get_children(): self.tree.delete(i)
        
        for cod, p in produtos.items():
            frente, fundo = p.get('estoque_atual', 0), p.get('estoque_fundo', 0)
            minimo = p.get('estoque_minimo', 0)
            
            tag = ''
            if p.get('controla_estoque', True):
                if frente <= minimo and fundo > 0: tag = 'atencao'
                elif frente <= minimo and fundo <= 0: tag = 'baixo_estoque'

            self.tree.insert("", "end", values=(
                cod, p['nome'], p.get('categoria', '-'), p.get('unidade', 'UN'),
                minimo, fundo, frente
            ), tags=(tag,))