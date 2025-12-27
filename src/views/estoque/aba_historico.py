# src/views/estoque/aba_historico.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, date
import calendar
from src.models import database

# --- COMPONENTE: CALENDÁRIO FLUTUANTE ---
class CTkCalendar(ctk.CTkFrame):
    def __init__(self, master, start_date=None, on_select=None, fg_color=None):
        super().__init__(master, fg_color=fg_color or "#2b2b2b", corner_radius=0)
        self.on_select = on_select
        self.selected_date = start_date or date.today()
        self.current_month = self.selected_date.month
        self.current_year = self.selected_date.year
        
        self.montar_estrutura()
        self.atualizar_calendario()

    def montar_estrutura(self):
        header = ctk.CTkFrame(self, fg_color="#2980B9", corner_radius=0, height=35)
        header.pack(fill="x")

        # Navegação
        ctk.CTkButton(header, text="<<", width=25, height=30, fg_color="transparent", hover_color="#1F618D", 
                      command=lambda: self.mudar_ano(-1)).pack(side="left", padx=1)
        ctk.CTkButton(header, text="<", width=25, height=30, fg_color="transparent", hover_color="#1F618D", 
                      command=lambda: self.mudar_mes(-1)).pack(side="left", padx=1)

        self.lbl_mes_ano = ctk.CTkLabel(header, text="Mês Ano", font=("Arial", 13, "bold"), text_color="white")
        self.lbl_mes_ano.pack(side="left", expand=True)

        ctk.CTkButton(header, text=">>", width=25, height=30, fg_color="transparent", hover_color="#1F618D", 
                      command=lambda: self.mudar_ano(1)).pack(side="right", padx=1)
        ctk.CTkButton(header, text=">", width=25, height=30, fg_color="transparent", hover_color="#1F618D", 
                      command=lambda: self.mudar_mes(1)).pack(side="right", padx=1)

        # Dias da Semana
        dias_frame = ctk.CTkFrame(self, fg_color="#333", corner_radius=0, height=25)
        dias_frame.pack(fill="x")
        for d in ["D", "S", "T", "Q", "Q", "S", "S"]:
            ctk.CTkLabel(dias_frame, text=d, width=38, height=25, font=("Arial", 11, "bold"), text_color="#ccc").pack(side="left", padx=1)

        self.grid_dias = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_dias.pack(fill="both", expand=True, pady=5, padx=5)

    def mudar_mes(self, direcao):
        self.current_month += direcao
        if self.current_month > 12:
            self.current_month = 1; self.current_year += 1
        elif self.current_month < 1:
            self.current_month = 12; self.current_year -= 1
        self.atualizar_calendario()

    def mudar_ano(self, direcao):
        self.current_year += direcao
        self.atualizar_calendario()

    def atualizar_calendario(self):
        for widget in self.grid_dias.winfo_children(): widget.destroy()

        meses_pt = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.lbl_mes_ano.configure(text=f"{meses_pt[self.current_month]} {self.current_year}")

        cal = calendar.monthcalendar(self.current_year, self.current_month)
        
        for semana in cal:
            frame_row = ctk.CTkFrame(self.grid_dias, fg_color="transparent")
            frame_row.pack(fill="x")
            for dia in semana:
                if dia == 0:
                    ctk.CTkLabel(frame_row, text="", width=38, height=30).pack(side="left", padx=1, pady=1)
                else:
                    is_hoje = (dia == date.today().day and self.current_month == date.today().month and self.current_year == date.today().year)
                    is_sel = (dia == self.selected_date.day and self.current_month == self.selected_date.month and self.current_year == self.selected_date.year)
                    
                    cor_fg = "#2980B9" if is_sel else "transparent"
                    borda_cor = "#2980B9" if is_hoje else None
                    borda_w = 1 if is_hoje else 0

                    btn = ctk.CTkButton(frame_row, text=str(dia), width=38, height=30, 
                                        fg_color=cor_fg, hover_color="#444", 
                                        border_color=borda_cor, border_width=borda_w,
                                        command=lambda d=dia: self.selecionar_dia(d))
                    btn.pack(side="left", padx=1, pady=1)

    def selecionar_dia(self, dia):
        data = date(self.current_year, self.current_month, dia)
        self.selected_date = data
        self.atualizar_calendario()
        if self.on_select: self.on_select(data)

# --- COMPONENTE: LISTA FLUTUANTE DE PESQUISA ---
class CTkFloatingDropdown:
    def __init__(self, entry_widget, data_list, width=200, height=200):
        self.entry = entry_widget
        self.data_list = data_list
        self.popup = None
        self.width = width
        self.height = height
        
        self.items_buttons = []
        self.current_selection_index = -1

        # Bindings
        self.entry.bind("<KeyRelease>", self.ao_digitar)
        self.entry.bind("<FocusIn>", self.ao_focar)
        self.entry.bind("<Down>", self.mover_selecao_baixo)
        self.entry.bind("<Up>", self.mover_selecao_cima)
        self.entry.bind("<Return>", self.selecionar_via_enter)
        self.entry.bind("<Tab>", self.fechar_lista)

    def mostrar_lista(self, items_filtrados):
        self.current_selection_index = -1
        if not items_filtrados:
            self.fechar_lista()
            return

        if self.popup is None or not self.popup.winfo_exists():
            self.popup = ctk.CTkToplevel(self.entry)
            self.popup.wm_overrideredirect(True)
            self.popup.attributes("-topmost", True)
            
            self.scroll_frame = ctk.CTkScrollableFrame(self.popup, width=self.width, height=self.height)
            self.scroll_frame.pack(fill="both", expand=True)

        try:
            x = self.entry.winfo_rootx()
            y = self.entry.winfo_rooty() + self.entry.winfo_height() + 2
            self.popup.geometry(f"{self.width}x{min(len(items_filtrados)*35 + 10, self.height)}+{x}+{y}")
        except: return

        for w in self.scroll_frame.winfo_children(): w.destroy()
        self.items_buttons = []

        for item in items_filtrados:
            btn = ctk.CTkButton(self.scroll_frame, text=item, anchor="w", fg_color="transparent", 
                                hover_color="#444", height=30,
                                command=lambda i=item: self.selecionar_item(i))
            btn.pack(fill="x")
            self.items_buttons.append(btn)

    def fechar_lista(self, event=None):
        if self.popup:
            self.popup.destroy()
            self.popup = None
            self.items_buttons = []

    def ao_digitar(self, event):
        if event.keysym in ["Down", "Up", "Return", "Tab", "Escape"]: return
        texto = self.entry.get().lower()
        filtrados = [i for i in self.data_list if texto in i.lower()]
        self.mostrar_lista(filtrados)

    def ao_focar(self, event):
        self.ao_digitar(event)

    def selecionar_item(self, item):
        self.entry.delete(0, 'end')
        self.entry.insert(0, item)
        self.fechar_lista()

    def atualizar_dados(self, nova_lista):
        self.data_list = nova_lista

    def mover_selecao_baixo(self, event):
        if not self.popup: self.ao_digitar(event); return
        if self.current_selection_index < len(self.items_buttons) - 1:
            self.current_selection_index += 1
            self.atualizar_destaque()

    def mover_selecao_cima(self, event):
        if not self.popup: return
        if self.current_selection_index > 0:
            self.current_selection_index -= 1
            self.atualizar_destaque()

    def atualizar_destaque(self):
        for idx, btn in enumerate(self.items_buttons):
            btn.configure(fg_color="#2980B9" if idx == self.current_selection_index else "transparent")

    def selecionar_via_enter(self, event):
        if self.popup and self.items_buttons and self.current_selection_index >= 0:
            self.selecionar_item(self.items_buttons[self.current_selection_index].cget("text"))
            return "break"


# --- CLASSE PRINCIPAL DA ABA ---
class AbaHistorico(ctk.CTkFrame):
    def __init__(self, master, produtos_ref, callback_atualizar):
        super().__init__(master)
        self.produtos = produtos_ref 
        self.callback_atualizar = callback_atualizar
        
        self.janela_ajuda = None
        self.popup_calendario = None 
        
        # Drops
        self.dropdown_prod = None    
        self.dropdown_user = None
        self.dropdown_tipo = None
        
        # VARIÁVEIS DE ORDENAÇÃO
        # sort_col: 'data', 'tipo', 'produto', etc.
        # sort_dir: 'asc' (▲), 'desc' (▼), 'original' (▲▼)
        self.sort_col = None
        self.sort_dir = "original"
        
        # Dados Iniciais
        self.lista_produtos_full = sorted([p['nome'] for p in self.produtos.values()])
        self.lista_usuarios_full = self.carregar_lista_usuarios()
        self.lista_tipos = ["TODOS", "VENDA", "ENTRADA", "PRODUCAO", "TRANSFERENCIA", "PERDA"]

        self.montar_layout()
        self.monitorar_janela_principal()
        self.resetar_datas_hoje()
        self.filtrar_dados() 

    def monitorar_janela_principal(self):
        root = self.winfo_toplevel()
        root.bind("<Configure>", self.ao_mover_janela)
        root.bind("<Unmap>", self.fechar_todos_popups_evento)
        root.bind("<Button-1>", self.ao_clicar_janela)

    def ao_mover_janela(self, event):
        if event.widget == self.winfo_toplevel(): self.fechar_todos_popups()

    def ao_clicar_janela(self, event):
        if self.popup_calendario:
            try:
                if str(event.widget).find(str(self.popup_calendario)) == -1: 
                    if "button" not in str(event.widget): 
                        self.fechar_todos_popups()
            except: self.fechar_todos_popups()
        
        if self.dropdown_prod: self.dropdown_prod.fechar_lista()
        if self.dropdown_user: self.dropdown_user.fechar_lista()
        if self.dropdown_tipo: self.dropdown_tipo.fechar_lista()

    def fechar_todos_popups_evento(self, event): self.fechar_todos_popups()

    def fechar_todos_popups(self):
        if self.popup_calendario: 
            self.popup_calendario.destroy()
            self.popup_calendario = None
        
        if self.dropdown_prod: self.dropdown_prod.fechar_lista()
        if self.dropdown_user: self.dropdown_user.fechar_lista()
        if self.dropdown_tipo: self.dropdown_tipo.fechar_lista()

    def resetar_datas_hoje(self):
        hoje = date.today().strftime("%d/%m/%Y")
        self.ent_data_ini.delete(0, 'end'); self.ent_data_ini.insert(0, hoje)
        self.ent_data_fim.delete(0, 'end'); self.ent_data_fim.insert(0, hoje)

    def carregar_lista_usuarios(self):
        try:
            movs = database.carregar_json(database.ARQ_MOVIMENTOS)
            usuarios = set()
            for m in movs:
                u = m.get('usuario')
                if u: usuarios.add(u)
            return sorted(list(usuarios)) if usuarios else ["Admin"]
        except: return ["Admin"]

    def montar_layout(self):
        # HEADER
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        ctk.CTkLabel(header_frame, text="Extrato Completo", font=("Arial", 14, "bold")).pack(side="left", padx=10)
        ctk.CTkButton(header_frame, text="?", width=30, fg_color="#2980B9", hover_color="#1F618D",
                      command=self.mostrar_ajuda).pack(side="left", padx=5)

        # FILTROS
        self.frame_filtros = ctk.CTkFrame(self, border_width=1, border_color="#444", height=50)
        self.frame_filtros.pack(fill="x", padx=10, pady=5)
        row = ctk.CTkFrame(self.frame_filtros, fg_color="transparent")
        row.pack(fill="x", padx=5, pady=8)

        # --- DATAS ---
        self.criar_campo_data(row, "De:", "ent_data_ini")
        self.criar_campo_data(row, "Até:", "ent_data_fim")

        # --- TIPO ---
        ctk.CTkLabel(row, text="Tipo:", text_color="#ccc", font=("Arial", 11)).pack(side="left", padx=(10, 2))
        self.ent_tipo = ctk.CTkEntry(row, width=120, placeholder_text="Selecione...")
        self.ent_tipo.pack(side="left", padx=2)
        self.dropdown_tipo = CTkFloatingDropdown(self.ent_tipo, self.lista_tipos, width=150)

        # --- PRODUTO ---
        ctk.CTkLabel(row, text="Prod:", text_color="#ccc", font=("Arial", 11)).pack(side="left", padx=(10, 2))
        self.ent_prod = ctk.CTkEntry(row, width=140, placeholder_text="Digite...")
        self.ent_prod.pack(side="left", padx=2)
        self.dropdown_prod = CTkFloatingDropdown(self.ent_prod, self.lista_produtos_full, width=250)

        # --- USUÁRIO ---
        ctk.CTkLabel(row, text="User:", text_color="#ccc", font=("Arial", 11)).pack(side="left", padx=(10, 2))
        self.ent_user = ctk.CTkEntry(row, width=90, placeholder_text="Nome...")
        self.ent_user.pack(side="left", padx=2)
        self.dropdown_user = CTkFloatingDropdown(self.ent_user, self.lista_usuarios_full, width=150)

        # BOTÕES
        ctk.CTkButton(row, text="🔎", width=40, font=("Arial", 22), fg_color="#27AE60", command=self.aplicar_filtro).pack(side="left", padx=(15, 5))
        ctk.CTkButton(row, text="🧹", width=40, font=("Arial", 22), fg_color="#7f8c8d", command=self.limpar_filtros).pack(side="left", padx=5)

        # TABELA
        table_container = ctk.CTkFrame(self, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.cols = ("data", "tipo", "produto", "qtd", "valor", "usuario", "motivo")
        self.tree = ttk.Treeview(table_container, columns=self.cols, show="headings")
        
        self.configurar_colunas_inicial()
        
        scroll = ctk.CTkScrollbar(table_container, command=self.tree.yview)
        self.tree.configure(yscroll=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        
        self.configurar_cores_tags()

    def criar_campo_data(self, parent, label, attr_name):
        ctk.CTkLabel(parent, text=label, text_color="#ccc", font=("Arial", 11)).pack(side="left", padx=(5, 2))
        entry = ctk.CTkEntry(parent, width=90, placeholder_text="DD/MM/AAAA")
        entry.pack(side="left", padx=2)
        entry.bind("<KeyRelease>", self.formatar_data_ao_digitar)
        setattr(self, attr_name, entry)
        
        btn = ctk.CTkButton(parent, text="📅", width=30, fg_color="#444", hover_color="#555",
                            command=lambda: self.abrir_calendario_dropdown(entry, btn))
        btn.pack(side="left", padx=2)

    def formatar_data_ao_digitar(self, event):
        if event.keysym.lower() in ['backspace', 'delete']: return
        widget = event.widget
        texto = widget.get()
        if len(texto) == 2: widget.insert(2, "/")
        elif len(texto) == 5: widget.insert(5, "/")
        elif len(texto) > 10: widget.delete(10, 'end')

    def abrir_calendario_dropdown(self, entry_widget, button_widget):
        self.fechar_todos_popups()
        
        self.popup_calendario = ctk.CTkToplevel(self)
        self.popup_calendario.wm_overrideredirect(True)
        self.popup_calendario.attributes("-topmost", True)
        
        x = button_widget.winfo_rootx() - 250
        y = button_widget.winfo_rooty() + 35
        self.popup_calendario.geometry(f"290x290+{x}+{y}")

        def ao_selecionar(data_obj):
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, data_obj.strftime("%d/%m/%Y"))
            self.fechar_todos_popups()

        cal = CTkCalendar(self.popup_calendario, on_select=ao_selecionar)
        cal.pack(fill="both", expand=True, padx=2, pady=2)
        
        ctk.CTkButton(self.popup_calendario, text="Fechar", height=20, fg_color="#333", 
                      command=self.fechar_todos_popups).pack(fill="x")
        
        self.popup_calendario.focus_force()

    def configurar_colunas_inicial(self):
        # Mapeamento Título -> ID Coluna
        titulos = {
            "data": "DATA/HORA",
            "tipo": "TIPO",
            "produto": "PRODUTO",
            "qtd": "QTD",
            "valor": "VALOR (R$)",
            "usuario": "USUÁRIO",
            "motivo": "MOTIVO"
        }
        
        for col, titulo in titulos.items():
            # Define o texto inicial com o ícone neutro ▲▼
            self.tree.heading(col, text=f"{titulo} ▲▼", command=lambda c=col: self.ordenar_coluna(c))
            self.tree.column(col, anchor="center")
        
        self.tree.column("data", width=140); self.tree.column("produto", width=220)
        self.tree.column("motivo", width=250)

    def ordenar_coluna(self, col):
        """Alterna a ordenação: Original -> Asc -> Desc -> Original"""
        
        # Se clicou na mesma coluna
        if self.sort_col == col:
            if self.sort_dir == "original":
                self.sort_dir = "asc"
            elif self.sort_dir == "asc":
                self.sort_dir = "desc"
            else:
                self.sort_dir = "original"
                self.sort_col = None
        # Se clicou em outra coluna
        else:
            self.sort_col = col
            self.sort_dir = "asc"

        self.atualizar_cabecalhos_icones()
        self.filtrar_dados() # Re-renderiza com a nova ordem

    def atualizar_cabecalhos_icones(self):
        titulos = {
            "data": "DATA/HORA", "tipo": "TIPO", "produto": "PRODUTO",
            "qtd": "QTD", "valor": "VALOR (R$)", "usuario": "USUÁRIO", "motivo": "MOTIVO"
        }
        
        for col, texto_base in titulos.items():
            icone = " ▲▼" # Padrão neutro
            
            if col == self.sort_col:
                if self.sort_dir == "asc": icone = " ▲"
                elif self.sort_dir == "desc": icone = " ▼"
            
            self.tree.heading(col, text=f"{texto_base}{icone}")

    def configurar_cores_tags(self):
        colors = {"SAIDA_VENDA": "#e6b0aa", "ENTRADA_FUNDO": "#abebc6", "ENTRADA_PRODUCAO": "#abebc6",
                  "SAIDA_PRODUCAO": "#fad7a0", "TRANSFERENCIA": "#d7bde2", "PERDA_FUNDO": "#fad7a0"}
        for k, v in colors.items(): self.tree.tag_configure(k, background=v, foreground="black")

    def formatar_numero_inteligente(self, valor):
        if float(valor).is_integer(): return f"{int(valor)}"
        return f"{valor:.3f}".rstrip('0').rstrip('.')

    def formatar_data_br(self, data_str):
        if not data_str: return "-"
        try:
            dt = datetime.strptime(str(data_str).split('.')[0], "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%d/%m/%Y %H:%M:%S")
        except: return data_str

    def get_data_filtro(self, widget):
        val = widget.get().strip()
        if not val: return None
        try: return datetime.strptime(val, "%d/%m/%Y").date()
        except: return None

    def filtrar_dados(self):
        # 1. Limpa tabela
        for i in self.tree.get_children(): self.tree.delete(i)
        
        try: 
            # Inverte para pegar do mais recente pro mais antigo por padrão (Original)
            todos_movs = database.carregar_json(database.ARQ_MOVIMENTOS)[::-1]
        except: 
            todos_movs = []

        f_ini = self.get_data_filtro(self.ent_data_ini)
        f_fim = self.get_data_filtro(self.ent_data_fim)
        
        f_tipo = self.ent_tipo.get().strip().upper()
        if not f_tipo: f_tipo = "TODOS"
        
        f_prod = self.ent_prod.get().strip().lower() 
        f_user = self.ent_user.get().strip().lower() 

        # Lista temporária para processar os dados ANTES de inserir
        linhas_processadas = []

        for m in todos_movs:
            # -- Lógica de Filtro --
            data_raw = m.get('data', '')
            try: dt_mov = datetime.strptime(data_raw.split()[0], "%Y-%m-%d").date()
            except: dt_mov = None
            
            if f_ini and dt_mov and dt_mov < f_ini: continue
            if f_fim and dt_mov and dt_mov > f_fim: continue
            if f_tipo != "TODOS" and f_tipo not in m.get('tipo', ''): continue
            if f_prod and f_prod not in m.get('nome', '').lower(): continue
            if f_user and f_user not in m.get('usuario', '').lower(): continue

            # -- Preparação dos Dados para Exibição e Ordenação --
            cod_prod = str(m.get('cod'))
            p = self.produtos.get(cod_prod, {})
            un = p.get('unidade', 'UN')
            qtd = float(m.get('qtd', 0))
            
            # Cálculo de Valor e Preço Base
            is_insumo = p.get('tipo') == 'INSUMO'
            usar_custo = is_insumo or 'PRODUCAO' in m.get('tipo', '') or 'ENTRADA' in m.get('tipo', '')
            base_calc = p.get('custo', 0.0) if usar_custo else p.get('preco', 0.0)
            valor_total = abs(qtd) * base_calc

            # Formatação Visual
            qtd_fmt = f"{self.formatar_numero_inteligente(qtd)} {un}"
            data_fmt = self.formatar_data_br(m.get('data'))
            val_fmt = f"R$ {valor_total:.2f}"

            # Objeto para Ordenação
            linha_obj = {
                'display': (data_fmt, m.get('tipo'), m.get('nome'), qtd_fmt, val_fmt, m.get('usuario'), m.get('motivo')),
                'tags': (m.get('tipo'),),
                # Valores crus para ordenação correta
                'sort_data': data_raw, # String ISO ordena corretamente cronologicamente
                'sort_tipo': m.get('tipo', ''),
                'sort_produto': m.get('nome', '').lower(),
                'sort_qtd': qtd,
                'sort_valor': valor_total,
                'sort_usuario': m.get('usuario', '').lower(),
                'sort_motivo': m.get('motivo', '').lower()
            }
            linhas_processadas.append(linha_obj)

        # -- Lógica de Ordenação --
        if self.sort_dir != "original" and self.sort_col:
            reverse = (self.sort_dir == "desc")
            
            # Mapeia o nome da coluna da tabela para a chave de ordenação
            key_map = {
                "data": "sort_data",
                "tipo": "sort_tipo",
                "produto": "sort_produto",
                "qtd": "sort_qtd",
                "valor": "sort_valor",
                "usuario": "sort_usuario",
                "motivo": "sort_motivo"
            }
            
            sort_key = key_map.get(self.sort_col)
            if sort_key:
                linhas_processadas.sort(key=lambda x: x[sort_key], reverse=reverse)

        # -- Inserção na Tabela --
        for item in linhas_processadas:
            self.tree.insert("", "end", values=item['display'], tags=item['tags'])

    def aplicar_filtro(self): self.filtrar_dados()
    
    def limpar_filtros(self):
        self.resetar_datas_hoje()
        self.ent_prod.delete(0, 'end')
        self.ent_user.delete(0, 'end')
        self.ent_tipo.delete(0, 'end') 
        
        # Reseta ordenação ao limpar
        self.sort_col = None
        self.sort_dir = "original"
        self.atualizar_cabecalhos_icones()
        
        self.filtrar_dados()
    
    def atualizar(self):
        self.lista_produtos_full = sorted([p['nome'] for p in self.produtos.values()])
        self.dropdown_prod.atualizar_dados(self.lista_produtos_full)
        self.lista_usuarios_full = self.carregar_lista_usuarios()
        self.dropdown_user.atualizar_dados(self.lista_usuarios_full)
        self.filtrar_dados()

    def mostrar_ajuda(self):
        if self.janela_ajuda and self.janela_ajuda.winfo_exists():
            self.janela_ajuda.lift(); self.janela_ajuda.focus_force(); return
        
        self.janela_ajuda = ctk.CTkToplevel(self)
        self.janela_ajuda.title("Ajuda Estoque")
        self.janela_ajuda.geometry("500x600")
        self.janela_ajuda.transient(self)
        self.janela_ajuda.lift()
        self.janela_ajuda.focus_force()
        
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
        linha_legenda("#abebc6", "ENTRADA", "Compra, Produção ou Ajuste.")
        linha_legenda("#fad7a0", "SAÍDA PROD/PERDA", "Insumo usado ou perda.")
        linha_legenda("#d7bde2", "TRANSFERÊNCIA", "Movimento Fundo -> Frente.")
        
        frame_regras = ctk.CTkFrame(self.janela_ajuda)
        frame_regras.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(frame_regras, text="ℹ️ DICAS DE USO", font=("Arial", 14, "bold")).pack(pady=10)
        texto_regras = """
1. ORDENAÇÃO (NOVO!):
• Clique no topo de qualquer coluna.
• 1º Clique: Ordena Crescente (▲).
• 2º Clique: Ordena Decrescente (▼).
• 3º Clique: Volta ao original (▲▼).

2. CALENDÁRIO & FILTROS:
• Use os filtros para refinar a busca.
• Deixe os campos vazios para ver tudo.
"""
        lbl_regras = ctk.CTkLabel(frame_regras, text=texto_regras, justify="left", anchor="nw", padx=10, font=("Consolas", 12))
        lbl_regras.pack(fill="both", expand=True)