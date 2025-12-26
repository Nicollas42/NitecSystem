# view_dashboard.py
import customtkinter as ctk

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, usuario_dados, callback_navegacao, callback_logout):
        super().__init__(master)
        self.usuario = usuario_dados
        self.nav = callback_navegacao
        self.logout = callback_logout

        # Barra Lateral
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar, text=f"Olá, {self.usuario['nome']}", font=("Arial", 18, "bold")).pack(pady=30)
        ctk.CTkLabel(self.sidebar, text=f"Perfil: {self.usuario['role'].upper()}", text_color="gray").pack(pady=(0, 20))

        # --- BOTÕES DO MENU ---
        
        # 1. CAIXA (Todos acessam)
        self.criar_botao("🛒 FRENTE DE CAIXA", "caixa")

        # 2. ESTOQUE (Só Admin)
        state_estoque = "normal" if self.usuario['role'] == 'admin' else "normal"
        self.criar_botao("📦 ESTOQUE / ITENS", "estoque", state=state_estoque)

        # 3. SOBRAS (Só Admin)
        self.criar_botao("🗑️ CONTROLE DE SOBRAS", "sobras", state=state_estoque)

        # 4. FINANCEIRO (Agora Ativo!)
        self.criar_botao("💰 ANÁLISE FINANCEIRA", "financeiro", state="normal")

        # Botão Sair
        ctk.CTkButton(self.sidebar, text="SAIR / LOGOUT", fg_color="#C0392B", 
                      command=self.logout).pack(side="bottom", pady=20, padx=20, fill="x")

        # Área Principal (Boas vindas)
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.pack(side="right", fill="both", expand=True)
        ctk.CTkLabel(self.main_area, text="Selecione uma opção no menu", font=("Arial", 20)).place(relx=0.5, rely=0.5, anchor="center")

    def criar_botao(self, texto, destino, state="normal"):
        btn = ctk.CTkButton(self.sidebar, text=texto, height=50, 
                            state=state,
                            fg_color="transparent" if state == "normal" else "#333",
                            border_width=2,
                            text_color=("gray10", "gray90") if state == "normal" else "gray",
                            command=lambda: self.nav(destino))
        btn.pack(pady=10, padx=20, fill="x")