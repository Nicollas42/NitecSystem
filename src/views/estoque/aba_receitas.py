# src/views/estoque/aba_receitas.py
import customtkinter as ctk
from tkinter import ttk, messagebox

class AbaReceitas(ctk.CTkFrame):
    def __init__(self, master, controller, produtos_ref, callback_atualizar):
        super().__init__(master)
        self.controller = controller
        self.produtos = produtos_ref
        self.callback_atualizar = callback_atualizar
        
        self.ingredientes_temp = [] 
        
        self.montar_layout()

    def montar_layout(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        # ESQUERDA
        frame_esq = ctk.CTkFrame(self, fg_color="#2b2b2b")
        frame_esq.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(frame_esq, text="1. Escolha o Produto", font=("Arial", 14, "bold"), text_color="#2CC985").pack(pady=10)
        
        self.lista_produtos = ttk.Treeview(frame_esq, columns=("nome",), show="headings")
        self.lista_produtos.heading("nome", text="Produtos Finais")
        self.lista_produtos.pack(fill="both", expand=True, padx=10, pady=10)
        self.lista_produtos.bind("<<TreeviewSelect>>", self.carregar_receita_existente)

        # DIREITA
        frame_dir = ctk.CTkFrame(self)
        frame_dir.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        f_head = ctk.CTkFrame(frame_dir, fg_color="transparent")
        f_head.pack(fill="x", padx=10, pady=10)
        
        self.lbl_produto_selecionado = ctk.CTkLabel(f_head, text="Nenhum Produto Selecionado", font=("Arial", 18, "bold"))
        self.lbl_produto_selecionado.pack(anchor="w")

        f_rend = ctk.CTkFrame(f_head, fg_color="transparent")
        f_rend.pack(fill="x", pady=5)
        ctk.CTkLabel(f_rend, text="Rendimento da Receita (Qtd Produzida):").pack(side="left")
        self.ent_rendimento = ctk.CTkEntry(f_rend, width=80, placeholder_text="Ex: 10")
        self.ent_rendimento.pack(side="left", padx=10)
        self.lbl_unidade_rend = ctk.CTkLabel(f_rend, text="UN")
        self.lbl_unidade_rend.pack(side="left")

        # Adicionar Ingrediente
        f_add = ctk.CTkFrame(frame_dir, border_width=1, border_color="#444")
        f_add.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(f_add, text="2. Adicionar Insumo", font=("Arial", 12, "bold"), text_color="#E67E22").pack(pady=5)
        
        self.combo_insumos = ctk.CTkComboBox(f_add, width=250, values=[])
        self.combo_insumos.pack(side="left", padx=10, pady=10)
        
        self.ent_qtd_ing = ctk.CTkEntry(f_add, width=80, placeholder_text="Qtd")
        self.ent_qtd_ing.pack(side="left", padx=5)
        
        self.lbl_un_ing = ctk.CTkLabel(f_add, text="UN")
        self.lbl_un_ing.pack(side="left", padx=5)

        ctk.CTkButton(f_add, text="+", width=40, fg_color="#27AE60", command=self.adicionar_ingrediente).pack(side="left", padx=10)

        # Lista
        self.tree_ing = ttk.Treeview(frame_dir, columns=("nome", "qtd", "custo"), show="headings", height=8)
        self.tree_ing.heading("nome", text="Insumo")
        self.tree_ing.heading("qtd", text="Qtd")
        self.tree_ing.heading("custo", text="Custo Est. (R$)")
        self.tree_ing.column("qtd", width=60, anchor="center")
        self.tree_ing.column("custo", width=100, anchor="center")
        self.tree_ing.pack(fill="both", expand=True, padx=10)

        f_footer = ctk.CTkFrame(frame_dir, height=50, fg_color="#333")
        f_footer.pack(fill="x", side="bottom")
        
        self.lbl_custo_total = ctk.CTkLabel(f_footer, text="Custo Total: R$ 0.00", font=("Arial", 14))
        self.lbl_custo_total.pack(side="left", padx=20, pady=15)
        
        ctk.CTkButton(f_footer, text="💾 SALVAR FICHA TÉCNICA", fg_color="#2980B9", 
                      command=self.salvar_receita).pack(side="right", padx=20, pady=10)

        self.combo_insumos.configure(command=self.atualizar_unidade_insumo)

    def atualizar(self):
        self.lista_produtos.delete(*self.lista_produtos.get_children())
        insumos = []
        for cod, p in self.produtos.items():
            if p.get('tipo') == 'PRODUTO':
                self.lista_produtos.insert("", "end", values=(p['nome'],), tags=(cod,))
            elif p.get('tipo') == 'INSUMO':
                insumos.append(p['nome'])
        self.combo_insumos.configure(values=sorted(insumos))

    def atualizar_unidade_insumo(self, escolha):
        for cod, p in self.produtos.items():
            if p['nome'] == escolha:
                self.lbl_un_ing.configure(text=p.get('unidade', 'UN'))
                break

    def carregar_receita_existente(self, event):
        sel = self.lista_produtos.selection()
        if not sel: return
        item = self.lista_produtos.item(sel[0])
        
        # --- CORREÇÃO AQUI: Forçar conversão para STRING ---
        cod_prod = str(item['tags'][0]) 
        # ---------------------------------------------------
        
        nome_prod = item['values'][0]
        
        self.lbl_produto_selecionado.configure(text=f"Receita: {nome_prod}")
        self.id_produto_atual = cod_prod
        
        # Agora o acesso ao dicionário é seguro
        if cod_prod in self.produtos:
            self.lbl_unidade_rend.configure(text=self.produtos[cod_prod].get('unidade', 'UN'))
        
        self.ingredientes_temp = []
        self.ent_rendimento.delete(0, "end")
        
        todas_receitas = self.controller.carregar_receitas()
        if cod_prod in todas_receitas:
            rec = todas_receitas[cod_prod]
            self.ent_rendimento.insert(0, rec.get('rendimento', 1))
            self.ingredientes_temp = rec.get('ingredientes', [])
        
        self.renderizar_ingredientes()

    def adicionar_ingrediente(self):
        nome = self.combo_insumos.get()
        qtd = self.ent_qtd_ing.get().replace(",", ".")
        if not nome or not qtd: return
        
        id_insumo = next((k for k, v in self.produtos.items() if v['nome'] == nome), None)
        if not id_insumo: return

        self.ingredientes_temp.append({
            "id": id_insumo,
            "nome": nome,
            "qtd": float(qtd)
        })
        self.ent_qtd_ing.delete(0, "end")
        self.renderizar_ingredientes()

    def renderizar_ingredientes(self):
        self.tree_ing.delete(*self.tree_ing.get_children())
        custo_total = 0.0
        for ing in self.ingredientes_temp:
            p_insumo = self.produtos.get(str(ing['id']), {}) # Garante str aqui também
            custo_unit = p_insumo.get('custo', 0.0)
            subtotal = custo_unit * ing['qtd']
            custo_total += subtotal
            self.tree_ing.insert("", "end", values=(ing['nome'], ing['qtd'], f"R$ {subtotal:.2f}"))

        self.lbl_custo_total.configure(text=f"Custo dos Ingredientes: R$ {custo_total:.2f}")

    def salvar_receita(self):
        if not hasattr(self, 'id_produto_atual'): return
        rend = self.ent_rendimento.get().replace(",", ".")
        if not rend: 
            messagebox.showerror("Erro", "Defina o rendimento.")
            return
            
        ok, msg = self.controller.salvar_receita(
            str(self.id_produto_atual), # Garante envio como string
            rend,
            self.ingredientes_temp
        )
        if ok:
            messagebox.showinfo("Sucesso", msg)
            self.callback_atualizar()