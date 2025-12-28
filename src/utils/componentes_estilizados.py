# src/utils/componentes_estilizados.py
import customtkinter as ctk
from datetime import date, datetime
import calendar

class CTkFloatingDropdown:
    """
    Dropdown flutuante robusto: Navegação (TAB), Busca, e Proteção contra conflitos de foco/clique.
    """
    def __init__(self, entry_widget, data_list, width=200, height=150, command=None):
        self.entry = entry_widget
        self.entry_widget = self.entry._entry
        self.data_list = sorted(data_list)
        self.popup = None
        self.width = width
        self.height = height
        self.command = command 
        self.bloquear_filtro = False 
        self.botoes_itens = []
        self.indice_selecionado = -1
        self.toplevel = self.entry.winfo_toplevel()
        self.last_x = None
        self.last_y = None
        
        # Controle de Timers para evitar conflitos
        self._after_id_abrir = None
        self._after_id_fechar = None

        # --- GESTÃO DE EVENTOS ---
        self.entry.bind("<KeyRelease>", self.ao_digitar)
        self.entry.bind("<Button-1>", self.ao_clicar)
        self.entry.bind("<Down>", self.mover_selecao_baixo)
        self.entry.bind("<Up>", self.mover_selecao_cima)
        self.entry.bind("<Return>", self.selecionar_via_enter)
        self.entry.bind("<Escape>", lambda e: self.fechar_e_limpar_foco())
        
        # FocusIn: Abre via TAB
        self.entry.bind("<FocusIn>", self.agendar_abertura_foco)
        # FocusOut: Fecha ao sair (com delay para permitir clique na lista)
        self.entry.bind("<FocusOut>", self.agendar_fechamento_foco)

        # Monitoramento Global
        self.toplevel.bind_all("<Button-1>", self.monitor_clique_global, add="+")
        self.entry.bind("<Unmap>", lambda e: self.fechar_lista(), add="+")
        self.toplevel.bind("<Unmap>", lambda e: self.fechar_lista(), add="+")
        self.toplevel.bind("<Deactivate>", lambda e: self.fechar_lista())
        self.toplevel.bind("<Configure>", self._reposicionar_popup)

    def agendar_abertura_foco(self, event):
        # Se houver um fechamento pendente, cancela ele (prioriza manter aberto/reabrir)
        if self._after_id_fechar:
            self.entry.after_cancel(self._after_id_fechar)
            self._after_id_fechar = None
            
        if self._after_id_abrir:
            self.entry.after_cancel(self._after_id_abrir)
        self._after_id_abrir = self.entry.after(150, self.ao_focar)

    def ao_focar(self, event=None):
        self._after_id_abrir = None
        # Só abre se não tiver popup já
        if not self.popup:
            self.ao_digitar()

    def agendar_fechamento_foco(self, event):
        # Se houver abertura pendente, não cancelamos imediatamente, 
        # pois o FocusOut acontece antes do clique na lista.
        if self._after_id_fechar:
            self.entry.after_cancel(self._after_id_fechar)
        self._after_id_fechar = self.entry.after(150, self.fechar_lista)

    def _reposicionar_popup(self, event=None):
        if not self.popup or not self.popup.winfo_exists(): return
        try:
            current_x = self.entry.winfo_rootx()
            current_y = self.entry.winfo_rooty() + self.entry.winfo_height() + 2
            if self.last_x is None or abs(current_x - self.last_x) > 3 or abs(current_y - self.last_y) > 3:
                self.last_x, self.last_y = current_x, current_y
                geom = self.popup.winfo_geometry().split('+')[0]
                self.popup.geometry(f"{geom}+{current_x}+{current_y}")
        except: pass

    def monitor_clique_global(self, event):
        try:
            widget_clicado = event.widget
            # Se clicou no próprio Entry, deixa o evento <Button-1> dele cuidar
            if widget_clicado == self.entry_widget: return
            
            # Se clicou DENTRO do popup (na lista), não fecha
            if self.popup and self.popup.winfo_exists():
                if str(widget_clicado).find(str(self.popup)) != -1: return
            
            # Clicou fora: fecha imediatamente
            self.fechar_lista()
        except: pass

    def fechar_e_limpar_foco(self):
        self.fechar_lista()
        self.toplevel.focus_set()

    def fechar_lista(self, event=None):
        # CANCELAMENTO NUCLEAR: Remove qualquer tarefa agendada de abrir ou fechar
        if self._after_id_abrir:
            self.entry.after_cancel(self._after_id_abrir)
            self._after_id_abrir = None
        
        if self._after_id_fechar:
            self.entry.after_cancel(self._after_id_fechar)
            self._after_id_fechar = None

        if self.popup:
            try: self.popup.destroy()
            except: pass
            self.popup, self.botoes_itens, self.indice_selecionado = None, [], -1
            self.last_x, self.last_y = None, None

    def ao_clicar(self, event):
        # Ao clicar, cancela fechamentos pendentes e força abertura
        if self._after_id_fechar:
            self.entry.after_cancel(self._after_id_fechar)
            self._after_id_fechar = None
        self.entry.after(50, self._forcar_abertura)

    def _forcar_abertura(self):
        self.ao_digitar()
        self.entry.focus_set()
        self.entry_widget.focus_set()
        self.entry.icursor("end")

    def mostrar_lista(self, items_filtrados):
        if self.bloquear_filtro or not items_filtrados or not self.entry.winfo_viewable():
            self.fechar_lista(); return
        if self.popup and self.popup.winfo_exists():
            self._desenhar_botoes(items_filtrados); self._reposicionar_popup(); return
        self.popup = ctk.CTkToplevel(self.entry)
        self.popup.wm_overrideredirect(True)
        self.popup.transient(self.toplevel)
        self.scroll_frame = ctk.CTkScrollableFrame(self.popup, width=self.width, height=self.height)
        self.scroll_frame.pack(fill="both", expand=True)
        try:
            x, y = self.entry.winfo_rootx(), self.entry.winfo_rooty() + self.entry.winfo_height() + 2
            altura = min(len(items_filtrados) * 35 + 40, self.height)
            self.popup.geometry(f"{self.width}x{altura}+{x}+{y}")
            self.last_x, self.last_y = x, y
        except: return
        self._desenhar_botoes(items_filtrados)

    def _desenhar_botoes(self, items_filtrados):
        for w in self.scroll_frame.winfo_children(): w.destroy()
        self.botoes_itens = []
        for item in items_filtrados:
            btn = ctk.CTkButton(self.scroll_frame, text=item, anchor="w", fg_color="transparent", 
                               hover_color="#444", height=30, command=lambda i=item: self.selecionar_item(i))
            btn.pack(fill="x"); self.botoes_itens.append(btn)
        self.indice_selecionado = -1

    def ao_digitar(self, event=None):
        if self.bloquear_filtro: return
        if event and event.keysym in ["Down", "Up", "Return", "Escape", "Tab"]: return
        texto = self.entry.get().lower()
        filtrados = [i for i in self.data_list if texto in i.lower()] if texto else self.data_list
        self.mostrar_lista(filtrados)

    def mover_selecao_baixo(self, event):
        if not self.popup or not self.botoes_itens: return
        if self.indice_selecionado < len(self.botoes_itens) - 1:
            self.indice_selecionado += 1; self._atualizar_destaque_teclado()
        return "break"

    def mover_selecao_cima(self, event):
        if not self.popup or not self.botoes_itens: return
        if self.indice_selecionado > 0:
            self.indice_selecionado -= 1; self._atualizar_destaque_teclado()
        return "break"

    def _atualizar_destaque_teclado(self):
        for i, btn in enumerate(self.botoes_itens):
            if i == self.indice_selecionado:
                btn.configure(fg_color="#1f538d")
                if i > 3: self.scroll_frame._parent_canvas.yview_moveto(i / len(self.botoes_itens))
            else: btn.configure(fg_color="transparent")

    def selecionar_via_enter(self, event):
        if self.popup and self.indice_selecionado != -1:
            self.selecionar_item(self.botoes_itens[self.indice_selecionado].cget("text"))
            return "break"

    def selecionar_item(self, item):
        self.bloquear_filtro = True 
        self.entry.delete(0, 'end'); self.entry.insert(0, item); self.fechar_e_limpar_foco()
        if self.command: self.command(item)
        self.entry.after(200, lambda: setattr(self, 'bloquear_filtro', False))

    def atualizar_dados(self, nova_lista): self.data_list = sorted(nova_lista)


class CTkCalendar(ctk.CTkToplevel):
    """
    Calendário flutuante que permite digitação e não fecha sozinho prematuramente.
    """
    def __init__(self, master, entry_widget=None, on_select=None):
        super().__init__(master)
        self.entry = entry_widget
        self.on_select = on_select
        self.toplevel_pai = self.entry.winfo_toplevel() if self.entry else master.winfo_toplevel()
        
        self.selected_date = date.today()
        self.validar_data_do_entry()
            
        self.current_month = self.selected_date.month
        self.current_year = self.selected_date.year
        
        self.wm_overrideredirect(True)
        self.transient(self.toplevel_pai)
        self.configure(fg_color="#2b2b2b")
        
        self.montar_estrutura()
        self.atualizar_calendario()
        self._posicionar()

        self.after(250, self.ativar_monitores_fechamento)
        
        if self.entry:
            self.after(100, lambda: self.entry.focus_set())
            self.entry.bind("<Return>", self.ao_dar_enter, add="+")

    def validar_data_do_entry(self):
        try:
            val = self.entry.get()
            self.selected_date = datetime.strptime(val, "%d/%m/%Y").date()
        except: pass

    def ativar_monitores_fechamento(self):
        self.toplevel_pai.bind("<Button-1>", self.monitor_clique_global, add="+")
        self.bind("<Escape>", lambda e: self.fechar())
        if self.entry:
            self.entry.bind("<FocusOut>", self.ao_perder_foco, add="+")

    def ao_perder_foco(self, event):
        self.after(150, self.fechar)

    def _posicionar(self):
        if self.entry:
            self.update_idletasks()
            x = self.entry.winfo_rootx()
            y = self.entry.winfo_rooty() + self.entry.winfo_height() + 2
            self.geometry(f"+{x}+{y}")

    def monitor_clique_global(self, event):
        try:
            widget_clicado = event.widget
            s_entry = str(self.entry)
            s_widget = str(widget_clicado)
            
            if s_widget == s_entry or s_widget == str(self.entry._entry) or s_entry in s_widget:
                return
            if str(self) in s_widget:
                return
            self.fechar()
        except: pass

    def ao_digitar_data(self, event=None):
        texto = self.entry.get()
        if len(texto) == 10:
            try:
                nova_data = datetime.strptime(texto, "%d/%m/%Y").date()
                self.selected_date = nova_data
                self.current_month = nova_data.month
                self.current_year = nova_data.year
                self.atualizar_calendario()
            except: pass

    def ao_dar_enter(self, event):
        self.validar_data_do_entry()
        if self.on_select: self.on_select(self.entry.get())
        self.fechar()

    def fechar(self):
        try:
            self.toplevel_pai.unbind("<Button-1>")
            if self.entry:
                self.entry.unbind("<Return>")
        except: pass
        self.destroy()

    def montar_estrutura(self):
        header = ctk.CTkFrame(self, fg_color="#2980B9", corner_radius=0, height=35)
        header.pack(fill="x")
        
        btn_config = {"width": 30, "fg_color": "transparent", "hover_color": "#1f5f8b"}
        ctk.CTkButton(header, text="<<", command=lambda: self.mudar_ano(-1), **btn_config).pack(side="left", padx=2)
        ctk.CTkButton(header, text="<", command=lambda: self.mudar_mes(-1), **btn_config).pack(side="left", padx=2)
        
        self.lbl_mes_ano = ctk.CTkLabel(header, text="", font=("Arial", 12, "bold"), text_color="white")
        self.lbl_mes_ano.pack(side="left", expand=True)

        ctk.CTkButton(header, text=">", command=lambda: self.mudar_mes(1), **btn_config).pack(side="right", padx=2)
        ctk.CTkButton(header, text=">>", command=lambda: self.mudar_ano(1), **btn_config).pack(side="right", padx=2)

        dias_frame = ctk.CTkFrame(self, fg_color="transparent")
        dias_frame.pack(fill="x", padx=8, pady=(5, 0))
        dias = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
        for d in dias:
            cor = "#2CC985" if d in ["Dom", "Sáb"] else "#ccc"
            ctk.CTkLabel(dias_frame, text=d, width=30, font=("Arial", 9, "bold"), text_color=cor).pack(side="left", expand=True)

        self.corpo_cal = ctk.CTkFrame(self, fg_color="transparent")
        self.corpo_cal.pack(fill="both", expand=True, padx=8, pady=5)

    def atualizar_calendario(self):
        for w in self.corpo_cal.winfo_children(): w.destroy()
        
        meses = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                 "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.lbl_mes_ano.configure(text=f"{meses[self.current_month]} {self.current_year}")

        cal = calendar.monthcalendar(self.current_year, self.current_month)
        for r, semana in enumerate(cal):
            for c, dia in enumerate(semana):
                if dia == 0: 
                    ctk.CTkLabel(self.corpo_cal, text="", width=30).grid(row=r, column=c)
                    continue
                
                dt = date(self.current_year, self.current_month, dia)
                is_selected = dt == self.selected_date
                is_today = dt == date.today()
                
                bg_color = "#27AE60" if is_selected else ("#2CC985" if is_today else ("#3a3a3a" if c in [0,6] else "#333"))
                fg_color = "white" if (is_selected or is_today) else "#ddd"
                
                btn = ctk.CTkButton(self.corpo_cal, text=str(dia), width=30, height=25, 
                                    fg_color=bg_color, hover_color="#1a9966", text_color=fg_color,
                                    command=lambda d=dia: self.selecionar_data(d))
                btn.grid(row=r, column=c, padx=2, pady=2)

    def mudar_mes(self, delta):
        self.current_month += delta
        if self.current_month > 12:
            self.current_month = 1; self.current_year += 1
        elif self.current_month < 1:
            self.current_month = 12; self.current_year -= 1
        self.atualizar_calendario()

    def mudar_ano(self, delta):
        self.current_year += delta
        self.atualizar_calendario()

    def selecionar_data(self, dia):
        data_sel = date(self.current_year, self.current_month, dia)
        if self.on_select:
            self.on_select(data_sel.strftime("%d/%m/%Y"))
        self.fechar()

# -------------------------------------------------------------------------
#  FUNÇÃO UTILITÁRIA GLOBAL
# -------------------------------------------------------------------------

def aplicar_mascara_data(event, entry):
    """
    Formata o campo de data (DD/MM/AAAA) enquanto o usuário digita.
    """
    if event.keysym in ["Return", "Escape", "Tab", "Up", "Down", "Left", "Right", "BackSpace", "Delete"]:
        return

    texto = entry.get()
    numeros = "".join(filter(str.isdigit, texto))
    numeros = numeros[:8]
    
    novo_texto = ""
    if len(numeros) > 2:
        novo_texto += numeros[:2] + "/"
        if len(numeros) > 4:
            novo_texto += numeros[2:4] + "/" + numeros[4:]
        else:
            novo_texto += numeros[2:]
    else:
        novo_texto = numeros

    if texto != novo_texto:
        entry.delete(0, "end")
        entry.insert(0, novo_texto)