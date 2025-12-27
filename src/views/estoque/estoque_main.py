import customtkinter as ctk
from tkinter import ttk
from src.controllers.estoque_controller import EstoqueController
from src.models import database

# --- IMPORTAÇÕES ---
from .aba_cadastro import AbaCadastro
from .aba_movimentacao import AbaMovimentacao
from .aba_visao_geral import AbaVisaoGeral
from .aba_historico import AbaHistorico
from .aba_receitas import AbaReceitas
from .aba_producao import AbaProducao # <--- NOVO!

class EstoqueFrame(ctk.CTkFrame):
    def __init__(self, master, callback_voltar):
        super().__init__(master)
        self.voltar_menu = callback_voltar
        self.controller = EstoqueController()
        self.produtos = {}
        
        self.estilizar_tabelas()
        self.montar_layout()
        self.atualizar_tudo()

    def estilizar_tabelas(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", rowheight=30, borderwidth=0)
        style.configure("Treeview.Heading", background="#1f1f1f", foreground="white", font=("Arial", 12, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", "#2CC985")], foreground=[("selected", "black")])

    def montar_layout(self):
        top = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color="#222")
        top.pack(fill="x")
        ctk.CTkButton(top, text="🔙 Voltar", width=100, fg_color="#444", command=self.voltar_menu).pack(side="left", padx=15, pady=10)
        ctk.CTkLabel(top, text="📦 GESTÃO DE ESTOQUE COMPLETA", font=("Arial", 20, "bold")).pack(side="left", padx=10)

        self.tabview = ctk.CTkTabview(self, anchor="nw")
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)

        # --- CRIANDO AS ABAS ---
        tab_cad = self.tabview.add("📝 Cadastro")
        tab_rec = self.tabview.add("👩‍🍳 Ficha Técnica")
        tab_prod = self.tabview.add("🏭 Produção Diária") # <--- NOVO!
        tab_mov = self.tabview.add("🔄 Movimentação")
        tab_list = self.tabview.add("📋 Visão Geral")
        tab_hist = self.tabview.add("📜 Histórico")

        # --- INSTANCIANDO ---
        self.aba_cadastro = AbaCadastro(tab_cad, self.controller, self.atualizar_tudo)
        self.aba_cadastro.pack(fill="both", expand=True)

        self.aba_receitas = AbaReceitas(tab_rec, self.controller, self.produtos, self.atualizar_tudo)
        self.aba_receitas.pack(fill="both", expand=True)

        # Aba de Produção
        self.aba_producao = AbaProducao(tab_prod, self.controller, self.produtos, self.atualizar_tudo) # <--- NOVO!
        self.aba_producao.pack(fill="both", expand=True)

        self.aba_movimentacao = AbaMovimentacao(tab_mov, self.controller, self.atualizar_tudo)
        self.aba_movimentacao.pack(fill="both", expand=True)

        self.aba_visao = AbaVisaoGeral(tab_list, self.atualizar_tudo)
        self.aba_visao.pack(fill="both", expand=True)

        self.aba_historico = AbaHistorico(tab_hist, self.produtos, self.atualizar_tudo)
        self.aba_historico.pack(fill="both", expand=True)

    def atualizar_tudo(self):
        print("🔄 Atualizando Módulos...")
        novos_dados = database.carregar_produtos()
        self.produtos.clear()
        self.produtos.update(novos_dados)
        
        self.aba_cadastro.atualizar_lista(self.produtos)
        self.aba_receitas.atualizar()
        self.aba_producao.atualizar() 
        self.aba_movimentacao.atualizar_produtos(self.produtos)
        self.aba_visao.atualizar(self.produtos)
        self.aba_historico.atualizar()