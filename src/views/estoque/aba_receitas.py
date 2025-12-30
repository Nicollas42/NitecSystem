import customtkinter as ctk
from tkinter import ttk, messagebox
from .sub_receitas.tab_ingredientes import TabIngredientes
from .sub_receitas.tab_maquinas import TabMaquinas
from .sub_receitas.tab_financeiro import TabFinanceiro

class AbaReceitas(ctk.CTkFrame):
    def __init__(self, master, controller, produtos_ref, callback_atualizar):
        super().__init__(master)
        self.controller = controller
        self.produtos = produtos_ref
        self.callback_atualizar = callback_atualizar
        
        self.id_produto_atual = None
        self.montar_layout()

    def montar_layout(self):
        self.columnconfigure(0, weight=1); self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)

        # ESQUERDA: LISTA
        frame_esq = ctk.CTkFrame(self, fg_color="#2b2b2b")
        frame_esq.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(frame_esq, text="Selecione o Produto", font=("Arial", 14, "bold"), text_color="#2CC985").pack(pady=10)
        
        self.lista_produtos = ttk.Treeview(frame_esq, columns=("nome",), show="headings")
        self.lista_produtos.heading("nome", text="Produtos (Internos)")
        self.lista_produtos.pack(fill="both", expand=True, padx=5, pady=5)
        self.lista_produtos.bind("<<TreeviewSelect>>", self.carregar_produto)

        # DIREITA: ABAS
        frame_dir = ctk.CTkFrame(self)
        frame_dir.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.lbl_selecao = ctk.CTkLabel(frame_dir, text="Nenhum Produto Selecionado", font=("Arial", 18, "bold"))
        self.lbl_selecao.pack(pady=10, anchor="w", padx=20)

        self.tabs = ctk.CTkTabview(frame_dir)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Instancia Módulos
        self.modulo_ing = TabIngredientes(self.tabs.add("🍎 Ingredientes"), self.produtos, self.recalcular_custos_tempo_real)
        self.modulo_ing.pack(fill="both", expand=True)
        
        self.modulo_maq = TabMaquinas(self.tabs.add("⚙️ Máquinas"), self.controller)
        self.modulo_maq.pack(fill="both", expand=True)
        
        self.modulo_fin = TabFinanceiro(self.tabs.add("💰 Precificação"), self.salvar_tudo, self.ao_alterar_financeiro)
        self.modulo_fin.pack(fill="both", expand=True)

    def ao_alterar_financeiro(self, event=None):
        self.recalcular_custos_tempo_real()

    def atualizar(self):
        # Atualiza lista lateral e combos
        self.lista_produtos.delete(*self.lista_produtos.get_children())
        insumos = []
        
        for cod, p in self.produtos.items():
            tipo = p.get('tipo', 'PRODUTO')
            
            # Lista da Esquerda: Apenas produtos fabricados (Internos)
            if tipo == 'INTERNO':
                self.lista_produtos.insert("", "end", values=(p['nome'],), tags=(str(cod),))
            
            # Dropdown de Ingredientes: APENAS TIPO 'INSUMO'
            if tipo == 'INSUMO':
                insumos.append(p['nome'])
        
        self.modulo_ing.atualizar_dropdown(sorted(insumos))
        self.modulo_maq.carregar_combo() 

    def carregar_produto(self, event):
        try:
            sel = self.lista_produtos.selection()
            if not sel: return
            
            tag_valor = self.lista_produtos.item(sel[0])['tags'][0]
            cod = str(tag_valor) 

            self.id_produto_atual = cod
            
            if cod not in self.produtos:
                print(f"ERRO: Produto ID {cod} não encontrado no dicionário self.produtos")
                return

            nome_prod = self.produtos[cod]['nome']
            self.lbl_selecao.configure(text=f"Editando: {nome_prod}")
            
            receitas_db = self.controller.carregar_receitas()
            rec = receitas_db.get(cod, {})
            
            self.modulo_ing.atualizar_dados(rec.get('ingredientes', []))
            self.modulo_maq.atualizar_dados(rec.get('maquinas_uso', []), rec.get('tempo_preparo', 60))
            self.modulo_fin.set_valores(rec.get('rendimento', 1), rec.get('margem_lucro', 100))
            
            self.recalcular_custos_tempo_real()
            
        except Exception as e:
            print(f"ERRO CRÍTICO ao carregar produto: {e}")
            import traceback
            traceback.print_exc()

    def recalcular_custos_tempo_real(self):
        if not self.id_produto_atual: return

        ingredientes = self.modulo_ing.ingredientes_lista
        maquinas = self.modulo_maq.maquinas_lista
        try: tempo_homem = float(self.modulo_maq.get_tempo_humano())
        except: tempo_homem = 0.0
        
        tarifas = self.controller.carregar_tarifas()
        bd_maquinas = self.controller.carregar_maquinas()

        custo_insumos = sum(float(i.get('custo_aprox', 0)) for i in ingredientes)

        custo_maquinas = 0.0
        for uso in maquinas:
            maq = bd_maquinas.get(uso['id'])
            if maq:
                tempo_h = float(uso['tempo_min']) / 60.0
                kwh = (maq['potencia_w'] / 1000) * tempo_h
                custo_luz = kwh * tarifas['energia_kwh']
                gas_kg = maq['gas_kg_h'] * tempo_h
                custo_gas = gas_kg * tarifas['gas_kg']
                custo_maquinas += (custo_luz + custo_gas)

        custo_mod = (tempo_homem / 60.0) * tarifas['mao_obra_h']
        custo_total = custo_insumos + custo_maquinas + custo_mod
        
        try: rendimento = self.modulo_fin.get_rendimento()
        except: rendimento = 1
        
        custo_unit = custo_total / rendimento if rendimento > 0 else 0
        
        try: margem = self.modulo_fin.get_margem() / 100.0
        except: margem = 0
        
        preco_sug = custo_unit * (1 + margem)

        self.modulo_fin.atualizar_resumo(
            custo_insumos,
            custo_maquinas + custo_mod,
            custo_total,
            custo_unit,
            preco_sug
        )

    def salvar_tudo(self):
        if not self.id_produto_atual: return
        
        ok, msg = self.controller.salvar_receita_avancada(
            self.id_produto_atual,
            self.modulo_fin.get_rendimento(),
            self.modulo_ing.ingredientes_lista,
            self.modulo_maq.maquinas_lista,
            self.modulo_maq.get_tempo_humano(),
            self.modulo_fin.get_margem()
        )
        if ok:
            messagebox.showinfo("Sucesso", msg)
            self.callback_atualizar()
        else:
            messagebox.showerror("Erro", msg)