# src/views/estoque/aba_historico.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, date
from src.models import database
from src.utils.componentes_estilizados import CTkFloatingDropdown, CTkCalendar
from src.utils.textos_ajuda import abrir_ajuda

class AbaHistorico(ctk.CTkFrame):
    def __init__(self, master, produtos_ref, callback_atualizar):
        super().__init__(master)
        self.produtos = produtos_ref 
        self.callback_atualizar = callback_atualizar
        self.popup_calendario = None 
        
        self.dropdown_prod = None    
        self.dropdown_user = None
        self.dropdown_tipo = None
        
        self.sort_col = None
        self.sort_dir = "original"
        
        self.lista_produtos_full = sorted([p['nome'] for p in self.produtos.values()])
        self.lista_usuarios_full = self.carregar_lista_usuarios()
        self.lista_tipos = ["TODOS", "VENDA", "ENTRADA", "PRODUCAO", "TRANSFERENCIA", "PERDA"]

        self.montar_layout()
        self.configurar_cores_tags()
        self.monitorar_eventos_globais()
        self.resetar_datas_hoje()
        self.filtrar_dados() 

    def montar_layout(self):
        """
        Gera a interface visual da aba de histórico.
        """
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        ctk.CTkLabel(header_frame, text="Extrato Completo", font=("Arial", 16, "bold"), text_color="#2CC985").pack(side="left", padx=10)
        ctk.CTkButton(header_frame, text="?", width=25, height=25, fg_color="#2980B9", command=self.mostrar_ajuda).pack(side="left")
        
        self.frame_filtros = ctk.CTkFrame(self, border_width=1, border_color="#444")
        self.frame_filtros.pack(fill="x", padx=10, pady=5)
        row = ctk.CTkFrame(self.frame_filtros, fg_color="transparent")
        row.pack(fill="x", padx=5, pady=8)

        # Campos de Data com o bind para o calendário corrigido
        self.criar_campo_data(row, "De:", "ent_data_ini")
        self.criar_campo_data(row, "Até:", "ent_data_fim")

        ctk.CTkLabel(row, text="Tipo:", text_color="#ccc", font=("Arial", 11)).pack(side="left", padx=(10, 2))
        self.ent_tipo = ctk.CTkEntry(row, width=120, placeholder_text="Selecione...")
        self.ent_tipo.pack(side="left", padx=2)
        self.dropdown_tipo = CTkFloatingDropdown(self.ent_tipo, self.lista_tipos, width=150)

        ctk.CTkLabel(row, text="Prod:", text_color="#ccc", font=("Arial", 11)).pack(side="left", padx=(10, 2))
        self.ent_prod = ctk.CTkEntry(row, width=140, placeholder_text="Digite...")
        self.ent_prod.pack(side="left", padx=2)
        self.dropdown_prod = CTkFloatingDropdown(self.ent_prod, self.lista_produtos_full, width=250)

        ctk.CTkLabel(row, text="User:", text_color="#ccc", font=("Arial", 11)).pack(side="left", padx=(10, 2))
        self.ent_user = ctk.CTkEntry(row, width=90, placeholder_text="Nome...")
        self.ent_user.pack(side="left", padx=2)
        self.dropdown_user = CTkFloatingDropdown(self.ent_user, self.lista_usuarios_full, width=150)

        ctk.CTkButton(row, text="🔎", width=40, fg_color="#27AE60", command=self.aplicar_filtro).pack(side="left", padx=(15, 5))
        ctk.CTkButton(row, text="🧹", width=40, fg_color="#7f8c8d", command=self.limpar_filtros).pack(side="left", padx=5)

        table_container = ctk.CTkFrame(self, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.cols = ("data", "tipo", "produto", "qtd", "valor", "usuario", "motivo")
        self.tree = ttk.Treeview(table_container, columns=self.cols, show="headings")
        self.configurar_colunas_inicial()
        
        scroll = ctk.CTkScrollbar(table_container, command=self.tree.yview)
        self.tree.configure(yscroll=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

    def criar_campo_data(self, parent, label, attr_name):
        """
        Cria campo de entrada de data com bind para calendário.
        """
        ctk.CTkLabel(parent, text=label, text_color="#ccc", font=("Arial", 11)).pack(side="left", padx=(5, 2))
        entry = ctk.CTkEntry(parent, width=90)
        entry.pack(side="left", padx=2)
        # O bind agora chama o método abrir_calendario da classe
        entry.bind("<Button-1>", lambda e: self.abrir_calendario(entry))
        setattr(self, attr_name, entry)

    def abrir_calendario(self, entry_widget):
        """
        Instancia o calendário flutuante.
        """
        if self.popup_calendario: self.fechar_calendario()
        self.popup_calendario = CTkCalendar(
            self.winfo_toplevel(), 
            on_select=lambda data: self.preencher_data(entry_widget, data)
        )

    def preencher_data(self, entry, data):
        """
        Preenche a data e fecha o popup.
        """
        entry.delete(0, 'end')
        entry.insert(0, data)
        self.fechar_calendario()
        self.aplicar_filtro()

    def fechar_calendario(self):
        """
        Fecha a janela do calendário.
        """
        if self.popup_calendario:
            self.popup_calendario.destroy()
            self.popup_calendario = None

    def filtrar_dados(self):
        """
        Consulta o banco via JSON conforme código original.
        """
        for i in self.tree.get_children(): self.tree.delete(i)
        try: todos_movs = database.carregar_json(database.ARQ_MOVIMENTOS)[::-1]
        except: todos_movs = []
        
        f_ini, f_fim = self.get_data_filtro(self.ent_data_ini), self.get_data_filtro(self.ent_data_fim)
        f_tipo = self.ent_tipo.get().strip().upper() or "TODOS"
        f_prod, f_user = self.ent_prod.get().strip().lower(), self.ent_user.get().strip().lower()
        
        linhas = []
        for m in todos_movs:
            data_raw = m.get('data', '')
            try: dt_mov = datetime.strptime(data_raw.split()[0], "%Y-%m-%d").date()
            except: dt_mov = None
            
            if f_ini and dt_mov and dt_mov < f_ini: continue
            if f_fim and dt_mov and dt_mov > f_fim: continue
            if f_tipo != "TODOS" and f_tipo not in m.get('tipo', ''): continue
            if f_prod and f_prod not in m.get('nome', '').lower(): continue
            if f_user and f_user not in m.get('usuario', '').lower(): continue

            p = self.produtos.get(str(m.get('cod')), {})
            qtd = float(m.get('qtd', 0))
            usar_custo = p.get('tipo') == 'INSUMO' or 'PRODUCAO' in m.get('tipo', '') or 'ENTRADA' in m.get('tipo', '')
            base = p.get('custo', 0.0) if usar_custo else p.get('preco', 0.0)
            
            linhas.append({
                'display': (self.formatar_data_br(data_raw), m.get('tipo'), m.get('nome'), 
                            f"{self.formatar_numero_inteligente(qtd)} {p.get('unidade', 'UN')}", 
                            f"R$ {qtd*base:.2f}", m.get('usuario'), m.get('motivo')),
                'tags': (m.get('tipo'),), 'sort_data': data_raw, 'sort_produto': m.get('nome', '').lower(),
                'sort_qtd': qtd, 'sort_valor': abs(qtd*base), 'sort_usuario': m.get('usuario', '').lower(),
                'sort_tipo': m.get('tipo', ''), 'sort_motivo': m.get('motivo', '').lower()
            })

        if self.sort_dir != "original" and self.sort_col:
            key_map = {"data": "sort_data", "tipo": "sort_tipo", "produto": "sort_produto", "qtd": "sort_qtd", "valor": "sort_valor", "usuario": "sort_usuario", "motivo": "sort_motivo"}
            linhas.sort(key=lambda x: x[key_map[self.sort_col]], reverse=(self.sort_dir == "desc"))

        for item in linhas: self.tree.insert("", "end", values=item['display'], tags=item['tags'])

    def configurar_colunas_inicial(self):
        titulos = {"data": "DATA/HORA", "tipo": "TIPO", "produto": "PRODUTO", "qtd": "QTD", "valor": "VALOR (R$)", "usuario": "USUÁRIO", "motivo": "MOTIVO"}
        for col, titulo in titulos.items():
            self.tree.heading(col, text=f"{titulo} ↕", command=lambda c=col: self.ordenar_coluna(c))
            self.tree.column(col, anchor="center")
        self.restaurar_layout_colunas()

    def ordenar_coluna(self, col):
        if self.sort_col == col:
            self.sort_dir = "asc" if self.sort_dir == "original" else "desc" if self.sort_dir == "asc" else "original"
            if self.sort_dir == "original": self.sort_col = None
        else: self.sort_col = col; self.sort_dir = "asc"
        self.atualizar_cabecalhos_icones(); self.filtrar_dados()

    def aplicar_filtro(self):
        self.restaurar_layout_colunas(); self.filtrar_dados()

    def limpar_filtros(self):
        self.resetar_datas_hoje()
        for e in [self.ent_prod, self.ent_user, self.ent_tipo]: e.delete(0, 'end')
        self.sort_col = None; self.sort_dir = "original"; self.atualizar_cabecalhos_icones()
        self.restaurar_layout_colunas(); self.filtrar_dados()

    def carregar_lista_usuarios(self):
        try:
            movs = database.carregar_json(database.ARQ_MOVIMENTOS)
            return sorted(list({m.get('usuario') for m in movs if m.get('usuario')})) or ["Admin"]
        except: return ["Admin"]

    def restaurar_layout_colunas(self):
        larguras = {"data": 140, "tipo": 100, "produto": 220, "qtd": 100, "valor": 100, "usuario": 100, "motivo": 250}
        self.tree.configure(displaycolumns=self.cols)
        for col, width in larguras.items(): self.tree.column(col, width=width)

    def atualizar_cabecalhos_icones(self):
        titulos = {"data": "DATA/HORA", "tipo": "TIPO", "produto": "PRODUTO", "qtd": "QTD", "valor": "VALOR (R$)", "usuario": "USUÁRIO", "motivo": "MOTIVO"}
        for col, base in titulos.items():
            icone = " ↑" if col == self.sort_col and self.sort_dir == "asc" else " ↓" if col == self.sort_col and self.sort_dir == "desc" else " ↕"
            self.tree.heading(col, text=f"{base}{icone}")

    def atualizar(self):
        """
        Atualiza dados ao trocar de aba.
        """
        self.lista_produtos_full = sorted([p['nome'] for p in self.produtos.values()])
        self.dropdown_prod.atualizar_dados(self.lista_produtos_full)
        self.lista_usuarios_full = self.carregar_lista_usuarios()
        self.dropdown_user.atualizar_dados(self.lista_usuarios_full)
        self.filtrar_dados()

    def resetar_datas_hoje(self):
        hoje = date.today().strftime("%d/%m/%Y")
        for e in [self.ent_data_ini, self.ent_data_fim]: e.delete(0, 'end'); e.insert(0, hoje)

    def configurar_cores_tags(self):
        colors = {"SAIDA_VENDA": "#e6b0aa", "ENTRADA_FUNDO": "#abebc6", "ENTRADA_PRODUCAO": "#abebc6", "SAIDA_PRODUCAO": "#fad7a0", "TRANSFERENCIA": "#d7bde2", "PERDA_FUNDO": "#fad7a0"}
        for k, v in colors.items(): self.tree.tag_configure(k, background=v, foreground="black")

    def formatar_numero_inteligente(self, v): return f"{int(v)}" if float(v).is_integer() else f"{v:.3f}".rstrip('0').rstrip('.')
    
    def formatar_data_br(self, s):
        try: return datetime.strptime(str(s).split('.')[0], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S")
        except: return s
    
    def get_data_filtro(self, w):
        try: return datetime.strptime(w.get().strip(), "%d/%m/%Y").date()
        except: return None
    
    def monitorar_eventos_globais(self):
        top = self.winfo_toplevel()
        top.bind("<Button-1>", self.monitorar_cliques, add="+")
        top.bind("<Configure>", lambda e: self.fechar_calendario(), add="+")

    def monitorar_cliques(self, event):
        for d in [self.dropdown_prod, self.dropdown_user, self.dropdown_tipo]:
            if d: d.fechar_lista()
        if self.popup_calendario and self.popup_calendario.winfo_exists():
            if not str(event.widget).startswith(str(self.popup_calendario)): self.fechar_calendario()

    def mostrar_ajuda(self):
        """
        Chama o modal centralizado.
        """
        abrir_ajuda(self.winfo_toplevel(), "historico")