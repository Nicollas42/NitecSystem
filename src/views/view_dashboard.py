# src/views/view_dashboard.py
import customtkinter as ctk

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, usuario_dados, callback_navegacao, callback_logout):
        super().__init__(master)
        self.usuario = usuario_dados
        self.nav = callback_navegacao
        self.logout = callback_logout

        # Barra Lateral
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="#1a1a1a")
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar, text=f"👤 {self.usuario['nome']}", font=("Arial", 16, "bold")).pack(pady=(30, 5))
        ctk.CTkLabel(self.sidebar, text=self.usuario['role'].upper(), text_color="#2CC985").pack(pady=(0, 30))

        # Controle de Acesso por Role
        isAdmin = self.usuario['role'] == 'admin'

        self.criar_botao("🛒 CAIXA (PDV)", "caixa")
        self.criar_botao("📦 ESTOQUE", "estoque", state="normal" if isAdmin else "disabled")
        self.criar_botao("🗑️ PERDAS / SOBRAS", "sobras", state="normal" if isAdmin else "disabled")
        self.criar_botao("💰 FINANCEIRO", "financeiro", state="normal" if isAdmin else "disabled")

        ctk.CTkButton(self.sidebar, text="SAIR", fg_color="#C0392B", command=self.logout).pack(side="bottom", pady=20, padx=20, fill="x")

        # Painel Central
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.pack(side="right", fill="both", expand=True)
        ctk.CTkLabel(self.main_area, text="Bem-vindo ao NitecSystem", font=("Arial", 24)).place(relx=0.5, rely=0.45, anchor="center")
        ctk.CTkLabel(self.main_area, text="Selecione um módulo à esquerda para começar", text_color="gray").place(relx=0.5, rely=0.52, anchor="center")

    def criar_botao(self, texto, destino, state="normal"):
        btn = ctk.CTkButton(self.sidebar, text=texto, height=45, state=state,
                            fg_color="#333" if state == "normal" else "#1a1a1a",
                            text_color="white" if state == "normal" else "gray",
                            command=lambda: self.nav(destino))
        btn.pack(pady=8, padx=15, fill="x")