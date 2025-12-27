import customtkinter as ctk
from tkinter import ttk
from src.models import database

class AbaHistorico(ctk.CTkFrame):
    def __init__(self, master, produtos_ref, callback_atualizar):
        super().__init__(master)
        self.produtos = produtos_ref # Referência para saber preços/unidades
        self.callback_atualizar = callback_atualizar
        self.janela_ajuda = None
        self.montar_layout()

    def montar_layout(self):
        filter_f = ctk.CTkFrame(self)
        filter_f.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(filter_f, text="Extrato Completo", font=("Arial", 14, "bold")).pack(side="left", padx=10)
        
        # Botão de Ajuda AZUL
        ctk.CTkButton(filter_f, text="?", width=30, fg_color="#2980B9", hover_color="#1F618D",
                      command=self.mostrar_ajuda).pack(side="left", padx=5)
        
        ctk.CTkButton(filter_f, text="🔄 Atualizar", width=150, command=self.callback_atualizar).pack(side="right", padx=10)

        cols = ("data", "tipo", "produto", "qtd", "valor", "usuario", "motivo")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        
        hdrs = ["DATA/HORA", "TIPO", "PRODUTO", "QTD", "VALOR", "USUÁRIO", "MOTIVO"]
        for c, h in zip(cols, hdrs): self.tree.heading(c, text=h)

        self.tree.column("data", width=140, anchor="center")
        self.tree.column("tipo", width=140, anchor="center")
        self.tree.column("produto", width=220)
        self.tree.column("qtd", width=80, anchor="center")
        self.tree.column("valor", width=100, anchor="e")
        self.tree.column("usuario", width=100, anchor="center")
        self.tree.column("motivo", width=200)

        scroll = ctk.CTkScrollbar(self, command=self.tree.yview)
        self.tree.configure(yscroll=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Configuração de Cores
        colors = {
            "SAIDA_VENDA": "#e6b0aa",       # Vermelho claro
            "ENTRADA_FUNDO": "#abebc6",     # Verde claro
            "ENTRADA_FRENTE": "#abebc6",    # Verde claro
            "TRANSFERENCIA": "#d7bde2",     # Roxo claro
            "PERDA_FUNDO": "#fad7a0",       # Laranja
            "PERDA_FRENTE": "#fad7a0"       # Laranja
        }
        for k, v in colors.items(): self.tree.tag_configure(k, background=v, foreground="black")

    def atualizar(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        try: movs = database.carregar_json(database.ARQ_MOVIMENTOS)[::-1]
        except: movs = []

        for m in movs:
            p = self.produtos.get(m['cod'], {})
            un = p.get('unidade', 'UN')
            qtd = float(m.get('qtd', 0))
            
            # Formata Qtd (KG com 3 casas, UN inteiro se possível)
            qtd_fmt = f"{qtd:.3f}" if un in ['KG', 'L'] else (f"{int(qtd)}" if qtd.is_integer() else f"{qtd:.2f}")
            # Formata Valor
            val_fmt = f"R$ {qtd * p.get('preco', 0):.2f}"

            self.tree.insert("", "end", values=(
                m.get('data'), m.get('tipo'), m.get('nome'), qtd_fmt, val_fmt, m.get('usuario'), m.get('motivo')
            ), tags=(m.get('tipo'),))

    def mostrar_ajuda(self):
        """Janela flutuante não-bloqueante com explicações"""
        if self.janela_ajuda and self.janela_ajuda.winfo_exists():
            self.janela_ajuda.lift()
            self.janela_ajuda.focus_force()
            return
        
        self.janela_ajuda = ctk.CTkToplevel(self)
        self.janela_ajuda.title("Ajuda Estoque")
        self.janela_ajuda.geometry("500x600")
        
        # Mantém a janela no topo mas permite clicar no sistema principal
        self.janela_ajuda.transient(self)
        self.janela_ajuda.lift()
        self.janela_ajuda.focus_force()
        
        ctk.CTkLabel(self.janela_ajuda, text="📖 GUIA RÁPIDO", font=("Arial", 20, "bold"), text_color="#2CC985").pack(pady=20)
        
        # --- Legenda de Cores ---
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
        linha_legenda("#abebc6", "ENTRADA", "Compra ou Produção.")
        linha_legenda("#d7bde2", "TRANSFERÊNCIA", "Movimento Fundo -> Frente.")
        linha_legenda("#fad7a0", "PERDA", "Quebra, Vencimento ou Uso.")

        # --- Regras de Negócio ---
        frame_regras = ctk.CTkFrame(self.janela_ajuda)
        frame_regras.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame_regras, text="⚙️ REGRAS DO SISTEMA", font=("Arial", 14, "bold")).pack(pady=10)
        
        texto_regras = """
1. ESTOQUE DUPLO (FRENTE vs FUNDO):
• FRENTE (Loja): Estoque visível ao cliente. O Caixa vende daqui.
• FUNDO (Depósito): Estoque fechado. Transfira para Frente antes de vender.

2. FLUXO OBRIGATÓRIO:
• Chegou Mercadoria? Lance ENTRADA no FUNDO.
• Prateleira Vazia? Faça TRANSFERÊNCIA (Fundo -> Frente).
• Venda? Baixa automática da FRENTE no caixa.

3. POR QUE NÃO TEM "SAÍDA MANUAL"?
• Se saiu, ou foi VENDA (dinheiro no caixa) ou foi PERDA (prejuízo).
• "Saída" genérica cria furos no caixa e no estoque.
"""
        lbl_regras = ctk.CTkLabel(frame_regras, text=texto_regras, justify="left", anchor="nw", padx=10, font=("Consolas", 12))
        lbl_regras.pack(fill="both", expand=True)