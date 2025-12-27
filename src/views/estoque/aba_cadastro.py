# src/views/estoque/aba_cadastro.py
import customtkinter as ctk
from tkinter import ttk, messagebox

# --- COMPONENTE: LISTA FLUTUANTE DE PESQUISA (Mantido igual) ---
class CTkFloatingDropdown:
    def __init__(self, entry_widget, data_list, width=200, height=150):
        self.entry = entry_widget
        self.data_list = sorted(data_list)
        self.popup = None
        self.width = width
        self.height = height
        
        self.items_buttons = []
        self.current_selection_index = -1

        self.entry.bind("<KeyRelease>", self.ao_digitar)
        self.entry.bind("<FocusIn>", self.ao_focar)
        self.entry.bind("<Down>", self.mover_selecao_baixo)
        self.entry.bind("<Up>", self.mover_selecao_cima)
        self.entry.bind("<Return>", self.selecionar_via_enter)
        self.entry.bind("<Tab>", self.fechar_lista)
        self.entry.bind("<FocusOut>", self.ao_perder_foco_entry)

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

    def set_value(self, value):
        self.entry.delete(0, 'end')
        self.entry.insert(0, value)

    def get(self):
        return self.entry.get()

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


class AbaCadastro(ctk.CTkFrame):
    def __init__(self, master, controller, callback_atualizar):
        super().__init__(master)
        self.controller = controller
        self.atualizar_sistema = callback_atualizar
        self.produtos = {} 
        self.janela_ajuda = None
        
        self.lista_categorias = ["Panificação", "Confeitaria", "Bebidas", "Frios", "Insumos", "Embalagens", "Outros", "Laticínios", "Hortifruti"]

        self.montar_layout()

    def montar_layout(self):
        # Container principal usando Grid para dividir a tela proporcionalmente
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configura as colunas: Coluna 0 (Form) = peso 3, Coluna 1 (Lista) = peso 2
        container.columnconfigure(0, weight=3)
        container.columnconfigure(1, weight=2)
        container.rowconfigure(0, weight=1)

        # ===================================================
        # ESQUERDA: FORMULÁRIO
        # ===================================================
        form = ctk.CTkFrame(container, border_width=1, border_color="#444")
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Grid interno do formulário (2 colunas para campos lado a lado)
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        # --- Título + Ajuda (Na mesma linha) ---
        title_frame = ctk.CTkFrame(form, fg_color="transparent")
        title_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=15, pady=15)
        
        ctk.CTkLabel(title_frame, text="Dados do Item", font=("Arial", 16, "bold"), text_color="#2CC985").pack(side="left")
        ctk.CTkButton(title_frame, text="?", width=25, height=25, fg_color="#2980B9", hover_color="#1F618D",
                      command=self.mostrar_ajuda).pack(side="left", padx=10)

        # --- Tipo de Item ---
        ctk.CTkLabel(form, text="Tipo do Item:", text_color="#ccc").grid(row=1, column=0, columnspan=2, sticky="w", padx=15)
        self.tipo_var = ctk.StringVar(value="PRODUTO")
        
        radio_frame = ctk.CTkFrame(form, fg_color="transparent")
        radio_frame.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 15))
        
        ctk.CTkRadioButton(radio_frame, text="🍞 PRODUTO (Venda)", variable=self.tipo_var, value="PRODUTO", fg_color="#2980B9").pack(side="left", padx=5)
        ctk.CTkRadioButton(radio_frame, text="📦 INSUMO (Matéria)", variable=self.tipo_var, value="INSUMO", fg_color="#E67E22").pack(side="left", padx=15)

        # --- Linha 1: Código e Unidade ---
        self.criar_input(form, "Código:", 3, 0)
        self.ent_cod = ctk.CTkEntry(form, placeholder_text="Ex: 1001")
        self.ent_cod.grid(row=4, column=0, padx=15, pady=(0, 10), sticky="ew")

        self.criar_input(form, "Unidade:", 3, 1)
        self.combo_un = ctk.CTkComboBox(form, values=["UN", "KG", "L", "PCT", "CX", "G", "ML"])
        self.combo_un.grid(row=4, column=1, padx=15, pady=(0, 10), sticky="ew")

        # --- Linha 2: Nome (Ocupa as 2 colunas) ---
        self.criar_input(form, "Nome:", 5, 0)
        self.ent_nome = ctk.CTkEntry(form, placeholder_text="Ex: Farinha de Trigo")
        self.ent_nome.grid(row=6, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="ew")

        # --- Linha 3: Categoria (Ocupa as 2 colunas) ---
        self.criar_input(form, "Categoria:", 7, 0)
        self.ent_cat = ctk.CTkEntry(form, placeholder_text="Selecione ou Digite...")
        self.ent_cat.grid(row=8, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="ew")
        self.dropdown_cat = CTkFloatingDropdown(self.ent_cat, self.lista_categorias, width=400) # Width maior para categoria

        # --- Linha 4: Custo e Preço ---
        self.criar_input(form, "Custo (R$):", 9, 0)
        self.ent_custo = ctk.CTkEntry(form, placeholder_text="0.00")
        self.ent_custo.grid(row=10, column=0, padx=15, pady=(0, 10), sticky="ew")

        self.criar_input(form, "Venda (R$):", 9, 1)
        self.ent_preco = ctk.CTkEntry(form, placeholder_text="0.00")
        self.ent_preco.grid(row=10, column=1, padx=15, pady=(0, 10), sticky="ew")

        # --- Linha 5: Estoque Mínimo e Controle ---
        self.criar_input(form, "Estoque Mínimo:", 11, 0)
        self.ent_minimo = ctk.CTkEntry(form, placeholder_text="Ex: 10")
        self.ent_minimo.grid(row=12, column=0, padx=15, pady=(0, 10), sticky="ew")

        self.switch_controla = ctk.CTkSwitch(form, text="Controlar Estoque")
        self.switch_controla.select()
        self.switch_controla.grid(row=12, column=1, padx=15, pady=(20, 10), sticky="w")

        # --- Botão Salvar ---
        ctk.CTkLabel(form, text="").grid(row=13, column=0) # Espaçador
        ctk.CTkButton(form, text="💾 SALVAR ITEM", fg_color="#27AE60", height=50, font=("Arial", 14, "bold"),
                      command=self.salvar).grid(row=14, column=0, columnspan=2, padx=15, pady=20, sticky="ew")

        # ===================================================
        # DIREITA: LISTA RÁPIDA (Expandida)
        # ===================================================
        list_frame = ctk.CTkFrame(container, fg_color="transparent")
        list_frame.grid(row=0, column=1, sticky="nsew")
        
        ctk.CTkLabel(list_frame, text="Itens Cadastrados", font=("Arial", 14, "bold")).pack(pady=(15, 10))
        
        # Frame para conter a Treeview e Scrollbar
        tree_container = ctk.CTkFrame(list_frame, fg_color="transparent")
        tree_container.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(tree_container, columns=("cod", "tipo", "nome"), show="headings")
        
        # Configuração das colunas para preencher melhor
        self.tree.heading("cod", text="ID")
        self.tree.column("cod", width=50, anchor="center")
        
        self.tree.heading("tipo", text="Tipo")
        self.tree.column("tipo", width=70, anchor="center")
        
        self.tree.heading("nome", text="Nome")
        self.tree.column("nome", width=200) # Nome ganha mais espaço
        
        scroll = ctk.CTkScrollbar(tree_container, command=self.tree.yview)
        self.tree.configure(yscroll=scroll.set)
        
        scroll.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        
        self.tree.bind("<<TreeviewSelect>>", self.carregar_edicao)

    def criar_input(self, p, t, r, c):
        ctk.CTkLabel(p, text=t, text_color="#ccc").grid(row=r, column=c, sticky="w", padx=15, pady=(5,0))

    def salvar(self):
        dados = {
            "id": self.ent_cod.get().strip(),
            "nome": self.ent_nome.get().strip(),
            "categoria": self.ent_cat.get(),
            "unidade": self.combo_un.get(),
            "tipo": self.tipo_var.get(),
            "custo": self.ent_custo.get().replace(",", ".") or "0",
            "preco": self.ent_preco.get().replace(",", ".") or "0",
            "minimo": self.ent_minimo.get().replace(",", ".") or "0",
            "controla_estoque": bool(self.switch_controla.get())
        }
        
        if not dados["id"] or not dados["nome"]:
            messagebox.showwarning("Erro", "Campos obrigatórios vazios")
            return

        if dados["tipo"] == "INSUMO" and float(dados["preco"]) > 0:
            if not messagebox.askyesno("Atenção", "Preço de Venda em Insumo?\n\nGeralmente Insumos (Farinha, Ovos) têm apenas Custo.\nDeseja continuar?"):
                return

        if self.controller.salvar_produto(dados):
            messagebox.showinfo("Sucesso", "Item Salvo!")
            self.limpar_form()
            self.atualizar_sistema()

    def limpar_form(self):
        for e in [self.ent_cod, self.ent_nome, self.ent_preco, self.ent_custo, self.ent_minimo, self.ent_cat]: 
            e.delete(0, "end")
        self.tipo_var.set("PRODUTO")
        self.dropdown_cat.fechar_lista()

    def atualizar_lista(self, produtos_dict):
        self.produtos = produtos_dict
        for i in self.tree.get_children(): self.tree.delete(i)
        
        for cod, p in produtos_dict.items():
            tipo_display = "📦 INS" if p.get('tipo') == "INSUMO" else "🍞 PROD"
            self.tree.insert("", "end", values=(cod, tipo_display, p['nome']))

    def carregar_edicao(self, event):
        sel = self.tree.selection()
        if not sel: return
        cod = self.tree.item(sel[0], "values")[0]
        p = self.produtos.get(cod)
        if p:
            self.limpar_form()
            self.ent_cod.insert(0, cod)
            self.ent_nome.insert(0, p['nome'])
            self.ent_preco.insert(0, p.get('preco', 0))
            self.ent_custo.insert(0, p.get('custo', 0))
            self.ent_minimo.insert(0, p.get('estoque_minimo', 0))
            self.combo_un.set(p.get('unidade', 'UN'))
            self.dropdown_cat.set_value(p.get('categoria', 'Outros'))
            self.tipo_var.set(p.get('tipo', 'PRODUTO'))
            
            if p.get('controla_estoque', True): self.switch_controla.select()
            else: self.switch_controla.deselect()

    def mostrar_ajuda(self):
        if self.janela_ajuda and self.janela_ajuda.winfo_exists():
            self.janela_ajuda.lift(); self.janela_ajuda.focus_force(); return
        
        self.janela_ajuda = ctk.CTkToplevel(self)
        self.janela_ajuda.title("Ajuda - Cadastro de Itens")
        self.janela_ajuda.geometry("500x550")
        self.janela_ajuda.transient(self)
        self.janela_ajuda.lift()
        self.janela_ajuda.focus_force()
        
        ctk.CTkLabel(self.janela_ajuda, text="📖 MANUAL DE CADASTRO", font=("Arial", 20, "bold"), text_color="#2CC985").pack(pady=20)
        
        texto_ajuda = """
1. TIPO DO ITEM (MUITO IMPORTANTE!)
• 📦 INSUMO: Matéria-prima que você COMPRA.
   Ex: Farinha, Leite, Ovos.
   -> Tem CUSTO (valor de compra).
   -> NÃO tem Preço de Venda (normalmente é 0).

• 🍞 PRODUTO: O que você VENDE na padaria.
   Ex: Pão Francês, Bolo, Café.
   -> Tem PREÇO DE VENDA.
   -> O Custo é calculado automaticamente pela Receita.

2. CAMPOS DE VALOR
• Custo (R$): Quanto custou pra comprar ou produzir.
• Venda (R$): Por quanto vai ser vendido no caixa.

3. ESTOQUE MÍNIMO
• O sistema avisará quando o estoque ficar abaixo desse número.

4. CONTROLAR ESTOQUE
• Ativado (Padrão): Desconta do estoque ao vender/produzir.
• Desativado: Apenas registra o valor financeiro (bom para Serviços ou Taxas).
"""
        lbl = ctk.CTkLabel(self.janela_ajuda, text=texto_ajuda, justify="left", anchor="nw", padx=20, font=("Consolas", 13))
        lbl.pack(fill="both", expand=True)