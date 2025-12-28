# src/views/main_view.py
import customtkinter as ctk
import src.dev_state as dev_state # <--- Lembre de manter o import corrigido
from src.controllers import config_manager
from src.models import database
from src.views.view_login import LoginFrame
from src.views.view_dashboard import DashboardFrame
from src.views.view_caixa import CaixaFrame
from src.views.estoque.estoque_main import EstoqueFrame
from src.views.view_sobras import SobrasFrame
from src.views.view_financeiro import FinanceiroFrame

class AppPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.config = config_manager.aplicar_tema_inicial()
        self.title("NitecSystem Professional - Padaria")
        self.geometry("1200x700")
        
        self.usuario_atual = None
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        # --- LÓGICA DE DEV (Carregar Estado Anterior) ---
        estado = dev_state.carregar_estado()
        modulo_salvo = estado.get("modulo")

        if modulo_salvo:
            # CORREÇÃO AQUI: Troquei "cargo" por "role" para compatibilidade
            self.usuario_atual = {"id": 1, "nome": "Admin (Dev)", "role": "admin"} 
            print(f"🚀 DEV MODE: Restaurando módulo '{modulo_salvo}'")
            self.navegar_para_modulo(modulo_salvo)
        else:
            self.mostrar_login()
        # ------------------------------------------------

    def limpar_tela(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def mostrar_login(self):
        dev_state.salvar_estado({"modulo": None, "aba_estoque": None})
        self.limpar_tela()
        self.usuario_atual = None
        LoginFrame(self.container, self.processar_login).pack(fill="both", expand=True)

    def processar_login(self, user, senha, label_erro):
        dados = database.verificar_login(user, senha)
        if dados:
            self.usuario_atual = dados
            self.mostrar_dashboard()
        else:
            label_erro.configure(text="Acesso Negado.")

    def mostrar_dashboard(self):
        self.limpar_tela()
        dev_state.salvar_estado({"modulo": "dashboard"}) 
        DashboardFrame(self.container, self.usuario_atual, 
                       self.navegar_para_modulo, self.mostrar_login).pack(fill="both", expand=True)

    def navegar_para_modulo(self, modulo):
        self.limpar_tela()
        dev_state.salvar_estado({"modulo": modulo})

        if modulo == "caixa":
            CaixaFrame(self.container, self.usuario_atual, self.mostrar_dashboard).pack(fill="both", expand=True)
        elif modulo == "estoque":
            EstoqueFrame(self.container, self.mostrar_dashboard).pack(fill="both", expand=True)
        elif modulo == "sobras":
            SobrasFrame(self.container, self.usuario_atual, self.mostrar_dashboard).pack(fill="both", expand=True)
        elif modulo == "financeiro":
            FinanceiroFrame(self.container, self.usuario_atual, self.mostrar_dashboard).pack(fill="both", expand=True)
        elif modulo == "dashboard":
             DashboardFrame(self.container, self.usuario_atual, self.navegar_para_modulo, self.mostrar_login).pack(fill="both", expand=True)

if __name__ == "__main__":
    app = AppPrincipal()
    app.mainloop()