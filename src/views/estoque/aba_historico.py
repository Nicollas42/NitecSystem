import customtkinter as ctk
from tkinter import ttk
from src.models import database

class AbaHistorico(ctk.CTkFrame):
    def __init__(self, master, produtos_ref, callback_atualizar):
        super().__init__(master)
        self.produtos = produtos_ref 
        self.callback_atualizar = callback_atualizar
        self.janela_ajuda = None
        self.montar_layout()

    def montar_layout(self):
        filter_f = ctk.CTkFrame(self)
        filter_f.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(filter_f, text="Extrato Completo", font=("Arial", 14, "bold")).pack(side="left", padx=10)
        
        ctk.CTkButton(filter_f, text="?", width=30, fg_color="#2980B9", hover_color="#1F618D",
                      command=self.mostrar_ajuda).pack(side="left", padx=5)
        
        ctk.CTkButton(filter_f, text="🔄 Atualizar", width=150, command=self.callback_atualizar).pack(side="right", padx=10)

        # Configuração das Colunas e Cabeçalhos
        cols = ("data", "tipo", "produto", "qtd", "valor", "usuario", "motivo")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        
        hdrs = ["DATA/HORA", "TIPO", "PRODUTO", "QTD", "VALOR (R$)", "USUÁRIO", "MOTIVO"]
        
        # Configura os Cabeçalhos (Centralizados por padrão)
        for c, h in zip(cols, hdrs): 
            self.tree.heading(c, text=h)

        # --- ALINHAMENTO DAS COLUNAS (AJUSTADO) ---
        self.tree.column("data", width=140, anchor="center")      # Data centralizada
        self.tree.column("tipo", width=140, anchor="center")      # Tipo centralizado
        self.tree.column("produto", width=220, anchor="w")        # Produto à Esquerda (West)
        self.tree.column("qtd", width=100, anchor="e")            # Qtd à Direita (East)
        self.tree.column("valor", width=100, anchor="e")          # Valor à Direita (East)
        self.tree.column("usuario", width=100, anchor="center")   # Usuário centralizado
        self.tree.column("motivo", width=250, anchor="w")         # Motivo à Esquerda (West)
        # ------------------------------------------

        scroll = ctk.CTkScrollbar(self, command=self.tree.yview)
        self.tree.configure(yscroll=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        colors = {
            "SAIDA_VENDA": "#e6b0aa",       
            "ENTRADA_FUNDO": "#abebc6",     
            "ENTRADA_PRODUCAO": "#abebc6",  
            "SAIDA_PRODUCAO": "#fad7a0",    
            "TRANSFERENCIA": "#d7bde2",     
            "PERDA_FUNDO": "#fad7a0",       
            "PERDA_FRENTE": "#fad7a0"       
        }
        for k, v in colors.items(): self.tree.tag_configure(k, background=v, foreground="black")

    def formatar_numero_inteligente(self, valor):
        if float(valor).is_integer():
            return f"{int(valor)}"
        else:
            return f"{valor:.3f}".rstrip('0').rstrip('.')

    def atualizar(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        try: movs = database.carregar_json(database.ARQ_MOVIMENTOS)[::-1]
        except: movs = []

        for m in movs:
            cod_prod = str(m.get('cod'))
            p = self.produtos.get(cod_prod, {})
            un = p.get('unidade', 'UN')
            qtd = float(m.get('qtd', 0))
            
            qtd_limpa = self.formatar_numero_inteligente(qtd)
            # Adicionei um espaço no final (" ") para não grudar na borda direita
            qtd_final = f"{qtd_limpa} {un} " 

            is_insumo = p.get('tipo') == 'INSUMO'
            if is_insumo or 'PRODUCAO' in m.get('tipo', ''):
                valor_base = p.get('custo', 0.0)
            else:
                valor_base = p.get('preco', 0.0)

            valor_total = abs(qtd) * valor_base
            # Adicionei um espaço no final (" ") para não grudar na borda direita
            val_fmt = f"R$ {valor_total:.2f} "

            self.tree.insert("", "end", values=(
                m.get('data'), 
                m.get('tipo'), 
                m.get('nome'), 
                qtd_final, 
                val_fmt, 
                m.get('usuario'), 
                m.get('motivo')
            ), tags=(m.get('tipo'),))

    def mostrar_ajuda(self):
        if self.janela_ajuda and self.janela_ajuda.winfo_exists():
            self.janela_ajuda.lift(); self.janela_ajuda.focus_force(); return
        
        self.janela_ajuda = ctk.CTkToplevel(self)
        self.janela_ajuda.title("Ajuda Estoque")
        self.janela_ajuda.geometry("500x600")
        self.janela_ajuda.transient(self); self.janela_ajuda.lift(); self.janela_ajuda.focus_force()
        ctk.CTkLabel(self.janela_ajuda, text="📖 GUIA RÁPIDO", font=("Arial", 20, "bold"), text_color="#2CC985").pack(pady=20)
        
        frame_cores = ctk.CTkFrame(self.janela_ajuda)
        frame_cores.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(frame_cores, text="🎨 ENTENDA AS CORES", font=("Arial", 14, "bold")).pack(pady=10)

        def linha_legenda(cor, titulo, desc):
            row = ctk.CTkFrame(frame_cores, fg_color="transparent")
            row.pack(fill="x", pady=5, padx=10)
            ctk.CTkLabel(row, text="      ", fg_color=cor, width=40, corner_radius=6).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=titulo, font=("Arial", 12, "bold"), width=120, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=desc, text_color="#ccc", anchor="w").pack(side="left", fill="x", expand=True)

        linha_legenda("#e6b0aa", "SAÍDA VENDA", "Venda realizada no caixa.")
        linha_legenda("#abebc6", "ENTRADA", "Compra ou Produção Pronta.")
        linha_legenda("#fad7a0", "SAÍDA PROD.", "Insumo consumido na produção.")
        linha_legenda("#d7bde2", "TRANSFERÊNCIA", "Movimento Fundo -> Frente.")
        
        frame_regras = ctk.CTkFrame(self.janela_ajuda)
        frame_regras.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(frame_regras, text="💰 VALORES (CUSTO vs VENDA)", font=("Arial", 14, "bold")).pack(pady=10)
        texto_regras = """
1. PRODUTOS FINAIS (Pão, Bolo):
• Valor = PREÇO DE VENDA (Receita Potencial).

2. INSUMOS (Farinha, Sal):
• Valor = PREÇO DE CUSTO (Gasto Real).
"""
        lbl_regras = ctk.CTkLabel(frame_regras, text=texto_regras, justify="left", anchor="nw", padx=10, font=("Consolas", 12))
        lbl_regras.pack(fill="both", expand=True)