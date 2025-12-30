# view_login.py
import customtkinter as ctk

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, callback_login):
        super().__init__(master)
        self.callback_login = callback_login # Função para chamar quando logar

        self.place(relx=0.5, rely=0.5, anchor="center")
        self.configure(fg_color="transparent")

        # Card de Login
        self.card = ctk.CTkFrame(self, width=320, height=360, corner_radius=20)
        self.card.pack()

        ctk.CTkLabel(self.card, text="SISTEMA PADARIA", font=("Arial", 22, "bold")).pack(pady=(40, 20))

        self.entry_user = ctk.CTkEntry(self.card, placeholder_text="Usuário", width=250, height=40)
        self.entry_user.pack(pady=10)

        self.entry_pass = ctk.CTkEntry(self.card, placeholder_text="Senha", width=250, height=40, show="*")
        self.entry_pass.pack(pady=10)

        self.btn_entrar = ctk.CTkButton(self.card, text="ENTRAR", width=250, height=40,
                                        command=self.tentar_login)
        self.btn_entrar.pack(pady=30)
        
        self.lbl_erro = ctk.CTkLabel(self.card, text="", text_color="red")
        self.lbl_erro.pack()

    def tentar_login(self):
        user = self.entry_user.get()
        senha = self.entry_pass.get()
        self.callback_login(user, senha, self.lbl_erro)