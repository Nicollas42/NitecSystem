# src/utils/componentes_estilizados.py
import customtkinter as ctk
from datetime import date, datetime
import calendar

class CTkFloatingDropdown:
    """
    Dropdown flutuante com busca inteligente para CustomTkinter.
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

        self.entry.bind("<KeyRelease>", self.ao_digitar)
        self.entry.bind("<FocusIn>", self.ao_focar)
        self.entry.bind("<Button-1>", self.ao_clicar)
        self.entry.bind("<Down>", self.mover_selecao_baixo)
        self.entry.bind("<Up>", self.mover_selecao_cima)
        self.entry.bind("<Return>", self.selecionar_via_enter)
        self.entry.bind("<Escape>", lambda e: self.fechar_e_limpar_foco())

        self.toplevel.bind_all("<Button-1>", self.monitor_clique_global, add="+")
        self.entry.bind("<Unmap>", lambda e: self.fechar_lista(), add="+")
        self.toplevel.bind("<Unmap>", lambda e: self.fechar_lista(), add="+")
        self.toplevel.bind("<Deactivate>", lambda e: self.fechar_lista())
        self.toplevel.bind("<FocusOut>", lambda e: self.fechar_lista())
        self.toplevel.bind("<Configure>", self._reposicionar_popup)

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
            if widget_clicado == self.entry_widget: return
            if self.popup and self.popup.winfo_exists():
                if str(widget_clicado).find(str(self.popup)) != -1: return
            if self.popup: self.fechar_lista()
            if self.toplevel.focus_get() == self.entry_widget: self.toplevel.focus_set()
        except: pass

    def fechar_e_limpar_foco(self):
        self.fechar_lista()
        self.toplevel.focus_set()

    def fechar_lista(self, event=None):
        if self.popup:
            try: self.popup.destroy()
            except: pass
            self.popup, self.botoes_itens, self.indice_selecionado = None, [], -1
            self.last_x, self.last_y = None, None

    def ao_focar(self, event):
        if not self.entry.winfo_viewable(): return
        self.ao_digitar(); self.entry.focus_set(); self.entry.icursor("end")

    def ao_clicar(self, event):
        self.fechar_lista()
        self.entry.after(50, self._forcar_abertura)

    def _forcar_abertura(self):
        self.ao_digitar(); self.entry.focus_set(); self.entry_widget.focus_set(); self.entry.icursor("end")

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
        if event and event.keysym in ["Down", "Up", "Return", "Escape"]: return
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
    Calendário flutuante customizado para seleção de datas.
    """
    def __init__(self, master, entry_widget=None, on_select=None):
        super().__init__(master)
        self.entry = entry_widget
        self.on_select = on_select
        self.selected_date = date.today()
        self.current_month = self.selected_date.month
        self.current_year = self.selected_date.year
        
        # Configuração da janela popup
        self.wm_overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color="#2b2b2b")

        self.montar_estrutura()
        self.atualizar_calendario()
        self._posicionar()

        # Fecha ao perder foco
        self.bind("<FocusOut>", lambda e: self.destroy() if e.widget != self else None)

    def _posicionar(self):
        if self.entry:
            self.update_idletasks()
            x = self.entry.winfo_rootx()
            y = self.entry.winfo_rooty() + self.entry.winfo_height() + 2
            self.geometry(f"+{x}+{y}")

    def montar_estrutura(self):
        # Cabeçalho azul original
        header = ctk.CTkFrame(self, fg_color="#2980B9", corner_radius=0, height=35)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Botões esquerda
        ctk.CTkButton(header, text="<<", width=30, fg_color="transparent", hover_color="#1f5f8b",
                      command=lambda: self.mudar_ano(-1)).pack(side="left", padx=5)
        ctk.CTkButton(header, text="<", width=30, fg_color="transparent", hover_color="#1f5f8b",
                      command=lambda: self.mudar_mes(-1)).pack(side="left", padx=2)

        # Mês e ano centralizado
        self.lbl_mes_ano = ctk.CTkLabel(header, text="", font=("Arial", 12, "bold"), text_color="white")
        self.lbl_mes_ano.pack(side="left", expand=True)

        # Botões direita
        ctk.CTkButton(header, text=">", width=30, fg_color="transparent", hover_color="#1f5f8b",
                      command=lambda: self.mudar_mes(1)).pack(side="right", padx=2)
        ctk.CTkButton(header, text=">>", width=30, fg_color="transparent", hover_color="#1f5f8b",
                      command=lambda: self.mudar_ano(1)).pack(side="right", padx=5)

        # Dias da semana
        dias_frame = ctk.CTkFrame(self, fg_color="transparent")
        dias_frame.pack(fill="x", padx=8, pady=(8, 4))
        dias_semana = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
        for dia in dias_semana:
            cor = "#2CC985" if dia in ["Dom", "Sáb"] else "#cccccc"
            ctk.CTkLabel(dias_frame, text=dia, width=30, font=("Arial", 10, "bold"),
                         text_color=cor).pack(side="left", expand=True)

        # Corpo do calendário
        self.corpo_cal = ctk.CTkFrame(self, fg_color="transparent")
        self.corpo_cal.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def atualizar_calendario(self):
        for widget in self.corpo_cal.winfo_children():
            widget.destroy()

        meses_pt = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.lbl_mes_ano.configure(text=f"{meses_pt[self.current_month]} {self.current_year}")

        cal = calendar.monthcalendar(self.current_year, self.current_month)

        for linha, semana in enumerate(cal):
            for col, dia in enumerate(semana):
                if dia == 0:
                    ctk.CTkLabel(self.corpo_cal, text="").grid(row=linha, column=col)
                    continue

                data_atual = date(self.current_year, self.current_month, dia)
                is_hoje = data_atual == date.today()
                is_fds = col in (0, 6)  # Dom ou Sáb

                if is_hoje:
                    bg = "#2CC985"
                    hover = "#1a9966"
                    texto = "white"
                elif is_fds:
                    bg = "#3a3a3a"      # cinza mais claro para finais de semana
                    hover = "#454545"
                    texto = "#dddddd"
                else:
                    bg = "#333333"
                    hover = "#3d3d3d"
                    texto = "#ffffff"

                btn = ctk.CTkButton(
                    self.corpo_cal,
                    text=str(dia),
                    width=30,
                    height=30,
                    corner_radius=8,
                    fg_color=bg,
                    hover_color=hover,
                    text_color=texto,
                    font=("Arial", 11),
                    command=lambda d=dia: self.selecionar_data(d)
                )
                btn.grid(row=linha, column=col, padx=2, pady=2)

    def mudar_mes(self, delta):
        self.current_month += delta
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        elif self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self.atualizar_calendario()

    def mudar_ano(self, delta):
        self.current_year += delta
        self.atualizar_calendario()

    def selecionar_data(self, dia):
        data_sel = date(self.current_year, self.current_month, dia)
        if self.on_select:
            self.on_select(data_sel.strftime("%d/%m/%Y"))
        self.destroy()