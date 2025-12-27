# src/views/estoque/aba_movimentacao.py
import customtkinter as ctk
from tkinter import messagebox
from src.utils.componentes_estilizados import CTkFloatingDropdown
from src.utils.textos_ajuda import abrir_ajuda

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

        header = ctk.CTkFrame(center, fg_color="transparent")
        header.pack(pady=10)
        ctk.CTkLabel(header, text="REGISTRO DE MOVIMENTAÇÃO", font=("Arial", 18, "bold")).pack(side="left")
        ctk.CTkButton(header, text="?", width=25, height=25, fg_color="#2980B9", command=self.mostrar_ajuda).pack(side="left", padx=10)

        ctk.CTkLabel(center, text="1. Selecione o Produto:").pack(anchor="w")
        self.ent_prod = ctk.CTkEntry(center, height=40, font=("Arial", 14), placeholder_text="Digite para buscar...")
        self.ent_prod.pack(fill="x", pady=5)
        self.dropdown_prod = CTkFloatingDropdown(self.ent_prod, self.lista_nomes, width=400)

        ctk.CTkLabel(center, text="2. Local da Movimentação:").pack(anchor="w", pady=(10,0))
        self.combo_local = ctk.CTkOptionMenu(center, values=["Fundo (Depósito)", "Frente (Loja)"], fg_color="#333", height=40)
        self.combo_local.pack(fill="x", pady=5)

        ctk.CTkLabel(center, text="3. Tipo de Operação:").pack(anchor="w", pady=(10,5))
        self.tipo_var = ctk.StringVar(value="ENTRADA")
        radio_f = ctk.CTkFrame(center, fg_color="transparent")
        radio_f.pack(fill="x", pady=5)
        ctk.CTkRadioButton(radio_f, text="🔼 ENTRADA", variable=self.tipo_var, value="ENTRADA", fg_color="#27AE60").pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(radio_f, text="🗑️ PERDA", variable=self.tipo_var, value="PERDA", fg_color="#C0392B").pack(side="left", padx=20)

        detalhes = ctk.CTkFrame(center, fg_color="transparent")
        detalhes.pack(fill="x", pady=20)
        ctk.CTkLabel(detalhes, text="Quantidade:").pack(side="left", padx=(0,10))
        self.ent_qtd = ctk.CTkEntry(detalhes, width=120, height=40, font=("Arial", 14), justify="center")
        self.ent_qtd.pack(side="left")
        ctk.CTkLabel(detalhes, text="Motivo:").pack(side="left", padx=(20,10))
        self.ent_motivo = ctk.CTkEntry(detalhes, placeholder_text="Ex: Compra NF 123", height=40)
        self.ent_motivo.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(center, text="✅ CONFIRMAR", height=50, fg_color="#2980B9", 
                      command=self.confirmar).pack(pady=10, fill="x")

    def mostrar_ajuda(self):
        abrir_ajuda(self, "movimentacao")

    def atualizar_produtos(self, produtos_dict):
        self.produtos_cache = produtos_dict
        self.lista_nomes = sorted([p['nome'] for p in produtos_dict.values()])
        self.dropdown_prod.atualizar_dados(self.lista_nomes)

    def confirmar(self):
        nome = self.ent_prod.get()
        cod = next((c for c, p in self.produtos_cache.items() if p['nome'] == nome), None)
        if cod:
            ok, msg = self.controller.movimentar_estoque(cod, self.ent_qtd.get(), self.tipo_var.get(), self.ent_motivo.get(), "Admin", self.combo_local.get().split()[0].lower())
            if ok: messagebox.showinfo("Sucesso", msg); self.atualizar_sistema()