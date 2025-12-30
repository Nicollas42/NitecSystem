# src/views/estoque/aba_cadastro.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from src.utils.componentes_estilizados import CTkFloatingDropdown
from src.utils.textos_ajuda import abrir_ajuda
from src.utils.formata_numeros_br import formata_numeros_br

class AbaCadastro(ctk.CTkFrame):
    def __init__(self, master, controller, callback_atualizar):
        super().__init__(master)
        self.controller = controller
        self.atualizar_sistema = callback_atualizar
        self.produtos = {} 
        self.lista_categorias = ["Panificação", "Confeitaria", "Bebidas", "Frios", "Insumos", "Embalagens", "Outros", "Laticínios", "Hortifruti"]
        
        # Lista para sugestão de grupos existentes
        self.lista_grupos = []

        self.expandido = False 
        self.montar_layout()

    # --- VALIDAÇÕES ---
    def validar_inteiro(self, texto):
        if texto == "": return True
        return texto.isdigit()

    def validar_decimal(self, texto):
        if texto == "": return True
        chars_validos = all(c.isdigit() or c in ",." for c in texto)
        contagem_seps = texto.count('.') + texto.count(',')
        return chars_validos and contagem_seps <= 1

    def validar_lista_numeros(self, texto):
        if texto == "": return True
        return all(c.isdigit() or c in ", " for c in texto)

    def montar_layout(self):
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.container.columnconfigure(0, weight=3)
        self.container.columnconfigure(1, weight=5)
        self.container.rowconfigure(0, weight=1)

        # === ESQUERDA: FORMULÁRIO ===
        self.form_frame = ctk.CTkFrame(self.container, border_width=1, border_color="#444")
        self.form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.form_frame.columnconfigure(0, weight=1)
        self.form_frame.columnconfigure(1, weight=1)

        self.montar_formulario(self.form_frame)

        # === DIREITA: LISTA ===
        self.list_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.list_frame.grid(row=0, column=1, sticky="nsew")
        
        header_list = ctk.CTkFrame(self.list_frame, fg_color="transparent", height=40)
        header_list.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(header_list, text="Itens Cadastrados", font=("Arial", 14, "bold")).pack(side="left")
        
        self.btn_expandir = ctk.CTkButton(header_list, text="⤢ Expandir Lista", width=120, height=25, 
                                          fg_color="#555", hover_color="#666", command=self.alternar_expansao)
        self.btn_expandir.pack(side="right")
        
        tree_container = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        tree_container.pack(fill="both", expand=True)

        cols = ("cod", "nome", "grupo", "custo", "venda", "cat")
        self.tree = ttk.Treeview(tree_container, columns=cols, show="headings", selectmode="browse")
        
        self.tree.heading("cod", text="ID")
        self.tree.heading("nome", text="NOME")
        self.tree.heading("grupo", text="GRUPO")
        self.tree.heading("custo", text="CUSTO")
        self.tree.heading("venda", text="VENDA")
        self.tree.heading("cat", text="CATEGORIA")
        
        self.tree.column("cod", width=40, anchor="center")
        self.tree.column("nome", width=180)
        self.tree.column("grupo", width=100)
        self.tree.column("custo", width=80, anchor="center")
        self.tree.column("venda", width=80, anchor="center")
        self.tree.column("cat", width=80, anchor="w")
        
        self.tree.tag_configure('odd', background='#2b2b2b')
        self.tree.tag_configure('even', background='#333333')
        
        vsb = ctk.CTkScrollbar(tree_container, orientation="vertical", command=self.tree.yview)
        hsb = ctk.CTkScrollbar(tree_container, orientation="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.perguntar_edicao)
        self.configurar_ordenacao()

    def montar_formulario(self, parent):
        vcmd_int = (self.register(self.validar_inteiro), "%P")
        vcmd_dec = (self.register(self.validar_decimal), "%P")
        vcmd_lista = (self.register(self.validar_lista_numeros), "%P")

        title_frame = ctk.CTkFrame(parent, fg_color="transparent")
        title_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=15, pady=15)
        ctk.CTkLabel(title_frame, text="Dados do Item", font=("Arial", 16, "bold"), text_color="#2CC985").pack(side="left")
        ctk.CTkButton(title_frame, text="?", width=25, height=25, fg_color="#2980B9", command=self.mostrar_ajuda).pack(side="left", padx=10)

        # Tipo
        self.tipo_var = ctk.StringVar(value="PRODUTO")
        radio_frame = ctk.CTkFrame(parent, fg_color="transparent")
        radio_frame.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 10))
        ctk.CTkRadioButton(radio_frame, text="🍞 PRODUTO", variable=self.tipo_var, value="PRODUTO", fg_color="#2980B9").pack(side="left", padx=5)
        ctk.CTkRadioButton(radio_frame, text="📦 INSUMO", variable=self.tipo_var, value="INSUMO", fg_color="#E67E22").pack(side="left", padx=15)

        # ID e Unidade
        self.criar_input(parent, "Código ID (Único):", 2, 0)
        self.ent_cod = ctk.CTkEntry(parent, placeholder_text="Ex: 1001", validate="key", validatecommand=vcmd_int)
        self.ent_cod.grid(row=3, column=0, padx=15, pady=(0, 10), sticky="ew")

        self.criar_input(parent, "Unidade:", 2, 1)
        self.combo_un = ctk.CTkComboBox(parent, values=["UN", "KG", "L", "PCT", "CX", "G", "ML"])
        self.combo_un.grid(row=3, column=1, padx=15, pady=(0, 10), sticky="ew")

        # Nome
        self.criar_input(parent, "Nome do Produto (Variação):", 4, 0)
        self.ent_nome = ctk.CTkEntry(parent, placeholder_text="Ex: Coca-Cola Zero 2L")
        self.ent_nome.grid(row=5, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="ew")

        # NOVO CAMPO: GRUPO
        self.criar_input(parent, "Grupo / Família (Para Agrupar):", 6, 0)
        self.ent_grupo = ctk.CTkEntry(parent, placeholder_text="Ex: Coca-Cola 2L (Deixe igual p/ agrupar)")
        self.ent_grupo.grid(row=7, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="ew")
        self.dropdown_grupo = CTkFloatingDropdown(self.ent_grupo, self.lista_grupos, width=400) # Dropdown inteligente

        # EAN
        self.criar_input(parent, "Código de Barras (EAN):", 8, 0)
        self.ent_ean = ctk.CTkEntry(parent, placeholder_text="Escaneie aqui...", validate="key", validatecommand=vcmd_lista)
        self.ent_ean.grid(row=9, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="ew")

        # Categoria
        self.criar_input(parent, "Categoria:", 10, 0)
        self.ent_cat = ctk.CTkEntry(parent, placeholder_text="Selecione...")
        self.ent_cat.grid(row=11, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="ew")
        self.dropdown_cat = CTkFloatingDropdown(self.ent_cat, self.lista_categorias, width=400)

        # Valores
        self.criar_input(parent, "Custo (R$):", 12, 0)
        self.ent_custo = ctk.CTkEntry(parent, placeholder_text="0.00", validate="key", validatecommand=vcmd_dec)
        self.ent_custo.grid(row=13, column=0, padx=15, pady=(0, 10), sticky="ew")

        self.criar_input(parent, "Venda (R$):", 12, 1)
        self.ent_preco = ctk.CTkEntry(parent, placeholder_text="0.00", validate="key", validatecommand=vcmd_dec)
        self.ent_preco.grid(row=13, column=1, padx=15, pady=(0, 10), sticky="ew")

        # Estoque Mínimo e Switch
        self.criar_input(parent, "Estoque Mínimo:", 14, 0)
        self.ent_minimo = ctk.CTkEntry(parent, placeholder_text="Ex: 10", validate="key", validatecommand=vcmd_dec)
        self.ent_minimo.grid(row=15, column=0, padx=15, pady=(0, 10), sticky="ew")

        self.switch_controla = ctk.CTkSwitch(parent, text="Controlar Estoque")
        self.switch_controla.select()
        self.switch_controla.grid(row=15, column=1, padx=15, pady=(20, 10), sticky="w")

        ctk.CTkButton(parent, text="💾 SALVAR ITEM", fg_color="#27AE60", height=50, font=("Arial", 14, "bold"),
                      command=self.salvar).grid(row=16, column=0, columnspan=2, padx=15, pady=20, sticky="ew")

    def criar_input(self, p, t, r, c):
        ctk.CTkLabel(p, text=t, text_color="#ccc").grid(row=r, column=c, sticky="w", padx=15, pady=(5,0))

    def mostrar_ajuda(self):
        abrir_ajuda(self, "cadastro")

    def alternar_expansao(self):
        if not self.expandido:
            self.form_frame.grid_remove()
            self.list_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
            self.btn_expandir.configure(text="🗗 Restaurar Visão")
            self.expandido = True
        else:
            self.list_frame.grid(row=0, column=1, columnspan=1, sticky="nsew")
            self.form_frame.grid(row=0, column=0, sticky="nsew")
            self.btn_expandir.configure(text="⤢ Expandir Lista")
            self.expandido = False

    def salvar(self):
        raw_eans = self.ent_ean.get()
        lista_eans = [e.strip() for e in raw_eans.split(',') if e.strip()]

        dados = {
            "id": self.ent_cod.get().strip(),
            "nome": self.ent_nome.get().strip(),
            "grupo": self.ent_grupo.get().strip().upper(), # Salva o GRUPO em maiúsculo
            "codigos_barras": lista_eans,
            "categoria": self.ent_cat.get(),
            "unidade": self.combo_un.get(),
            "tipo": self.tipo_var.get(),
            "custo": self.ent_custo.get().replace(",", ".") or "0",
            "preco": self.ent_preco.get().replace(",", ".") or "0",
            "minimo": self.ent_minimo.get().replace(",", ".") or "0",
            "controla_estoque": bool(self.switch_controla.get())
        }

        if not dados["id"] or not dados["nome"]:
            messagebox.showwarning("Erro", "Campos obrigatórios (ID e Nome) vazios")
            return
        
        sucesso, mensagem = self.controller.salvar_produto(dados)
        
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self.limpar_form()
            self.atualizar_sistema()
        else:
            messagebox.showerror("Erro de Cadastro", mensagem)

    def limpar_form(self):
        for e in [self.ent_cod, self.ent_nome, self.ent_ean, self.ent_preco, self.ent_custo, self.ent_minimo, self.ent_cat, self.ent_grupo]: 
            e.delete(0, "end")
        self.tipo_var.set("PRODUTO")
        self.dropdown_cat.fechar_lista()
        self.dropdown_grupo.fechar_lista()

    def atualizar_lista(self, produtos_dict):
        self.produtos = produtos_dict
        for i in self.tree.get_children(): self.tree.delete(i)
        
        # Atualiza sugestões de grupos para o dropdown
        grupos_existentes = sorted(list(set(p.get('grupo', '') for p in produtos_dict.values() if p.get('grupo'))))
        self.lista_grupos = grupos_existentes
        self.dropdown_grupo.atualizar_dados(self.lista_grupos)

        for i, (cod, p) in enumerate(produtos_dict.items()):
            custo_fmt = formata_numeros_br(p.get('custo', 0), moeda=True)
            preco_fmt = formata_numeros_br(p.get('preco', 0), moeda=True)
            
            valores = (
                cod, 
                p['nome'], 
                p.get('grupo', '-'), # Mostra o Grupo na tabela
                f"R$ {custo_fmt}",
                f"R$ {preco_fmt}",
                p.get('categoria', '')
            )
            
            tag_linha = 'even' if i % 2 == 0 else 'odd'
            self.tree.insert("", "end", values=valores, tags=(tag_linha,))

    def perguntar_edicao(self, event):
        sel = self.tree.selection()
        if not sel: return
        
        cod = self.tree.item(sel[0], "values")[0]
        p = self.produtos.get(cod)
        if not p: return

        resposta = messagebox.askyesno("Editar Item", f"Deseja carregar os dados de '{p['nome']}' para edição?")
        
        if resposta:
            self.carregar_edicao(cod)
        else:
            self.tree.selection_remove(sel[0])

    def carregar_edicao(self, cod):
        p = self.produtos.get(cod)
        if p:
            self.limpar_form()
            self.ent_cod.insert(0, cod)
            self.ent_nome.insert(0, p['nome'])
            self.ent_grupo.insert(0, p.get('grupo', '')) # Carrega o Grupo
            
            eans = p.get('codigos_barras', [])
            if isinstance(eans, list):
                self.ent_ean.insert(0, ", ".join(eans))
            elif eans:
                self.ent_ean.insert(0, str(eans))
            
            self.ent_preco.insert(0, p.get('preco', 0))
            self.ent_custo.insert(0, p.get('custo', 0))
            self.ent_minimo.insert(0, p.get('estoque_minimo', 0))
            self.combo_un.set(p.get('unidade', 'UN'))
            self.ent_cat.insert(0, p.get('categoria', 'Outros'))
            self.tipo_var.set(p.get('tipo', 'PRODUTO'))
            if p.get('controla_estoque', True): self.switch_controla.select()
            else: self.switch_controla.deselect()
            
            if self.expandido:
                self.alternar_expansao()

    def configurar_ordenacao(self):
        colunas = ["cod", "nome", "grupo", "custo", "venda", "cat"]
        for col in colunas:
            self.tree.heading(col, command=lambda c=col: self.ordenar_treeview(c, False))

    def ordenar_treeview(self, col, reverse):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        try:
            l.sort(key=lambda t: float(t[0].replace('R$', '').replace('.', '').replace(',', '.').strip()), reverse=reverse)
        except ValueError:
            l.sort(reverse=reverse)
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)
            tag_linha = 'even' if index % 2 == 0 else 'odd'
            self.tree.item(k, tags=(tag_linha,))
        self.tree.heading(col, command=lambda: self.ordenar_treeview(col, not reverse))