# src/utils/componentes_estilizados.py
import customtkinter as ctk

class CTkFloatingDropdown:
    """
    Componente de busca inteligente que flutua sobre a interface.
    Auto-gerencia o fechamento ao perder foco ou mudar de contexto.
    """
    def __init__(self, entry_widget, data_list, width=200, height=150, command=None):
        self.entry = entry_widget
        self.data_list = sorted(data_list)
        self.popup = None
        self.width = width
        self.height = height
        self.command = command 
        
        self.items_buttons = []
        self.current_selection_index = -1

        # Bindings fundamentais
        self.entry.bind("<KeyRelease>", self.ao_digitar)
        self.entry.bind("<FocusIn>", self.ao_focar)
        self.entry.bind("<Down>", self.mover_selecao_baixo)
        self.entry.bind("<Up>", self.mover_selecao_cima)
        self.entry.bind("<Return>", self.selecionar_via_enter)
        self.entry.bind("<Tab>", self.fechar_lista)
        
        # Fecha ao clicar fora ou perder o foco do campo
        self.entry.bind("<FocusOut>", self.ao_perder_foco_entry)

    def fechar_lista(self, event=None):
        """Fecha o popup de forma segura."""
        if self.popup:
            try:
                self.popup.destroy()
            except:
                pass
            self.popup = None
            self.items_buttons = []

    def ao_perder_foco_entry(self, event):
        """Delay para verificar se o foco foi para a lista ou para fora do app."""
        self.entry.after(200, self._validar_fechamento)

    def _validar_fechamento(self):
        if self.popup:
            try:
                focado = self.entry.focus_get()
                # Se o novo foco não for o Entry nem o Popup, fecha.
                if focado != self.entry and str(focado).find(str(self.popup)) == -1:
                    self.fechar_lista()
            except:
                self.fechar_lista()

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
            
            # Fecha se a janela principal (App) for movida
            self.entry.winfo_toplevel().bind("<Configure>", lambda e: self.fechar_lista(), add="+")

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
        if self.command: self.command(item)

    def atualizar_dados(self, nova_lista):
        self.data_list = sorted(nova_lista)

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
            item = self.items_buttons[self.current_selection_index].cget("text")
            self.selecionar_item(item)
            return "break"