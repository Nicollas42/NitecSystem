# src/views/view_login.py
import customtkinter as ctk
from tkinter import messagebox
from src.views.main_view import MainApp

class LoginView:
    def __init__(self, root):
        self.root = root
        self.root.title("Nitec System - Login")
        self.root.geometry("400x400")
        self.root.resizable(False, False)
        
        # Centraliza a janela
        try:
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = (screen_width - 400) // 2
            y = (screen_height - 400) // 2
            self.root.geometry(f"400x400+{x}+{y}")
        except: pass

        self.montar_tela()

    def montar_tela(self):
        # Limpa qualquer coisa que esteja na janela (caso seja logout)
        for widget in self.root.winfo_children():
            widget.destroy()

        self.frame = ctk.CTkFrame(self.root)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(self.frame, text="🔐 ACESSO AO SISTEMA", font=("Arial", 20, "bold")).pack(pady=(40, 20))

        self.ent_usuario = ctk.CTkEntry(self.frame, placeholder_text="Usuário", width=250)
        self.ent_usuario.pack(pady=10)
        
        # Usuário padrão para facilitar testes
        self.ent_usuario.insert(0, "Admin")

        self.ent_senha = ctk.CTkEntry(self.frame, placeholder_text="Senha", show="*", width=250)
        self.ent_senha.pack(pady=10)

        ctk.CTkButton(self.frame, text="ENTRAR", width=250, height=40, fg_color="#27AE60",
                      command=self.realizar_login).pack(pady=20)

        ctk.CTkLabel(self.frame, text="v4.1 (Django + PostgreSQL)", text_color="gray", font=("Arial", 10)).pack(side="bottom", pady=10)

    def realizar_login(self):
        usuario = self.ent_usuario.get()
        senha = self.ent_senha.get()

        # Validação simples (futuramente podemos consultar o Django Auth)
        if usuario and senha == "admin":  
            self.abrir_sistema_principal(usuario)
        else:
            messagebox.showerror("Erro", "Senha incorreta! (Tente 'admin')")

    def abrir_sistema_principal(self, nome_usuario):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.geometry("1200x700")
        self.root.title(f"Nitec System - {nome_usuario}")
        self.root.resizable(True, True)
        try: self.root.state("zoomed")
        except: pass

        # Chama o Menu Principal
        app = MainApp(self.root, nome_usuario, self.reiniciar_login)
        app.pack(fill="both", expand=True)

    def reiniciar_login(self):
        # Função chamada pelo botão "Voltar" do EstoqueFrame
        self.__init__(self.root) # Recria a tela de login na mesma janela