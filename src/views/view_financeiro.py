# src/views/view_financeiro.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from src.controllers.estoque_controller import EstoqueController

class FinanceiroFrame(ctk.CTkFrame):
    def __init__(self, master, usuario_dados, callback_voltar):
        super().__init__(master)
        self.voltar_menu = callback_voltar
        
        # Conecta ao Controller SQL
        self.ctrl = EstoqueController()
        
        self.vendas = self.ctrl.carregar_vendas()
        self.movimentos = self.ctrl.carregar_movimentacoes()
        self.produtos = self.ctrl.carregar_produtos()

        self.montar_layout()

    def montar_layout(self):
        # CABEÇALHO
        top = ctk.CTkFrame(self, height=50, corner_radius=0)
        top.pack(fill="x")
        
        ctk.CTkButton(top, text="🔙 Voltar", width=100, fg_color="#555", 
                      command=self.voltar_menu).pack(side="left", padx=(10, 5), pady=10)
        
        # Botão Ajuda
        ctk.CTkButton(top, text="?", width=30, fg_color="#333", hover_color="#444", 
                      command=self.mostrar_ajuda).pack(side="left", padx=5)

        ctk.CTkLabel(top, text="ANÁLISE FINANCEIRA (PostgreSQL)", font=("Arial", 16, "bold")).pack(side="left", padx=20)

        # CÁLCULOS
        total_vendas = sum(float(v['total']) for v in self.vendas)
        qtd_vendas = len(self.vendas)
        
        total_perdas = 0
        # Filtra apenas movimentos de PERDA
        sobras = [m for m in self.movimentos if 'PERDA' in m['tipo']]
        
        for s in sobras:
            cod = str(s['cod'])
            # Busca preço atual
            if cod in self.produtos:
                preco = float(self.produtos[cod]['preco'])
                # s['qtd'] em PERDA é negativo no movimento, mas queremos o absoluto para somar valor
                total_perdas += (abs(float(s['qtd'])) * preco)

        lucro_bruto = total_vendas - total_perdas

        # CARDS
        kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpi_frame.pack(fill="x", padx=20, pady=20)

        self.criar_card(kpi_frame, "💰 RECEITA BRUTA", f"R$ {total_vendas:.2f}", "#27AE60", 0)
        self.criar_card(kpi_frame, "🗑️ PERDAS (R$)", f"R$ {total_perdas:.2f}", "#C0392B", 1)
        self.criar_card(kpi_frame, "📊 SALDO LÍQUIDO", f"R$ {lucro_bruto:.2f}", "#2980B9", 2)
        self.criar_card(kpi_frame, "🧾 Nº VENDAS", f"{qtd_vendas}", "#8E44AD", 3)

        # TABELA
        ctk.CTkLabel(self, text="Histórico Recente de Vendas", font=("Arial", 14, "bold")).pack(anchor="w", padx=20)
        
        tabela_frame = ctk.CTkFrame(self)
        tabela_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        cols = ("data", "op", "pag", "total")
        tree = ttk.Treeview(tabela_frame, columns=cols, show="headings")
        tree.heading("data", text="DATA")
        tree.heading("op", text="VENDEDOR")
        tree.heading("pag", text="PAGAMENTO")
        tree.heading("total", text="VALOR (R$)")

        tree.column("data", width=150, anchor="center")
        tree.column("op", width=150)
        tree.column("pag", width=100, anchor="center")
        tree.column("total", width=100, anchor="e")
        tree.pack(fill="both", expand=True)

        # Inverte para mostrar as mais recentes primeiro (já vem ordenado do banco, mas reforça)
        for v in self.vendas:
            val = float(v['total'])
            tree.insert("", "end", values=(v['data'], v['operador'], v.get('pagamento', 'Dinheiro'), f"{val:.2f}"))

    def criar_card(self, parent, titulo, valor, cor, col):
        card = ctk.CTkFrame(parent, fg_color=cor, height=100)
        card.grid(row=0, column=col, padx=10, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)
        ctk.CTkLabel(card, text=titulo, text_color="white", font=("Arial", 12, "bold")).pack(pady=(15, 5))
        ctk.CTkLabel(card, text=valor, text_color="white", font=("Arial", 22, "bold")).pack(pady=(0, 15))

    def mostrar_ajuda(self):
        msg = """
        💰 ANÁLISE FINANCEIRA

        Este painel mostra a saúde real do seu negócio baseada no Banco de Dados.

        📊 Entenda os Números:
        - Receita Bruta: Soma de todas as vendas finalizadas no Caixa.
        - Perdas (R$): Soma de todas as sobras registradas (Qtd x Preço de Venda).
        - Saldo Líquido: É o dinheiro que sobra (Receita - Perdas).

        📝 Histórico:
        - A tabela abaixo mostra as últimas vendas realizadas.
        """
        messagebox.showinfo("Ajuda - Financeiro", msg)