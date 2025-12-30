import customtkinter as ctk
from tkinter import ttk
from src.utils.componentes_estilizados import CTkFloatingDropdown
from src.utils.formata_numeros_br import formata_numeros_br

class TabIngredientes(ctk.CTkFrame):
    def __init__(self, master, produtos_ref, callback_alteracao=None):
        super().__init__(master, fg_color="transparent")
        self.produtos = produtos_ref
        self.callback_alteracao = callback_alteracao 
        self.ingredientes_lista = [] 
        self.item_em_edicao_index = None 
        self.montar_layout()

    def montar_layout(self):
        f_add = ctk.CTkFrame(self, fg_color="transparent")
        f_add.pack(fill="x", pady=5)
        
        self.ent_insumo = ctk.CTkEntry(f_add, placeholder_text="Buscar Insumo...", width=200)
        self.ent_insumo.pack(side="left", padx=5)
        self.dropdown_insumos = CTkFloatingDropdown(self.ent_insumo, [], width=300)
        
        self.ent_qtd = ctk.CTkEntry(f_add, placeholder_text="Qtd", width=60)
        self.ent_qtd.pack(side="left", padx=5)
        
        self.btn_acao = ctk.CTkButton(f_add, text="+ Add", width=80, command=self.confirmar_item)
        self.btn_acao.pack(side="left", padx=5)

        self.tree = ttk.Treeview(self, columns=("nome", "qtd", "un", "custo"), show="headings", height=10)
        self.tree.heading("nome", text="Insumo"); self.tree.column("nome", width=220)
        self.tree.heading("qtd", text="Qtd"); self.tree.column("qtd", width=60, anchor="center")
        self.tree.heading("un", text="Un"); self.tree.column("un", width=50, anchor="center")
        self.tree.heading("custo", text="Custo Est."); self.tree.column("custo", width=80, anchor="center")
        self.tree.pack(fill="both", expand=True, pady=5)
        
        self.tree.bind("<<TreeviewSelect>>", self.ao_selecionar)
        
        ctk.CTkButton(self, text="Remover Selecionado", fg_color="#C0392B", height=25, 
                      command=self.remover).pack(pady=5)

    def atualizar_dados(self, dados_ingredientes):
        print(f"DEBUG [TabIngredientes]: Recebendo lista com {len(dados_ingredientes)} itens.")
        self.ingredientes_lista = dados_ingredientes
        self.limpar_campos()
        self.renderizar()

    def atualizar_dropdown(self, lista_nomes):
        self.dropdown_insumos.atualizar_dados(lista_nomes)

    def ao_selecionar(self, event):
        sel = self.tree.selection()
        if not sel: return
        idx = self.tree.index(sel[0])
        self.item_em_edicao_index = idx
        item = self.ingredientes_lista[idx]
        print(f"DEBUG [TabIngredientes]: Selecionado para editar: {item['nome']}")
        
        self.ent_insumo.delete(0, 'end'); self.ent_insumo.insert(0, item['nome'])
        self.ent_qtd.delete(0, 'end'); self.ent_qtd.insert(0, str(item['qtd']))
        self.btn_acao.configure(text="Atualizar", fg_color="#F39C12")

    def confirmar_item(self):
        nome = self.ent_insumo.get()
        qtd_str = self.ent_qtd.get().replace(",", ".")
        print(f"DEBUG [TabIngredientes]: Tentando adicionar '{nome}' qtd '{qtd_str}'")
        
        item_db = next((v for k,v in self.produtos.items() if v['nome'] == nome), None)
        
        if not item_db:
            print(f"DEBUG [TabIngredientes]: ERRO - Item '{nome}' não encontrado no banco de produtos.")
            return

        if item_db and qtd_str:
            try:
                qtd_float = float(qtd_str)
                custo_unit = float(item_db.get('custo', 0))
                custo_tot = custo_unit * qtd_float
                
                novo_dado = {
                    "id": item_db['id'], 
                    "nome": nome, 
                    "qtd": qtd_float,
                    "un": item_db.get('unidade', 'UN'),
                    "custo_aprox": custo_tot
                }

                if self.item_em_edicao_index is not None:
                    self.ingredientes_lista[self.item_em_edicao_index] = novo_dado
                else:
                    self.ingredientes_lista.append(novo_dado)
                
                print(f"DEBUG [TabIngredientes]: Item processado com sucesso. Total lista: {len(self.ingredientes_lista)}")
                self.renderizar()
                self.limpar_campos()
                if self.callback_alteracao: self.callback_alteracao()
                
            except ValueError as e:
                print(f"DEBUG [TabIngredientes]: Erro de valor: {e}")

    def limpar_campos(self):
        self.ent_insumo.delete(0, 'end')
        self.ent_qtd.delete(0, 'end')
        self.dropdown_insumos.fechar_lista()
        self.item_em_edicao_index = None
        self.btn_acao.configure(text="+ Add", fg_color="#3B8ED0")
        if self.tree.selection(): self.tree.selection_remove(self.tree.selection()[0])

    def remover(self):
        sel = self.tree.selection()
        if sel:
            idx = self.tree.index(sel[0])
            del self.ingredientes_lista[idx]
            self.renderizar()
            self.limpar_campos()
            if self.callback_alteracao: self.callback_alteracao()

    def renderizar(self):
        print("DEBUG [TabIngredientes]: Renderizando tabela...")
        for i in self.tree.get_children(): self.tree.delete(i)
        for ing in self.ingredientes_lista:
            c = formata_numeros_br(ing.get('custo_aprox', 0), True)
            un = ing.get('un', 'UN')
            self.tree.insert("", "end", values=(ing['nome'], ing['qtd'], un, c))