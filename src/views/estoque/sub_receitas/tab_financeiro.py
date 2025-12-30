import customtkinter as ctk
from src.utils.formata_numeros_br import formata_numeros_br

class TabFinanceiro(ctk.CTkFrame):
    def __init__(self, master, callback_salvar, callback_recalcular):
        super().__init__(master, fg_color="transparent")
        self.callback_salvar = callback_salvar
        self.callback_recalcular = callback_recalcular
        self.montar_layout()

    def montar_layout(self):
        f_res = ctk.CTkFrame(self, fg_color="transparent")
        f_res.pack(fill="x", pady=10)
        
        self.lbl_custo_mp = ctk.CTkLabel(f_res, text="Matéria Prima: R$ 0,00", anchor="w")
        self.lbl_custo_mp.pack(fill="x")
        
        self.lbl_custo_ind = ctk.CTkLabel(f_res, text="Custos Indiretos: R$ 0,00", anchor="w")
        self.lbl_custo_ind.pack(fill="x")
        
        self.lbl_custo_total = ctk.CTkLabel(f_res, text="CUSTO TOTAL LOTE: R$ 0,00", font=("Arial", 12, "bold"), anchor="w", text_color="#E74C3C")
        self.lbl_custo_total.pack(fill="x", pady=5)
        
        ctk.CTkLabel(f_res, text="-"*40).pack()
        
        # Rendimento
        f_rend = ctk.CTkFrame(f_res, fg_color="transparent")
        f_rend.pack(fill="x", pady=5)
        ctk.CTkLabel(f_rend, text="Rendimento (Qtd):").pack(side="left")
        self.ent_rendimento = ctk.CTkEntry(f_rend, width=80)
        self.ent_rendimento.insert(0, "1")
        self.ent_rendimento.pack(side="left", padx=5)
        self.ent_rendimento.bind("<KeyRelease>", self.callback_recalcular) # Recalcula ao digitar
        
        self.lbl_custo_unit = ctk.CTkLabel(f_res, text="CUSTO UNITÁRIO: R$ 0,00", 
                                           font=("Arial", 16, "bold"), text_color="#E74C3C")
        self.lbl_custo_unit.pack(pady=10)
        
        # Precificação
        f_prec = ctk.CTkFrame(self, border_width=1, border_color="#2980B9")
        f_prec.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(f_prec, text="Margem de Lucro (%):").pack(side="left", padx=10, pady=10)
        self.ent_margem = ctk.CTkEntry(f_prec, width=60)
        self.ent_margem.insert(0, "100")
        self.ent_margem.pack(side="left", padx=5)
        self.ent_margem.bind("<KeyRelease>", self.callback_recalcular) # Recalcula ao digitar
        
        self.lbl_sugestao = ctk.CTkLabel(self, text="Preço Sugerido: R$ 0,00", 
                                         font=("Arial", 20, "bold"), text_color="#27AE60")
        self.lbl_sugestao.pack(pady=10)

        ctk.CTkButton(self, text="💾 SALVAR FICHA TÉCNICA", height=50, fg_color="#27AE60", 
                      command=self.callback_salvar).pack(fill="x", side="bottom", padx=20, pady=20)

    def get_rendimento(self): 
        try: return float(self.ent_rendimento.get().replace(",", "."))
        except: return 1.0
        
    def get_margem(self): 
        try: return float(self.ent_margem.get().replace(",", "."))
        except: return 0.0
    
    def set_valores(self, rendimento, margem):
        self.ent_rendimento.delete(0, 'end'); self.ent_rendimento.insert(0, rendimento)
        self.ent_margem.delete(0, 'end'); self.ent_margem.insert(0, margem)

    def atualizar_resumo(self, mp, indireto, total, unit, preco):
        self.lbl_custo_mp.configure(text=f"Matéria Prima: R$ {formata_numeros_br(mp, True)}")
        self.lbl_custo_ind.configure(text=f"Custos Indiretos: R$ {formata_numeros_br(indireto, True)}")
        self.lbl_custo_total.configure(text=f"CUSTO TOTAL LOTE: R$ {formata_numeros_br(total, True)}")
        self.lbl_custo_unit.configure(text=f"CUSTO UNITÁRIO: R$ {formata_numeros_br(unit, True)}")
        self.lbl_sugestao.configure(text=f"Preço Sugerido: R$ {formata_numeros_br(preco, True)}")