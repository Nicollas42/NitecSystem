# view_estoque.py
import customtkinter as ctk
from tkinter import ttk, messagebox
import database

class EstoqueFrame(ctk.CTkFrame):
    def __init__(self, master, callback_voltar):
        super().__init__(master)
        self.voltar_menu = callback_voltar
        
        # Carrega dados
        self.produtos = database.carregar_produtos()
        
        # Prepara listas para os Selects
        self.atualizar_listas_auxiliares()

        self.montar_layout()
        self.atualizar_tabela()

    def atualizar_listas_auxiliares(self):
        """Cria listas ordenadas para os ComboBoxes"""
        self.lista_codigos = sorted(list(self.produtos.keys()))
        
        # Mapa reverso para achar código pelo nome
        self.mapa_nomes = {prod['nome']: cod for cod, prod in self.produtos.items()}
        self.lista_nomes = sorted(list(self.mapa_nomes.keys()))

    def montar_layout(self):
        # 1. CABEÇALHO
        top = ctk.CTkFrame(self, height=50, corner_radius=0)
        top.pack(fill="x", side="top")
        
        ctk.CTkButton(top, text="🔙 Voltar", width=100, fg_color="#555", 
                      command=self.voltar_menu).pack(side="left", padx=(10, 5), pady=10)
        
        ctk.CTkButton(top, text="?", width=30, fg_color="#333", hover_color="#444", 
                      command=self.mostrar_ajuda).pack(side="left", padx=5)

        ctk.CTkLabel(top, text="GESTÃO DE ESTOQUE", font=("Arial", 16, "bold")).pack(side="left", padx=20)

        # 2. FORMULÁRIO INTELIGENTE
        form = ctk.CTkFrame(self)
        form.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(form, text="Cadastro / Entrada de Mercadoria", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=10)

        # --- CÓDIGO (AGORA É COMBOBOX) ---
        ctk.CTkLabel(form, text="Código:").grid(row=1, column=0, padx=10, sticky="w")
        self.combo_cod = ctk.CTkComboBox(form, width=100, 
                                         values=self.lista_codigos,
                                         command=self.ao_escolher_codigo)
        self.combo_cod.set("")
        self.combo_cod.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")

        # --- NOME (AGORA É COMBOBOX) ---
        ctk.CTkLabel(form, text="Nome:").grid(row=1, column=1, padx=10, sticky="w")
        self.combo_nome = ctk.CTkComboBox(form, width=250, 
                                          values=self.lista_nomes,
                                          command=self.ao_escolher_nome)
        self.combo_nome.set("")
        self.combo_nome.grid(row=2, column=1, padx=10, pady=(0, 10), sticky="ew")

        # Preço
        ctk.CTkLabel(form, text="Preço (R$):").grid(row=1, column=2, padx=10, sticky="w")
        self.entry_preco = ctk.CTkEntry(form, placeholder_text="0.00", width=100)
        self.entry_preco.grid(row=2, column=2, padx=10, pady=(0, 10), sticky="ew")

        # Unidade
        ctk.CTkLabel(form, text="Un:").grid(row=1, column=3, padx=10, sticky="w")
        self.combo_un = ctk.CTkComboBox(form, values=["UN", "KG", "G"], width=70)
        self.combo_un.grid(row=2, column=3, padx=10, pady=(0, 10))

        # Estoque
        ctk.CTkLabel(form, text="Estoque Atual:").grid(row=1, column=4, padx=10, sticky="w")
        
        frame_est = ctk.CTkFrame(form, fg_color="transparent")
        frame_est.grid(row=2, column=4, padx=10, pady=(0, 10), sticky="w")
        
        self.entry_estoque = ctk.CTkEntry(frame_est, placeholder_text="0", width=80)
        self.entry_estoque.pack(side="left")
        
        # Botão Somar (+)
        ctk.CTkButton(frame_est, text="➕", width=30, fg_color="#2980B9", 
                      command=self.somar_estoque).pack(side="left", padx=5)

        # Botões de Ação
        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.grid(row=2, column=5, padx=10)

        ctk.CTkButton(btn_frame, text="SALVAR DADOS", fg_color="#27AE60", width=120, 
                      command=self.salvar_produto_sobrescrever).pack(side="left", padx=5)
        
        ctk.CTkButton(btn_frame, text="EXCLUIR", fg_color="#C0392B", width=100, 
                      command=self.excluir_produto).pack(side="left", padx=5)

        # 3. TABELA
        lista_frame = ctk.CTkFrame(self)
        lista_frame.pack(fill="both", expand=True, padx=20, pady=10)

        cols = ("cod", "nome", "preco", "un", "est")
        self.tree = ttk.Treeview(lista_frame, columns=cols, show="headings", selectmode="browse")
        
        self.tree.heading("cod", text="CÓDIGO")
        self.tree.heading("nome", text="NOME")
        self.tree.heading("preco", text="R$ UNIT")
        self.tree.heading("un", text="UN")
        self.tree.heading("est", text="ESTOQUE ATUAL")

        self.tree.column("cod", width=80, anchor="center")
        self.tree.column("nome", width=350)
        self.tree.column("preco", width=100, anchor="e")
        self.tree.column("un", width=60, anchor="center")
        self.tree.column("est", width=120, anchor="center")

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.ao_selecionar_tabela)

    # --- LÓGICA DE AUTO-PREENCHIMENTO ---
    
    def ao_escolher_codigo(self, codigo_escolhido):
        """Chamado quando usuário seleciona um CÓDIGO na lista"""
        if codigo_escolhido in self.produtos:
            self.preencher_formulario(codigo_escolhido)
            
    def ao_escolher_nome(self, nome_escolhido):
        """Chamado quando usuário seleciona um NOME na lista"""
        if nome_escolhido in self.mapa_nomes:
            codigo = self.mapa_nomes[nome_escolhido]
            self.preencher_formulario(codigo)

    def preencher_formulario(self, cod):
        """Preenche todos os campos com base no código"""
        dados = self.produtos[cod]
        
        # Evita loop infinito de atualização (se já estiver preenchido)
        if self.combo_cod.get() != cod:
            self.combo_cod.set(cod)
            
        if self.combo_nome.get() != dados['nome']:
            self.combo_nome.set(dados['nome'])

        self.entry_preco.delete(0, "end")
        self.entry_preco.insert(0, f"{dados['preco']:.2f}")
        
        self.combo_un.set(dados['un'])
        
        self.entry_estoque.delete(0, "end")
        self.entry_estoque.insert(0, f"{dados.get('estoque', 0)}")

    # --- SALVAR E MANIPULAR DADOS ---

    def salvar_produto_sobrescrever(self):
        cod = self.combo_cod.get().strip() # Pega do ComboBox
        nome = self.combo_nome.get().strip() # Pega do ComboBox
        preco_txt = self.entry_preco.get().replace(",", ".")
        est_txt = self.entry_estoque.get().replace(",", ".")
        un = self.combo_un.get()

        if not cod or not nome or not preco_txt:
            messagebox.showwarning("Aviso", "Preencha Código, Nome e Preço!")
            return

        try:
            preco = float(preco_txt)
            estoque = float(est_txt) if est_txt else 0.0
        except ValueError:
            messagebox.showerror("Erro", "Números inválidos.")
            return

        # Aviso de alteração manual de estoque
        if cod in self.produtos:
            est_antigo = self.produtos[cod].get("estoque", 0)
            if estoque != est_antigo:
                if not messagebox.askyesno("Correção", f"Alterar estoque de {est_antigo} para {estoque}?"):
                    return

        self.produtos[cod] = {"nome": nome, "preco": preco, "un": un, "estoque": estoque}
        database.salvar_produtos(self.produtos)
        
        messagebox.showinfo("Sucesso", "Salvo!")
        
        # Atualiza listas (caso seja um produto novo)
        self.atualizar_listas_auxiliares()
        self.combo_cod.configure(values=self.lista_codigos)
        self.combo_nome.configure(values=self.lista_nomes)
        
        self.limpar_form()
        self.atualizar_tabela()

    def somar_estoque(self):
        cod = self.combo_cod.get().strip()
        qtd_entrada_txt = self.entry_estoque.get().replace(",", ".")

        if not cod or cod not in self.produtos:
            messagebox.showwarning("Aviso", "Selecione um produto cadastrado.")
            return

        try:
            qtd_entrada = float(qtd_entrada_txt)
            if qtd_entrada <= 0: raise ValueError
        except:
            messagebox.showerror("Erro", "Quantidade inválida.")
            return

        nome = self.produtos[cod]['nome']
        atual = self.produtos[cod].get('estoque', 0)
        novo = atual + qtd_entrada

        if messagebox.askyesno("Adicionar Estoque", f"Produto: {nome}\nAtual: {atual}\nEntrada: +{qtd_entrada}\nNovo: {novo}"):
            self.produtos[cod]['estoque'] = novo
            database.salvar_produtos(self.produtos)
            messagebox.showinfo("Sucesso", "Estoque adicionado!")
            self.limpar_form()
            self.atualizar_tabela()

    def excluir_produto(self):
        cod = self.combo_cod.get().strip()
        if not cod: return
        if cod in self.produtos:
            if messagebox.askyesno("Confirmar", f"Excluir '{self.produtos[cod]['nome']}'?"):
                del self.produtos[cod]
                database.salvar_produtos(self.produtos)
                
                # Atualiza listas
                self.atualizar_listas_auxiliares()
                self.combo_cod.configure(values=self.lista_codigos)
                self.combo_nome.configure(values=self.lista_nomes)
                
                self.limpar_form()
                self.atualizar_tabela()

    def atualizar_tabela(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for cod, dados in self.produtos.items():
            est = dados.get("estoque", 0)
            if dados['un'] in ['KG', 'G']: est_fmt = f"{est:.3f}"
            else: est_fmt = f"{int(est)}"
            self.tree.insert("", "end", values=(cod, dados['nome'], f"{dados['preco']:.2f}", dados['un'], est_fmt))

    def ao_selecionar_tabela(self, event):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel[0], "values")
        # Chama o preenchedor usando o código (item[0])
        self.preencher_formulario(item[0])

    def limpar_form(self):
        self.combo_cod.set("")
        self.combo_nome.set("")
        self.entry_preco.delete(0, "end")
        self.entry_estoque.delete(0, "end")
        self.combo_un.set("UN")

    def mostrar_ajuda(self):
        msg = """
        📦 GESTÃO INTELIGENTE

        🔍 Busca Rápida:
        - Clique em 'Código' ou 'Nome' para selecionar um produto existente.
        - Os dados serão preenchidos automaticamente.

        ➕ Adicionar Estoque:
        1. Selecione o produto.
        2. Digite a quantidade que CHEGOU (ex: 50).
        3. Clique no botão azul (+).
        """
        messagebox.showinfo("Ajuda - Estoque", msg)