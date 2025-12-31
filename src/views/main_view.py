# src/views/main_view.py
import customtkinter as ctk
from src.views.estoque.estoque_main import EstoqueFrame
from src.views.view_caixa import CaixaFrame
from src.views.view_financeiro import FinanceiroFrame # Assumindo que dashboard é financeiro

class MainApp(ctk.CTkFrame):
    def __init__(self, master, usuario_dados, callback_logout):
        super().__init__(master)
        self.master = master
        self.usuario = usuario_dados
        self.callback_logout = callback_logout
        
        self.montar_menu()

    def montar_menu(self):
        # Limpa tela
        for w in self.winfo_children(): w.destroy()

        # Fundo elegante
        self.configure(fg_color="#1a1a1a")
        
        # Barra lateral
        sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="#222")
        sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(sidebar, text="NITEC SYSTEM", font=("Arial", 24, "bold"), text_color="#2CC985").pack(pady=(40, 20))
        ctk.CTkLabel(sidebar, text=f"Olá, {self.usuario}", font=("Arial", 14), text_color="gray").pack(pady=(0, 40))

        # Botões do Menu
        self.criar_botao_menu(sidebar, "📦 GESTÃO DE ESTOQUE", self.abrir_estoque, "#2980B9")
        self.criar_botao_menu(sidebar, "🛒 CAIXA (PDV)", self.abrir_caixa, "#27AE60")
        self.criar_botao_menu(sidebar, "📊 FINANCEIRO / DASH", self.abrir_financeiro, "#8E44AD")
        
        ctk.CTkButton(sidebar, text="🚪 Sair", fg_color="#C0392B", command=self.callback_logout).pack(side="bottom", pady=20, padx=20, fill="x")

        # Área de Conteúdo (Logo central)
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(side="right", fill="both", expand=True)
        ctk.CTkLabel(content, text="Selecione um módulo ao lado", font=("Arial", 20), text_color="#555").place(relx=0.5, rely=0.5, anchor="center")

    def criar_botao_menu(self, parent, texto, comando, cor):
        ctk.CTkButton(parent, text=texto, height=50, fg_color="transparent", border_width=1, border_color=cor,
                      hover_color=cor, font=("Arial", 14, "bold"), anchor="w", command=comando).pack(fill="x", padx=20, pady=10)

    def abrir_estoque(self):
        self.limpar_conteudo()
        # Passa self.montar_menu como callback para o botão "Voltar" do estoque
        app = EstoqueFrame(self, callback_voltar=self.montar_menu)
        app.pack(fill="both", expand=True)

    def abrir_caixa(self):
        self.limpar_conteudo()
        # Como o Caixa espera um dicionário de usuário, adaptamos se for só string
        user_dict = {"nome": self.usuario} if isinstance(self.usuario, str) else self.usuario
        app = CaixaFrame(self, usuario_dados=user_dict, callback_voltar=self.montar_menu)
        app.pack(fill="both", expand=True)

    def abrir_financeiro(self):
        self.limpar_conteudo()
        user_dict = {"nome": self.usuario} if isinstance(self.usuario, str) else self.usuario
        app = FinanceiroFrame(self, usuario_dados=user_dict, callback_voltar=self.montar_menu)
        app.pack(fill="both", expand=True)

    def limpar_conteudo(self):
        for w in self.winfo_children(): w.destroy()