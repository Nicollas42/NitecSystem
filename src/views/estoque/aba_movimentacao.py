# src/views/estoque/aba_movimentacao.py
import customtkinter as ctk
from tkinter import messagebox

# --- COMPONENTE: LISTA FLUTUANTE DE PESQUISA (PADRÃO) ---
class CTkFloatingDropdown:
    def __init__(self, entry_widget, data_list, width=200, height=150, command=None):
        self.entry = entry_widget
        self.data_list = sorted(data_list)
        self.popup = None
        self.width = width
        self.height = height
        self.command = command 
        
        self.items_buttons = []
        self.current_selection_index = -1

        # Eventos para fechar e controlar o dropdown
        self.entry.bind("<KeyRelease>", self.ao_digitar)
        self.entry.bind("<FocusIn>", self.ao_focar)
        self.entry.bind("<Down>", self.mover_selecao_baixo)
        self.entry.bind("<Up>", self.mover_selecao_cima)
        self.entry.bind("<Return>", self.selecionar_via_enter)
        self.entry.bind("<Tab>", self.fechar_lista)
        
        # Evento CRUCIAL: Fecha ao perder o foco
        self.entry.bind("<FocusOut>", self.ao_perder_foco_entry)

    def fechar_lista(self, event=None):
        """Destrói o popup de forma segura"""
        if self.popup:
            try:
                self.popup.destroy()
            except:
                pass
            self.popup = None
            self.items_buttons = []

    def ao_perder_foco_entry(self, event):
        """Verifica se o foco foi para o popup; se não, fecha."""
        # Pequeno delay para permitir que o clique no botão do popup seja processado antes de fechar
        self.entry.after(200, self._validar_fechamento)

    def _validar_fechamento(self):
        if self.popup:
            try:
                focado = self.entry.focus_get()
                # Se o novo widget focado não for o Entry e não for parte do popup, fecha.
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
            self.popup.wm_overrideredirect(True) # Remove bordas da janela
            self.popup.attributes("-topmost", True) # Mantém na frente
            
            self.scroll_frame = ctk.CTkScrollableFrame(self.popup, width=self.width, height=self.height)
            self.scroll_frame.pack(fill="both", expand=True)
            
            # Fecha se a janela principal for movida
            self.entry.winfo_toplevel().bind("<Configure>", lambda e: self.fechar_lista(), add="+")

        try:
            # Posicionamento dinâmico logo abaixo do Entry
            x = self.entry.winfo_rootx()
            y = self.entry.winfo_rooty() + self.entry.winfo_height() + 2
            self.popup.geometry(f"{self.width}x{min(len(items_filtrados)*35 + 10, self.height)}+{x}+{y}")
        except: return

        # Limpa e recria os botões
        for w in self.scroll_frame.winfo_children(): w.destroy()
        self.items_buttons = []

        for item in items_filtrados:
            btn = ctk.CTkButton(self.scroll_frame, text=item, anchor="w", fg_color="transparent", 
                                hover_color="#444", height=30,
                                command=lambda i=item: self.selecionar_item(i))
            btn.pack(fill="x")
            self.items_buttons.append(btn)
    
    # ... (restante das funções ao_digitar, mover_selecao, etc, permanecem as mesmas)

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

    def ao_perder_foco_entry(self, event):
        self.entry.after(150, self._verificar_foco_destino)

    def _verificar_foco_destino(self):
        if self.popup:
            try:
                focado = self.entry.focus_get()
                if focado is None or (focado != self.entry and str(focado).find(str(self.scroll_frame)) == -1):
                    self.fechar_lista()
            except: pass

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


class AbaMovimentacao(ctk.CTkFrame):
    def __init__(self, master, controller, callback_atualizar):
        super().__init__(master)
        self.controller = controller
        self.atualizar_sistema = callback_atualizar
        self.lista_nomes = []
        self.produtos_cache = {}

        self.montar_layout()

    def montar_layout(self):
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.pack(fill="both", expand=True, padx=50, pady=20)

        ctk.CTkLabel(center, text="REGISTRO DE MOVIMENTAÇÃO", font=("Arial", 18, "bold")).pack(pady=10)

        # --- SELEÇÃO DE PRODUTO (PADRONIZADO) ---
        ctk.CTkLabel(center, text="1. Selecione o Produto:").pack(anchor="w")
        
        self.ent_prod = ctk.CTkEntry(center, height=40, font=("Arial", 14), placeholder_text="Digite para buscar...")
        self.ent_prod.pack(fill="x", pady=5)
        
        # Vincula o Dropdown ao Entry
        self.dropdown_prod = CTkFloatingDropdown(self.ent_prod, self.lista_nomes, width=400)

        # --- LOCAL ---
        ctk.CTkLabel(center, text="2. Local da Movimentação:").pack(anchor="w", pady=(10,0))
        self.combo_local = ctk.CTkOptionMenu(center, values=["Fundo (Depósito)", "Frente (Loja)"], fg_color="#333", height=40)
        self.combo_local.pack(fill="x", pady=5)

        # --- TIPO DE MOVIMENTAÇÃO (LADO A LADO) ---
        ctk.CTkLabel(center, text="3. Tipo de Operação:").pack(anchor="w", pady=(10,5))
        
        self.tipo_var = ctk.StringVar(value="ENTRADA")
        radio_f = ctk.CTkFrame(center, fg_color="transparent")
        radio_f.pack(fill="x", pady=5)
        
        # Colocados lado a lado usando pack side=left no mesmo frame
        ctk.CTkRadioButton(radio_f, text="🔼 ENTRADA", variable=self.tipo_var, value="ENTRADA", fg_color="#27AE60").pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(radio_f, text="🗑️ PERDA", variable=self.tipo_var, value="PERDA", fg_color="#C0392B").pack(side="left", padx=20)

        # --- DETALHES ---
        detalhes = ctk.CTkFrame(center, fg_color="transparent")
        detalhes.pack(fill="x", pady=20)
        
        ctk.CTkLabel(detalhes, text="Quantidade:").pack(side="left", padx=(0,10))
        self.ent_qtd = ctk.CTkEntry(detalhes, width=120, height=40, font=("Arial", 14), justify="center")
        self.ent_qtd.pack(side="left")

        ctk.CTkLabel(detalhes, text="Motivo:").pack(side="left", padx=(20,10))
        self.ent_motivo = ctk.CTkEntry(detalhes, placeholder_text="Ex: Compra NF 123", height=40)
        self.ent_motivo.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(center, text="✅ CONFIRMAR", height=50, fg_color="#2980B9", 
                      command=self.confirmar).pack(pady=10, fill="x")
        
        ctk.CTkLabel(center, text="--- OU ---", text_color="#666").pack(pady=10)
        
        ctk.CTkButton(center, text="📦 REPOSIÇÃO RÁPIDA (Fundo -> Frente)", 
                      height=50, fg_color="#8E44AD", hover_color="#732D91",
                      command=self.abrir_reposicao).pack(fill="x")

    def atualizar_produtos(self, produtos_dict):
        self.produtos_cache = produtos_dict
        self.lista_nomes = sorted([p['nome'] for p in produtos_dict.values()])
        
        # Atualiza a lista do Dropdown flutuante
        if hasattr(self, 'dropdown_prod'):
            self.dropdown_prod.atualizar_dados(self.lista_nomes)

    def confirmar(self):
        nome = self.ent_prod.get() # Pega do Entry agora
        qtd = self.ent_qtd.get().replace(",", ".")
        motivo = self.ent_motivo.get()
        tipo = self.tipo_var.get()
        local = self.combo_local.get().split()[0].lower()

        # Acha o ID pelo nome
        cod = next((c for c, p in self.produtos_cache.items() if p['nome'] == nome), None)
        
        if cod:
            ok, msg = self.controller.movimentar_estoque(cod, qtd, tipo, motivo, "Admin", local)
            if ok:
                messagebox.showinfo("Sucesso", msg)
                self.ent_prod.delete(0, 'end')
                self.ent_qtd.delete(0, 'end')
                self.ent_motivo.delete(0, 'end')
                self.atualizar_sistema()
            else:
                messagebox.showerror("Erro", msg)
        else:
            messagebox.showerror("Erro", "Produto inválido ou não encontrado.")

    def abrir_reposicao(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Reposição de Loja")
        dialog.geometry("400x450")
        
        dialog.transient(self)
        dialog.lift()
        dialog.focus_force()

        ctk.CTkLabel(dialog, text="REPOSIÇÃO RÁPIDA", font=("Arial", 16, "bold"), text_color="#8E44AD").pack(pady=20)
        
        # Mantendo o combobox simples no popup para simplicidade ou pode-se mudar para Entry também se desejar
        combo = ctk.CTkComboBox(dialog, values=self.lista_nomes, width=300)
        combo.pack(pady=10)

        ent = ctk.CTkEntry(dialog, placeholder_text="Qtd para Frente", width=150, font=("Arial", 20))
        ent.pack(pady=10); ent.focus_set()

        def salvar():
            nome = combo.get()
            cod = next((c for c, p in self.produtos_cache.items() if p['nome'] == nome), None)
            if cod:
                ok, msg = self.controller.transferir_fundo_para_frente(cod, ent.get(), "Admin")
                if ok:
                    messagebox.showinfo("Sucesso", msg)
                    dialog.destroy()
                    self.atualizar_sistema()
                else:
                    messagebox.showerror("Erro", msg)

        ctk.CTkButton(dialog, text="TRANSFERIR", fg_color="#27AE60", height=45, command=salvar).pack(pady=30)