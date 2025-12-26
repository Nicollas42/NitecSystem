# main.py (Só as partes alteradas ou arquivo completo para garantir)
import customtkinter as ctk
import config_manager
import database
from view_login import LoginFrame
from view_dashboard import DashboardFrame
from view_caixa import CaixaFrame
from view_estoque import EstoqueFrame
from view_sobras import SobrasFrame
from view_financeiro import FinanceiroFrame

class AppPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.config = config_manager.aplicar_tema_inicial()
        self.title("Sistema Padaria Modular v2.2")
        self.geometry("1200x700")
        
        self.usuario_atual = None
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self.mostrar_login()

    def limpar_tela(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def mostrar_login(self):
        self.limpar_tela()
        self.usuario_atual = None
        LoginFrame(self.container, self.processar_login).pack(fill="both", expand=True)

    def processar_login(self, user, senha, label_erro):
        dados = database.verificar_login(user, senha)
        if dados:
            self.usuario_atual = dados
            self.mostrar_dashboard()
        else:
            label_erro.configure(text="Usuário ou senha incorretos.")

    def mostrar_dashboard(self):
        self.limpar_tela()
        DashboardFrame(self.container, self.usuario_atual, 
                       self.navegar_para_modulo, self.mostrar_login).pack(fill="both", expand=True)

    def navegar_para_modulo(self, modulo):
        if modulo == "caixa":
            self.limpar_tela()
            CaixaFrame(self.container, self.usuario_atual, self.mostrar_dashboard).pack(fill="both", expand=True)
        
        elif modulo == "estoque":
            self.limpar_tela()
            EstoqueFrame(self.container, self.mostrar_dashboard).pack(fill="both", expand=True)
        
        elif modulo == "sobras":
            self.limpar_tela()
            SobrasFrame(self.container, self.usuario_atual, self.mostrar_dashboard).pack(fill="both", expand=True)
        
        elif modulo == "financeiro":
            self.limpar_tela()
            # Este é o comando que realmente abre a tela
            FinanceiroFrame(self.container, self.usuario_atual, self.mostrar_dashboard).pack(fill="both", expand=True)

if __name__ == "__main__":
    app = AppPrincipal()
    app.mainloop()