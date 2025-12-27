import customtkinter as ctk
from tkinter import messagebox

class AbaMovimentacao(ctk.CTkFrame):
    def __init__(self, master, controller, callback_atualizar):
        super().__init__(master)
        self.controller = controller
        self.atualizar_sistema = callback_atualizar
        self.lista_nomes = []
        self.produtos_cache = {}

        self.montar_layout()

    def montar_layout(self):
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.pack(fill="both", expand=True, padx=50, pady=20)

        ctk.CTkLabel(center, text="REGISTRO DE MOVIMENTAÇÃO", font=("Arial", 18, "bold")).pack(pady=10)

        ctk.CTkLabel(center, text="1. Selecione o Produto:").pack(anchor="w")
        self.combo_prod = ctk.CTkComboBox(center, height=40, font=("Arial", 14))
        self.combo_prod.pack(fill="x", pady=5)

        ctk.CTkLabel(center, text="2. Local da Movimentação:").pack(anchor="w", pady=(10,0))
        self.combo_local = ctk.CTkOptionMenu(center, values=["Fundo (Depósito)", "Frente (Loja)"], fg_color="#333")
        self.combo_local.pack(fill="x", pady=5)

        self.tipo_var = ctk.StringVar(value="ENTRADA")
        radio_f = ctk.CTkFrame(center)
        radio_f.pack(fill="x", pady=15)
        
        ctk.CTkRadioButton(radio_f, text="🔼 ENTRADA", variable=self.tipo_var, value="ENTRADA", fg_color="#27AE60").pack(side="left", padx=40, pady=10)
        ctk.CTkRadioButton(radio_f, text="🗑️ PERDA", variable=self.tipo_var, value="PERDA", fg_color="#C0392B").pack(side="right", padx=40, pady=10)

        detalhes = ctk.CTkFrame(center, fg_color="transparent")
        detalhes.pack(fill="x", pady=10)
        
        ctk.CTkLabel(detalhes, text="Qtd:").pack(side="left", padx=(0,10))
        self.ent_qtd = ctk.CTkEntry(detalhes, width=120)
        self.ent_qtd.pack(side="left")

        ctk.CTkLabel(detalhes, text="Motivo:").pack(side="left", padx=(20,10))
        self.ent_motivo = ctk.CTkEntry(detalhes, placeholder_text="Ex: Compra NF 123")
        self.ent_motivo.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(center, text="✅ CONFIRMAR", height=50, fg_color="#2980B9", 
                      command=self.confirmar).pack(pady=20, fill="x")
        
        ctk.CTkLabel(center, text="--- OU ---", text_color="#666").pack(pady=10)
        
        ctk.CTkButton(center, text="📦 REPOSIÇÃO RÁPIDA (Fundo -> Frente)", 
                      height=50, fg_color="#8E44AD", hover_color="#732D91",
                      command=self.abrir_reposicao).pack(fill="x")

    def atualizar_produtos(self, produtos_dict):
        self.produtos_cache = produtos_dict
        self.lista_nomes = sorted([p['nome'] for p in produtos_dict.values()])
        self.combo_prod.configure(values=self.lista_nomes)

    def confirmar(self):
        nome = self.combo_prod.get()
        qtd = self.ent_qtd.get().replace(",", ".")
        motivo = self.ent_motivo.get()
        tipo = self.tipo_var.get()
        local = self.combo_local.get().split()[0].lower()

        # Acha o ID pelo nome
        cod = next((c for c, p in self.produtos_cache.items() if p['nome'] == nome), None)
        
        if cod:
            ok, msg = self.controller.movimentar_estoque(cod, qtd, tipo, motivo, "Admin", local)
            if ok:
                messagebox.showinfo("Sucesso", msg)
                self.atualizar_sistema()
            else:
                messagebox.showerror("Erro", msg)
        else:
            messagebox.showerror("Erro", "Produto inválido")

    def abrir_reposicao(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Reposição de Loja")
        dialog.geometry("400x450")
        
        # Centraliza e foca
        dialog.transient(self)
        dialog.lift()
        dialog.focus_force()

        ctk.CTkLabel(dialog, text="REPOSIÇÃO RÁPIDA", font=("Arial", 16, "bold"), text_color="#8E44AD").pack(pady=20)
        combo = ctk.CTkComboBox(dialog, values=self.lista_nomes, width=300)
        combo.pack(pady=10)

        ent = ctk.CTkEntry(dialog, placeholder_text="Qtd para Frente", width=150, font=("Arial", 20))
        ent.pack(pady=10); ent.focus_set()

        def salvar():
            nome = combo.get()
            cod = next((c for c, p in self.produtos_cache.items() if p['nome'] == nome), None)
            if cod:
                ok, msg = self.controller.transferir_fundo_para_frente(cod, ent.get(), "Admin")
                if ok:
                    messagebox.showinfo("Sucesso", msg)
                    dialog.destroy()
                    self.atualizar_sistema()
                else:
                    messagebox.showerror("Erro", msg)

        ctk.CTkButton(dialog, text="TRANSFERIR", fg_color="#27AE60", height=45, command=salvar).pack(pady=30)