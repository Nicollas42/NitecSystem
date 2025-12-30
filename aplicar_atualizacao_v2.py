import os

# --- CONTEÚDO CORRIGIDO: estoque_controller.py ---
# Correção: Lógica de 'in' para detectar ENTRADA_PRODUCAO corretamente
controller_code = """
# src/controllers/estoque_controller.py
import datetime
from src.models import database

# Constantes de Movimentação
TIPO_ENTRADA_COMPRA = "ENTRADA_COMPRA" 
TIPO_SAIDA_VENDA = "SAIDA_VENDA"
TIPO_SAIDA_PRODUCAO = "SAIDA_PRODUCAO" 
TIPO_ENTRADA_PRODUCAO = "ENTRADA_PRODUCAO" 
TIPO_AJUSTE_PERDA = "SAIDA_PERDA"
TIPO_AJUSTE_SOBRA = "ENTRADA_AJUSTE"

class EstoqueController:
    def __init__(self):
        self.db = database

    def salvar_produto(self, dados_produto):
        produtos = self.db.carregar_produtos()
        cod = dados_produto['id']

        # Preserva saldos se existir
        estoque_frente = produtos[cod].get('estoque_atual', 0.0) if cod in produtos else 0.0
        estoque_fundo = produtos[cod].get('estoque_fundo', 0.0) if cod in produtos else 0.0

        novo_produto = {
            "id": cod,
            "nome": dados_produto['nome'].strip().upper(),
            "unidade": dados_produto.get('unidade', 'UN'), 
            "categoria": dados_produto.get('categoria', 'Outros'),
            "tipo": dados_produto.get('tipo', 'PRODUTO'),          # CAMPO NOVO
            "controla_estoque": dados_produto.get('controla_estoque', True),
            "estoque_atual": estoque_frente, 
            "estoque_fundo": estoque_fundo,
            "estoque_minimo": float(str(dados_produto.get('minimo', 0)).replace(',', '.')),
            "preco": float(str(dados_produto.get('preco', 0)).replace(',', '.')),
            "custo": float(str(dados_produto.get('custo', 0)).replace(',', '.')), # CAMPO NOVO
            "ativo": True
        }
        produtos[cod] = novo_produto
        self.db.salvar_produtos(produtos)
        return True

    def transferir_fundo_para_frente(self, produto_id, qtd, usuario="admin", motivo=None):
        produtos = self.db.carregar_produtos()
        
        if produto_id not in produtos:
            return False, "Produto não encontrado."
            
        prod = produtos[produto_id]
        try:
            qtd_num = float(str(qtd).replace(',', '.'))
        except:
            return False, "Quantidade inválida."

        saldo_fundo = prod.get('estoque_fundo', 0.0)
        saldo_frente = prod.get('estoque_atual', 0.0)

        if saldo_fundo < qtd_num:
            return False, f"Saldo insuficiente no FUNDO ({saldo_fundo})."

        prod['estoque_fundo'] = round(saldo_fundo - qtd_num, 4)
        prod['estoque_atual'] = round(saldo_frente + qtd_num, 4)
        
        self.db.salvar_produtos(produtos)
        
        motivo_final = motivo if motivo else "Fundo -> Frente"

        self.db.registrar_movimentacao(
            "TRANSFERENCIA", produto_id, prod['nome'], qtd_num, 
            motivo_final, usuario, saldo_frente, prod['estoque_atual']
        )
        
        return True, f"Transferência de {qtd_num} realizada!"
    
    def movimentar_estoque(self, produto_id, qtd, tipo_mov, motivo="", usuario="Admin", local="fundo"):
        produtos = self.db.carregar_produtos()
        if produto_id not in produtos:
            return False, "Produto não encontrado."
            
        prod = produtos[produto_id]
        chave_estoque = 'estoque_atual' if local == "frente" else 'estoque_fundo'
        
        try:
            qtd_num = float(str(qtd).replace(',', '.'))
        except:
            return False, "Quantidade inválida."

        saldo_anterior = prod.get(chave_estoque, 0.0)
        
        # --- CORREÇÃO IMPORTANTE AQUI ---
        # Verifica se 'ENTRADA' está na string (serve para ENTRADA, ENTRADA_COMPRA, ENTRADA_PRODUCAO)
        if "ENTRADA" in tipo_mov.upper():
            novo_saldo = saldo_anterior + qtd_num
        else: # SAIDA, PERDA, SAIDA_PRODUCAO
            novo_saldo = saldo_anterior - qtd_num
        # --------------------------------

        prod[chave_estoque] = round(novo_saldo, 4)
        self.db.salvar_produtos(produtos)
        
        self.db.registrar_movimentacao(
            f"{tipo_mov}_{local.upper()}", produto_id, prod['nome'], qtd_num, 
            motivo, usuario, saldo_anterior, novo_saldo
        )
        
        return True, f"{tipo_mov} realizada. Novo saldo: {novo_saldo}"
    
    def registrar_producao(self, id_produto_final, qtd_produzida, usuario):
        try:
            # Carrega receitas (Fichas Técnicas)
            # Nota: Isso assume que você vai criar um arquivo de receitas futuramente
            fichas = self.db.carregar_json(self.db.ARQ_SOBRAS.replace("sobras.json", "receitas.json")) 
            
            if id_produto_final not in fichas:
                # Se não tiver receita, apenas dá entrada no produto final (produção manual)
                self.movimentar_estoque(id_produto_final, qtd_produzida, TIPO_ENTRADA_PRODUCAO, "Produção Avulsa", usuario, "fundo")
                return True, "Produção registrada (Sem baixa de insumos - Receita não encontrada)"
                
            receita = fichas[id_produto_final]
            rendimento = float(receita.get('rendimento', 1))
            fator = float(qtd_produzida) / rendimento
            
            # Baixa os insumos
            for ing in receita['ingredientes']:
                qtd_nec = float(ing['qtd']) * fator
                # TIPO_SAIDA_PRODUCAO vai cair no 'else' do movimentar_estoque (subtrair)
                self.movimentar_estoque(ing['id'], qtd_nec, TIPO_SAIDA_PRODUCAO, f"Prod. {id_produto_final}", usuario, "fundo")
            
            # Entrada do produto final
            # TIPO_ENTRADA_PRODUCAO vai cair no 'if "ENTRADA" in...' (somar)
            self.movimentar_estoque(id_produto_final, qtd_produzida, TIPO_ENTRADA_PRODUCAO, "Produção Concluída", usuario, "fundo")
            
            return True, f"Produção de {qtd_produzida} {receita['nome']} concluída!"
        except Exception as e:
            return False, f"Erro na produção: {str(e)}"
"""

# --- CONTEÚDO: aba_cadastro.py (Interface Atualizada) ---
aba_cadastro_code = """
import customtkinter as ctk
from tkinter import ttk, messagebox

class AbaCadastro(ctk.CTkFrame):
    def __init__(self, master, controller, callback_atualizar):
        super().__init__(master)
        self.controller = controller
        self.atualizar_sistema = callback_atualizar
        self.produtos = {} 
        
        self.montar_layout()

    def montar_layout(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True)

        # --- ESQUERDA: FORMULÁRIO ---
        form = ctk.CTkFrame(container, border_width=1, border_color="#444")
        form.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)
        
        ctk.CTkLabel(form, text="Dados do Item", font=("Arial", 16, "bold"), text_color="#2CC985").grid(row=0, column=0, columnspan=2, pady=15, padx=15, sticky="w")

        # --- TIPO DE ITEM (Insumo vs Produto) ---
        ctk.CTkLabel(form, text="Tipo do Item:", text_color="#ccc").grid(row=1, column=0, sticky="w", padx=15)
        self.tipo_var = ctk.StringVar(value="PRODUTO")
        
        radio_frame = ctk.CTkFrame(form, fg_color="transparent")
        radio_frame.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 10))
        
        ctk.CTkRadioButton(radio_frame, text="🍞 PRODUTO (Venda)", variable=self.tipo_var, value="PRODUTO", fg_color="#2980B9").pack(side="left", padx=5)
        ctk.CTkRadioButton(radio_frame, text="📦 INSUMO (Matéria)", variable=self.tipo_var, value="INSUMO", fg_color="#E67E22").pack(side="left", padx=5)

        self.criar_input(form, "Código:", 3, 0)
        self.ent_cod = ctk.CTkEntry(form, placeholder_text="Ex: 1001")
        self.ent_cod.grid(row=4, column=0, padx=15, pady=(0, 10), sticky="ew")

        self.criar_input(form, "Unidade:", 3, 1)
        self.combo_un = ctk.CTkComboBox(form, values=["UN", "KG", "L", "PCT", "CX", "G", "ML"], width=100)
        self.combo_un.grid(row=4, column=1, padx=15, pady=(0, 10), sticky="w")

        self.criar_input(form, "Nome:", 5, 0)
        self.ent_nome = ctk.CTkEntry(form, placeholder_text="Ex: Farinha de Trigo")
        self.ent_nome.grid(row=6, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="ew")

        self.criar_input(form, "Categoria:", 7, 0)
        self.combo_cat = ctk.CTkComboBox(form, values=["Panificação", "Confeitaria", "Bebidas", "Frios", "Insumos", "Embalagens", "Outros"])
        self.combo_cat.grid(row=8, column=0, padx=15, pady=(0, 10), sticky="ew")

        # --- NOVOS CAMPOS: CUSTO E PREÇO ---
        self.criar_input(form, "Custo (R$):", 9, 0)
        self.ent_custo = ctk.CTkEntry(form, placeholder_text="0.00")
        self.ent_custo.grid(row=10, column=0, padx=15, pady=(0, 10), sticky="ew")

        self.criar_input(form, "Venda (R$):", 9, 1)
        self.ent_preco = ctk.CTkEntry(form, placeholder_text="0.00")
        self.ent_preco.grid(row=10, column=1, padx=15, pady=(0, 10), sticky="ew")

        self.criar_input(form, "Estoque Mínimo:", 11, 0)
        self.ent_minimo = ctk.CTkEntry(form, placeholder_text="Ex: 10")
        self.ent_minimo.grid(row=12, column=0, padx=15, pady=(0, 10), sticky="ew")

        self.switch_controla = ctk.CTkSwitch(form, text="Controlar Estoque")
        self.switch_controla.select()
        self.switch_controla.grid(row=13, column=0, columnspan=2, padx=15, pady=20, sticky="w")

        ctk.CTkButton(form, text="💾 SALVAR ITEM", fg_color="#27AE60", height=45, 
                      command=self.salvar).grid(row=14, column=0, columnspan=2, padx=15, pady=10, sticky="ew")

        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        # --- DIREITA: LISTA RÁPIDA ---
        list_frame = ctk.CTkFrame(container, width=300)
        list_frame.pack(side="right", fill="y", pady=10)
        
        ctk.CTkLabel(list_frame, text="Itens Cadastrados", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Colunas extras para ver o tipo
        self.tree = ttk.Treeview(list_frame, columns=("cod", "tipo", "nome"), show="headings")
        self.tree.heading("cod", text="ID"); self.tree.column("cod", width=50, anchor="center")
        self.tree.heading("tipo", text="Tipo"); self.tree.column("tipo", width=80, anchor="center")
        self.tree.heading("nome", text="Nome"); self.tree.column("nome", width=150)
        
        scroll = ctk.CTkScrollbar(list_frame, command=self.tree.yview)
        self.tree.configure(yscroll=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.tree.bind("<<TreeviewSelect>>", self.carregar_edicao)

    def criar_input(self, p, t, r, c):
        ctk.CTkLabel(p, text=t, text_color="#ccc").grid(row=r, column=c, sticky="w", padx=15, pady=(5,0))

    def salvar(self):
        dados = {
            "id": self.ent_cod.get().strip(),
            "nome": self.ent_nome.get().strip(),
            "categoria": self.combo_cat.get(),
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
            if not messagebox.askyesno("Atenção", "Preço de Venda em Insumo?\\n\\nGeralmente Insumos (Farinha, Ovos) têm apenas Custo.\\nDeseja continuar?"):
                return

        if self.controller.salvar_produto(dados):
            messagebox.showinfo("Sucesso", "Item Salvo!")
            self.limpar_form()
            self.atualizar_sistema()

    def limpar_form(self):
        for e in [self.ent_cod, self.ent_nome, self.ent_preco, self.ent_custo, self.ent_minimo]: 
            e.delete(0, "end")
        self.tipo_var.set("PRODUTO")

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
            self.combo_cat.set(p.get('categoria', 'Outros'))
            self.tipo_var.set(p.get('tipo', 'PRODUTO'))
"""

def atualizar_arquivos():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Caminhos
    path_controller = os.path.join(base_dir, "src", "controllers", "estoque_controller.py")
    path_aba = os.path.join(base_dir, "src", "views", "estoque", "aba_cadastro.py")
    
    # Gravar Controller
    with open(path_controller, "w", encoding="utf-8") as f:
        f.write(controller_code)
    print(f"✅ Atualizado: {path_controller}")
    
    # Gravar Aba Cadastro
    with open(path_aba, "w", encoding="utf-8") as f:
        f.write(aba_cadastro_code)
    print(f"✅ Atualizado: {path_aba}")

if __name__ == "__main__":
    atualizar_arquivos()