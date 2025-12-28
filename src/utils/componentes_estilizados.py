# src/utils/componentes_estilizados.py
import customtkinter as ctk
from datetime import date, datetime
import calendar


class CTkFloatingDropdown:
    """
    Dropdown flutuante com busca inteligente para CustomTkinter.
    Comportamento profissional completo:
    - Abre ao clicar/foco
    - Fecha ao clicar fora, Alt+Tab ou mudar de janela
    - Reabre perfeitamente ao voltar e clicar
    - Acompanha a janela ao arrastar
    - Cursor visível no primeiro clique
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

        # Última posição conhecida (para acompanhar movimento da janela)
        self.last_x = None
        self.last_y = None

        # Bindings
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

        # Fecha ao perder foco/ativação da janela
        self.toplevel.bind("<Deactivate>", lambda e: self.fechar_lista())
        self.toplevel.bind("<FocusOut>", lambda e: self.fechar_lista())

        # Acompanha movimento da janela
        self.toplevel.bind("<Configure>", self._reposicionar_popup)

    def _reposicionar_popup(self, event=None):
        if not self.popup or not self.popup.winfo_exists():
            return
        try:
            current_x = self.entry.winfo_rootx()
            current_y = self.entry.winfo_rooty() + self.entry.winfo_height() + 2
            if self.last_x is None or abs(current_x - self.last_x) > 3 or abs(current_y - self.last_y) > 3:
                self.last_x = current_x
                self.last_y = current_y
                geom = self.popup.winfo_geometry().split('+')[0]
                self.popup.geometry(f"{geom}+{current_x}+{current_y}")
        except:
            pass

    def monitor_clique_global(self, event):
        try:
            widget_clicado = event.widget
            if widget_clicado == self.entry_widget:
                return
            if self.popup and self.popup.winfo_exists():
                if str(widget_clicado).find(str(self.popup)) != -1:
                    return
            if self.popup:
                self.fechar_lista()
            if self.toplevel.focus_get() == self.entry_widget:
                self.toplevel.focus_set()
        except:
            pass

    def fechar_e_limpar_foco(self):
        self.fechar_lista()
        self.toplevel.focus_set()

    def fechar_lista(self, event=None):
        if self.popup:
            try:
                self.popup.destroy()
            except:
                pass
            self.popup = None
            self.botoes_itens = []
            self.indice_selecionado = -1
            self.last_x = None
            self.last_y = None

    def ao_focar(self, event):
        if not self.entry.winfo_viewable():
            return
        self.ao_digitar()
        self.entry.focus_set()
        self.entry.icursor("end")

    def ao_clicar(self, event):
        self.fechar_lista()
        self.entry.after(50, self._forcar_abertura)

    def _forcar_abertura(self):
        self.ao_digitar()
        self.entry.focus_set()
        self.entry_widget.focus_set()
        self.entry.icursor("end")

    def mostrar_lista(self, items_filtrados):
        if self.bloquear_filtro or not items_filtrados or not self.entry.winfo_viewable():
            self.fechar_lista()
            return

        if self.popup and self.popup.winfo_exists():
            self._desenhar_botoes(items_filtrados)
            self._reposicionar_popup()
            return

        self.popup = ctk.CTkToplevel(self.entry)
        self.popup.wm_overrideredirect(True)
        self.popup.transient(self.toplevel)
        self.popup.lift()

        self.scroll_frame = ctk.CTkScrollableFrame(self.popup, width=self.width, height=self.height)
        self.scroll_frame.pack(fill="both", expand=True)
        
        try:
            x = self.entry.winfo_rootx()
            y = self.entry.winfo_rooty() + self.entry.winfo_height() + 2
            altura = min(len(items_filtrados) * 35 + 40, self.height)
            self.popup.geometry(f"{self.width}x{altura}+{x}+{y}")
            self.last_x = x
            self.last_y = y
        except:
            return

        self._desenhar_botoes(items_filtrados)

    def _desenhar_botoes(self, items_filtrados):
        for w in self.scroll_frame.winfo_children():
            w.destroy()
        self.botoes_itens = []
        for item in items_filtrados:
            btn = ctk.CTkButton(
                self.scroll_frame, 
                text=item, 
                anchor="w", 
                fg_color="transparent", 
                hover_color="#444", 
                height=30,
                command=lambda i=item: self.selecionar_item(i)
            )
            btn.pack(fill="x")
            self.botoes_itens.append(btn)
        self.indice_selecionado = -1

    def ao_digitar(self, event=None):
        if self.bloquear_filtro:
            return
        if event and event.keysym in ["Down", "Up", "Return", "Escape"]:
            return
        texto = self.entry.get().lower()
        filtrados = [i for i in self.data_list if texto in i.lower()] if texto else self.data_list
        self.mostrar_lista(filtrados)

    def mover_selecao_baixo(self, event):
        if not self.popup or not self.botoes_itens:
            return
        if self.indice_selecionado < len(self.botoes_itens) - 1:
            self.indice_selecionado += 1
            self._atualizar_destaque_teclado()
        return "break"

    def mover_selecao_cima(self, event):
        if not self.popup or not self.botoes_itens:
            return
        if self.indice_selecionado > 0:
            self.indice_selecionado -= 1
            self._atualizar_destaque_teclado()
        return "break"

    def _atualizar_destaque_teclado(self):
        for i, btn in enumerate(self.botoes_itens):
            if i == self.indice_selecionado:
                btn.configure(fg_color="#1f538d")
                if i > 3:
                    self.scroll_frame._parent_canvas.yview_moveto(i / len(self.botoes_itens))
            else:
                btn.configure(fg_color="transparent")

    def selecionar_via_enter(self, event):
        if self.popup and self.indice_selecionado != -1:
            item = self.botoes_itens[self.indice_selecionado].cget("text")
            self.selecionar_item(item)
            return "break"

    def selecionar_item(self, item):
        self.bloquear_filtro = True 
        self.entry.delete(0, 'end')
        self.entry.insert(0, item)
        self.fechar_e_limpar_foco()
        if self.command:
            self.command(item)
        self.entry.after(200, lambda: setattr(self, 'bloquear_filtro', False))

    def atualizar_dados(self, nova_lista):
        self.data_list = sorted(nova_lista)
        



class CTkCalendar(ctk.CTkFrame):
    """
    Calendário customizado com navegação cronológica e seleção de data.
    """
    def __init__(self, master, start_date=None, on_select=None, fg_color=None):
        super().__init__(master, fg_color=fg_color or "#2b2b2b", corner_radius=0)
        self.on_select = on_select
        self.selected_date = start_date or date.today()
        self.current_month = self.selected_date.month
        self.current_year = self.selected_date.year
        
        self.montar_estrutura()
        self.atualizar_calendario()

    def montar_estrutura(self):
        """Monta o cabeçalho com setas na ordem correta: << < Mês > >>"""
        header = ctk.CTkFrame(self, fg_color="#2980B9", corner_radius=0, height=35)
        header.pack(fill="x")

        # Esquerda: Voltar Ano e Mês
        ctk.CTkButton(header, text="<<", width=25, height=30, fg_color="transparent", 
                      command=lambda: self.mudar_ano(-1)).pack(side="left", padx=1)
        ctk.CTkButton(header, text="<", width=25, height=30, fg_color="transparent", 
                      command=lambda: self.mudar_mes(-1)).pack(side="left", padx=1)
        
        self.lbl_mes_ano = ctk.CTkLabel(header, text="", font=("Arial", 12, "bold"), text_color="white")
        self.lbl_mes_ano.pack(side="left", expand=True)

        # Direita: Avançar Mês e Ano
        ctk.CTkButton(header, text=">", width=25, height=30, fg_color="transparent", 
                      command=lambda: self.mudar_mes(1)).pack(side="right", padx=1)
        ctk.CTkButton(header, text=">>", width=25, height=30, fg_color="transparent", 
                      command=lambda: self.mudar_ano(1)).pack(side="right", padx=1)

        dias_frame = ctk.CTkFrame(self, fg_color="transparent")
        dias_frame.pack(fill="x", padx=2, pady=2)
        for i, d in enumerate(["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]):
            ctk.CTkLabel(dias_frame, text=d, width=35, font=("Arial", 10, "bold"), text_color="#7f8c8d").grid(row=0, column=i)

        self.corpo_cal = ctk.CTkFrame(self, fg_color="transparent")
        self.corpo_cal.pack(fill="both", expand=True, padx=2, pady=2)

    def atualizar_calendario(self):
        for w in self.corpo_cal.winfo_children(): w.destroy()
        meses_pt = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.lbl_mes_ano.configure(text=f"{meses_pt[self.current_month]} {self.current_year}")

        cal = calendar.monthcalendar(self.current_year, self.current_month)
        for r, semana in enumerate(cal):
            for c, dia in enumerate(semana):
                if dia == 0: continue
                
                hoje = date.today()
                cor_btn = "#3d3d3d"
                if dia == hoje.day and self.current_month == hoje.month and self.current_year == hoje.year:
                    cor_btn = "#27AE60"
                
                btn = ctk.CTkButton(self.corpo_cal, text=str(dia), width=32, height=30,
                                   fg_color=cor_btn, hover_color="#2980B9",
                                   command=lambda d=dia: self.selecionar_data(d))
                btn.grid(row=r, column=c, padx=1, pady=1)

    def mudar_mes(self, n):
        self.current_month += n
        if self.current_month > 12: self.current_month = 1; self.current_year += 1
        elif self.current_month < 1: self.current_month = 12; self.current_year -= 1
        self.atualizar_calendario()

    def mudar_ano(self, n):
        self.current_year += n
        self.atualizar_calendario()

    def selecionar_data(self, dia):
        data_sel = date(self.current_year, self.current_month, dia)
        if self.on_select: self.on_select(data_sel.strftime("%d/%m/%Y"))
    """
    Calendário flutuante customizado para seleção de datas.
    """
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

        # Setas corrigidas: << e < para voltar | > e >> para avançar
        ctk.CTkButton(header, text="<<", width=25, height=30, fg_color="transparent", 
                      command=lambda: self.mudar_ano(-1)).pack(side="left", padx=1)
        ctk.CTkButton(header, text="<", width=25, height=30, fg_color="transparent", 
                      command=lambda: self.mudar_mes(-1)).pack(side="left", padx=1)
        
        self.lbl_mes_ano = ctk.CTkLabel(header, text="", font=("Arial", 12, "bold"), text_color="white")
        self.lbl_mes_ano.pack(side="left", expand=True)

        ctk.CTkButton(header, text=">", width=25, height=30, fg_color="transparent", 
                      command=lambda: self.mudar_mes(1)).pack(side="right", padx=1)
        ctk.CTkButton(header, text=">>", width=25, height=30, fg_color="transparent", 
                      command=lambda: self.mudar_ano(1)).pack(side="right", padx=1)

        dias_frame = ctk.CTkFrame(self, fg_color="transparent")
        dias_frame.pack(fill="x", padx=2, pady=2)
        dias_semana = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
        for i, d in enumerate(dias_semana):
            ctk.CTkLabel(dias_frame, text=d, width=35, font=("Arial", 10, "bold"), text_color="#7f8c8d").grid(row=0, column=i)

        self.corpo_cal = ctk.CTkFrame(self, fg_color="transparent")
        self.corpo_cal.pack(fill="both", expand=True, padx=2, pady=2)

    def atualizar_calendario(self):
        for w in self.corpo_cal.winfo_children(): w.destroy()
        
        meses_pt = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.lbl_mes_ano.configure(text=f"{meses_pt[self.current_month]} {self.current_year}")

        cal = calendar.monthcalendar(self.current_year, self.current_month)
        for r, semana in enumerate(cal):
            for c, dia in enumerate(semana):
                if dia == 0: continue
                
                cor_btn = "#3d3d3d"
                if date(self.current_year, self.current_month, dia) == date.today():
                    cor_btn = "#27AE60"
                
                btn = ctk.CTkButton(self.corpo_cal, text=str(dia), width=32, height=30,
                                   fg_color=cor_btn, hover_color="#2980B9",
                                   command=lambda d=dia: self.selecionar_data(d))
                btn.grid(row=r, column=c, padx=1, pady=1)

    def mudar_mes(self, n):
        self.current_month += n
        if self.current_month > 12: self.current_month = 1; self.current_year += 1
        elif self.current_month < 1: self.current_month = 12; self.current_year -= 1
        self.atualizar_calendario()

    def mudar_ano(self, n):
        self.current_year += n
        self.atualizar_calendario()

    def selecionar_data(self, dia):
        data_sel = date(self.current_year, self.current_month, dia)
        if self.on_select: self.on_select(data_sel.strftime("%d/%m/%Y"))
    """
    Calendário flutuante customizado para seleção de datas.
    """
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

        ctk.CTkButton(header, text="<<", width=25, height=30, fg_color="transparent", 
                      command=lambda: self.mudar_ano(-1)).pack(side="left", padx=1)
        ctk.CTkButton(header, text="<", width=25, height=30, fg_color="transparent", 
                      command=lambda: self.mudar_mes(-1)).pack(side="left", padx=1)
        
        self.lbl_mes_ano = ctk.CTkLabel(header, text="", font=("Arial", 12, "bold"), text_color="white")
        self.lbl_mes_ano.pack(side="left", expand=True)

        ctk.CTkButton(header, text=">", width=25, height=30, fg_color="transparent", 
                      command=lambda: self.mudar_mes(1)).pack(side="right", padx=1)
        ctk.CTkButton(header, text=">>", width=25, height=30, fg_color="transparent", 
                      command=lambda: self.mudar_ano(1)).pack(side="right", padx=1)

        dias_frame = ctk.CTkFrame(self, fg_color="transparent")
        dias_frame.pack(fill="x", padx=2, pady=2)
        dias_semana = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
        for i, d in enumerate(dias_semana):
            ctk.CTkLabel(dias_frame, text=d, width=35, font=("Arial", 10, "bold"), text_color="#7f8c8d").grid(row=0, column=i)

        self.corpo_cal = ctk.CTkFrame(self, fg_color="transparent")
        self.corpo_cal.pack(fill="both", expand=True, padx=2, pady=2)

    def atualizar_calendario(self):
        """
        Gera a grade de botões para os dias do mês atual.
        """
        for w in self.corpo_cal.winfo_children(): w.destroy()
        
        meses_pt = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.lbl_mes_ano.configure(text=f"{meses_pt[self.current_month]} {self.current_year}")

        cal = calendar.monthcalendar(self.current_year, self.current_month)
        for r, semana in enumerate(cal):
            for c, dia in enumerate(semana):
                if dia == 0: continue
                
                cor_btn = "#3d3d3d"
                texto_cor = "white"
                if date(self.current_year, self.current_month, dia) == date.today():
                    cor_btn = "#27AE60"
                
                btn = ctk.CTkButton(self.corpo_cal, text=str(dia), width=32, height=30,
                                   fg_color=cor_btn, text_color=texto_cor, hover_color="#2980B9",
                                   command=lambda d=dia: self.selecionar_data(d))
                btn.grid(row=r, column=c, padx=1, pady=1)

    def mudar_mes(self, n):
        self.current_month += n
        if self.current_month > 12: self.current_month = 1; self.current_year += 1
        elif self.current_month < 1: self.current_month = 12; self.current_year -= 1
        self.atualizar_calendario()

    def mudar_ano(self, n):
        self.current_year += n
        self.atualizar_calendario()

    def selecionar_data(self, dia):
        data_sel = date(self.current_year, self.current_month, dia)
        if self.on_select: self.on_select(data_sel.strftime("%d/%m/%Y"))