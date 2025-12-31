# src/views/estoque/aba_auditoria.py

import customtkinter as ctk
from tkinter import ttk
from datetime import datetime, date
from src.utils.componentes_estilizados import CTkCalendar, aplicar_mascara_data
from src.utils.formata_numeros_br import formata_numeros_br

class AbaAuditoria(ctk.CTkFrame):
    """
    Aba responsável pela Auditoria de Estoque.
    Gera relatórios detalhados de vendas vs. perdas e resultado financeiro por item.
    """

    def __init__(self, master, produtos_ref, callback_atualizar, controller):
        super().__init__(master)
        self.produtos = produtos_ref
        self.callback_atualizar = callback_atualizar
        self.controller = controller
        
        self.popup_calendario = None
        
        # Variáveis de ordenação
        self.sort_col = None
        self.sort_dir = "desc" # Padrão: maior para o menor

        self.montar_layout()
        self.resetar_datas_mes_atual()
        
        # Gera o relatório inicial após renderizar
        self.after(500, self.gerar_relatorio)

    def montar_layout(self):
        """Monta a interface da aba de Auditoria."""
        # --- CABEÇALHO ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(header, text="📋 Auditoria de Estoque", font=("Arial", 18, "bold"), text_color="#2CC985").pack(side="left", padx=10)

        # Filtro de Datas
        frame_filtros = ctk.CTkFrame(header, fg_color="transparent")
        frame_filtros.pack(side="right")

        self.criar_campo_data(frame_filtros, "De:", "ent_data_ini")
        self.criar_campo_data(frame_filtros, "Até:", "ent_data_fim")

        ctk.CTkButton(frame_filtros, text="🔄 Atualizar Auditoria", width=140, fg_color="#2980B9", 
                      command=self.gerar_relatorio).pack(side="left", padx=10)

        # --- TABELA DE RESULTADOS ---
        table_container = ctk.CTkFrame(self, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Definição das colunas
        self.cols = ("cod", "nome", "qtd_venda", "receita", "cmv", "qtd_perda", "vlr_perda", "lucro")
        self.tree = ttk.Treeview(table_container, columns=self.cols, show="headings", selectmode="browse")

        # Configuração dos Cabeçalhos
        cabecalhos = {
            "cod": "ID",
            "nome": "PRODUTO",
            "qtd_venda": "QTD VENDAS",
            "receita": "RECEITA (R$)",
            "cmv": "CUSTO VENDA",
            "qtd_perda": "QTD PERDA",
            "vlr_perda": "PREJUÍZO (R$)",
            "lucro": "LUCRO LÍQ. (R$)"
        }

        for col, texto in cabecalhos.items():
            self.tree.heading(col, text=texto, command=lambda c=col: self.ordenar_coluna(c))
            anchor = "w" if col == "nome" else "center"
            self.tree.column(col, anchor=anchor)

        # Larguras das colunas
        self.tree.column("cod", width=50)
        self.tree.column("nome", width=220)
        self.tree.column("qtd_venda", width=90)
        self.tree.column("receita", width=100)
        self.tree.column("cmv", width=100)
        self.tree.column("qtd_perda", width=90)
        self.tree.column("vlr_perda", width=100)
        self.tree.column("lucro", width=110)

        # Scrollbar
        scroll = ctk.CTkScrollbar(table_container, command=self.tree.yview)
        self.tree.configure(yscroll=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        # Cores para Lucro (Verde) e Prejuízo (Vermelho)
        self.tree.tag_configure("positivo", foreground="#27AE60") 
        self.tree.tag_configure("negativo", foreground="#C0392B") 
        self.tree.tag_configure("neutro", foreground="white")

    def criar_campo_data(self, parent, label, attr_name):
        """Cria inputs de data com suporte a calendário."""
        ctk.CTkLabel(parent, text=label, text_color="#ccc", font=("Arial", 12)).pack(side="left", padx=(10, 5))
        entry = ctk.CTkEntry(parent, width=100, justify="center")
        entry.pack(side="left")
        
        entry.bind("<Button-1>", lambda e: self.abrir_calendario(e, entry))
        entry.bind("<KeyRelease>", lambda e: aplicar_mascara_data(e, entry))
        
        setattr(self, attr_name, entry)

    def abrir_calendario(self, event, entry_widget):
        """Abre o popup de calendário."""
        if self.popup_calendario: 
            try: self.popup_calendario.destroy()
            except: pass
        
        def on_select(data_str):
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, data_str)
        
        self.popup_calendario = CTkCalendar(self, entry_widget=entry_widget, on_select=on_select)

    def resetar_datas_mes_atual(self):
        """Define o período padrão como o mês atual."""
        hoje = date.today()
        primeiro_dia = date(hoje.year, hoje.month, 1)
        
        self.ent_data_ini.delete(0, 'end')
        self.ent_data_ini.insert(0, primeiro_dia.strftime("%d/%m/%Y"))
        
        self.ent_data_fim.delete(0, 'end')
        self.ent_data_fim.insert(0, hoje.strftime("%d/%m/%Y"))

    def get_datas(self):
        """Retorna as datas de início e fim convertidas para objeto date."""
        try:
            d_ini = datetime.strptime(self.ent_data_ini.get(), "%d/%m/%Y").date()
            d_fim = datetime.strptime(self.ent_data_fim.get(), "%d/%m/%Y").date()
            return d_ini, d_fim
        except:
            return None, None

    def gerar_relatorio(self):
        """Processa os dados e popula a tabela de auditoria."""
        for i in self.tree.get_children(): self.tree.delete(i)

        dt_ini, dt_fim = self.get_datas()
        if not dt_ini or not dt_fim: return 

        # 1. Pega dados do Controller
        movimentos = self.controller.carregar_movimentacoes()
        self.produtos = self.controller.carregar_produtos() 
        relatorio = {}

        # 2. Inicializa estrutura para todos os produtos
        for cod, dados in self.produtos.items():
            relatorio[cod] = {
                "nome": dados['nome'],
                "custo_unit": dados.get('custo', 0),
                "preco_unit": dados.get('preco', 0),
                "qtd_vendida": 0,
                "qtd_perda": 0,
                "receita_total": 0.0,
                "custo_vendas": 0.0, 
                "valor_perda": 0.0, 
            }

        # 3. Processa Movimentos
        for mov in movimentos:
            try:
                data_mov = datetime.strptime(mov['data'].split()[0], "%Y-%m-%d").date()
            except: continue

            if not (dt_ini <= data_mov <= dt_fim): continue
            
            cod = str(mov.get('cod'))
            if cod not in relatorio: continue 

            qtd = abs(float(mov.get('qtd', 0)))
            tipo = mov.get('tipo', '')
            
            custo_atual = relatorio[cod]['custo_unit']
            preco_atual = relatorio[cod]['preco_unit']

            if "VENDA" in tipo:
                relatorio[cod]['qtd_vendida'] += qtd
                relatorio[cod]['receita_total'] += (qtd * preco_atual)
                relatorio[cod]['custo_vendas'] += (qtd * custo_atual)
            
            elif "PERDA" in tipo:
                relatorio[cod]['qtd_perda'] += qtd
                relatorio[cod]['valor_perda'] += (qtd * custo_atual)

        # 4. Formata para Tabela
        lista_final = []
        for cod, r in relatorio.items():
            if r['qtd_vendida'] == 0 and r['qtd_perda'] == 0: continue
                
            lucro_liquido = r['receita_total'] - r['custo_vendas'] - r['valor_perda']
            
            lista_final.append({
                "cod": cod,
                "nome": r['nome'],
                "qtd_venda": r['qtd_vendida'], 
                "receita": r['receita_total'],
                "cmv": r['custo_vendas'],
                "qtd_perda": r['qtd_perda'],
                "vlr_perda": r['valor_perda'],
                "lucro": lucro_liquido
            })

        self.popular_tabela(lista_final)

    def popular_tabela(self, dados):
        """Insere os dados processados na Treeview."""
        # Ordenação
        if self.sort_col:
            reverse = (self.sort_dir == "desc")
            dados.sort(key=lambda x: x[self.sort_col], reverse=reverse)
        else:
            dados.sort(key=lambda x: x['lucro'], reverse=True)

        for item in dados:
            tag = "neutro"
            if item['lucro'] > 0: tag = "positivo"
            elif item['lucro'] < 0: tag = "negativo"

            vals = (
                item['cod'],
                item['nome'],
                formata_numeros_br(item['qtd_venda'], moeda=False),
                formata_numeros_br(item['receita'], moeda=True),
                formata_numeros_br(item['cmv'], moeda=True),
                formata_numeros_br(item['qtd_perda'], moeda=False),
                formata_numeros_br(item['vlr_perda'], moeda=True),
                formata_numeros_br(item['lucro'], moeda=True),
            )
            self.tree.insert("", "end", values=vals, tags=(tag,))

    def ordenar_coluna(self, col):
        """Define a coluna e direção de ordenação."""
        if self.sort_col == col:
            self.sort_dir = "asc" if self.sort_dir == "desc" else "desc"
        else:
            self.sort_col = col
            self.sort_dir = "desc"
        
        self.gerar_relatorio()

    def atualizar(self):
        """Chamado externamente para atualizar dados."""
        self.gerar_relatorio()