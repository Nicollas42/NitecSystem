# src/utils/componentes_estilizados.py
import customtkinter as ctk

class CTkFloatingDropdown:
    """
    Componente de busca inteligente com gestão de foco seletiva.
    Permite digitação contínua e garante reabertura ao resetar o foco apenas em cliques externos.
    """
    def __init__(self, entry_widget, data_list, width=200, height=150, command=None):
        """
        Inicializa o dropdown e configura os eventos.
        """
        self.entry = entry_widget
        self.data_list = sorted(data_list)
        self.popup = None
        self.width = width
        self.height = height
        self.command = command 
        self.bloquear_filtro = False 
        
        self.botoes_itens = []
        self.indice_selecionado = -1

        self.toplevel = self.entry.winfo_toplevel()

        # Bindings de escrita e navegação
        self.entry.bind("<KeyRelease>", self.ao_digitar)
        self.entry.bind("<FocusIn>", self.ao_focar)
        self.entry.bind("<Button-1>", self.ao_clicar) 
        self.entry.bind("<Down>", self.mover_selecao_baixo)
        self.entry.bind("<Up>", self.mover_selecao_cima)
        self.entry.bind("<Return>", self.selecionar_via_enter)
        self.entry.bind("<Escape>", lambda e: self.fechar_e_limpar_foco())

        # Monitoramento Global de Cliques
        self.toplevel.bind_all("<Button-1>", self.monitor_clique_global, add="+")
        
        # Fecha se a aba mudar ou janela for minimizada
        self.entry.bind("<Unmap>", lambda e: self.fechar_lista(), add="+")
        self.toplevel.bind("<Unmap>", lambda e: self.fechar_lista(), add="+")

    def monitor_clique_global(self, event):
        """
        Gere o fecho da lista e a remoção do foco apenas quando necessário.
        """
        try:
            widget_clicado = event.widget
            
            # Se clicou no Entry, mantém o foco e a lista (se houver texto/interação)
            if widget_clicado == self.entry:
                return
            
            # Se clicou dentro do popup, mantém o foco no Entry para permitir navegação teclado
            if self.popup and self.popup.winfo_exists():
                if str(widget_clicado).find(str(self.popup)) != -1:
                    return

            # Clique em QUALQUER outro lugar: Fecha a lista e limpa o foco do Entry
            if self.popup:
                self.fechar_lista()
            
            # Só tira o foco se o widget atual for o Entry, permitindo que o próximo clique seja um FocusIn
            if self.toplevel.focus_get() == self.entry:
                self.toplevel.after(0, self.toplevel.focus_set)
                
        except:
            pass

    def fechar_e_limpar_foco(self):
        """Fecha a lista e garante que o campo perca o foco (usado no Esc)."""
        self.fechar_lista()
        self.toplevel.focus_set()

    def fechar_lista(self, event=None):
        """Destrói o popup sem necessariamente tirar o foco (permite continuar a digitar)."""
        if self.popup:
            try:
                self.popup.destroy()
            except:
                pass
            self.popup = None
            self.botoes_itens = []
            self.indice_selecionado = -1

    def ao_focar(self, event):
        """Abre a lista ao ganhar foco."""
        if not self.entry.winfo_viewable():
            return
        self.ao_digitar()

    def ao_clicar(self, event):
        """Garante a abertura no clique se já não estiver aberta."""
        if not self.popup or not self.popup.winfo_exists():
            self.ao_digitar()

    def mostrar_lista(self, items_filtrados):
        """Renderiza ou atualiza a janela flutuante."""
        if self.bloquear_filtro or not items_filtrados or not self.entry.winfo_viewable():
            self.fechar_lista()
            return

        if self.popup and self.popup.winfo_exists():
            self._desenhar_botoes(items_filtrados)
            return

        self.popup = ctk.CTkToplevel(self.entry)
        self.popup.wm_overrideredirect(True)
        self.popup.attributes("-topmost", True)
        self.popup.transient(self.toplevel)
        
        self.scroll_frame = ctk.CTkScrollableFrame(self.popup, width=self.width, height=self.height)
        self.scroll_frame.pack(fill="both", expand=True)
        
        try:
            x = self.entry.winfo_rootx()
            y = self.entry.winfo_rooty() + self.entry.winfo_height() + 2
            self.popup.geometry(f"{self.width}x{min(len(items_filtrados)*35 + 10, self.height)}+{x}+{y}")
        except:
            return

        self._desenhar_botoes(items_filtrados)

    def _desenhar_botoes(self, items_filtrados):
        """Recria os botões de sugestão."""
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
        """Filtra dados e ignora teclas de comando."""
        if self.bloquear_filtro:
            return
        
        if event and event.keysym in ["Down", "Up", "Return", "Escape"]:
            return

        texto = self.entry.get().lower()
        filtrados = [i for i in self.data_list if texto in i.lower()] if texto else self.data_list
        self.mostrar_lista(filtrados)

    def mover_selecao_baixo(self, event):
        """Navega para baixo no menu."""
        if not self.popup or not self.botoes_itens:
            return
        if self.indice_selecionado < len(self.botoes_itens) - 1:
            self.indice_selecionado += 1
            self._atualizar_destaque_teclado()
        return "break"

    def mover_selecao_cima(self, event):
        """Navega para cima no menu."""
        if not self.popup or not self.botoes_itens:
            return
        if self.indice_selecionado > 0:
            self.indice_selecionado -= 1
            self._atualizar_destaque_teclado()
        return "break"

    def _atualizar_destaque_teclado(self):
        """Aplica o destaque visual via teclado."""
        for i, btn in enumerate(self.botoes_itens):
            if i == self.indice_selecionado:
                btn.configure(fg_color="#1f538d")
                if i > 3:
                    self.scroll_frame._parent_canvas.yview_moveto(i / len(self.botoes_itens))
            else:
                btn.configure(fg_color="transparent")

    def selecionar_via_enter(self, event):
        """Seleciona o item destacado ao pressionar Enter."""
        if self.popup and self.indice_selecionado != -1:
            item = self.botoes_itens[self.indice_selecionado].cget("text")
            self.selecionar_item(item)
            return "break"

    def selecionar_item(self, item):
        """Finaliza a seleção, preenche o campo e tira o foco."""
        self.bloquear_filtro = True 
        self.entry.delete(0, 'end')
        self.entry.insert(0, item)
        self.fechar_e_limpar_foco()
        
        if self.command:
            self.command(item)
            
        self.entry.after(200, lambda: setattr(self, 'bloquear_filtro', False))

    def atualizar_dados(self, nova_lista):
        """Sincroniza a lista de dados."""
        self.data_list = sorted(nova_lista)