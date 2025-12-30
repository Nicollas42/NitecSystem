import customtkinter as ctk
from src.utils.componentes_estilizados import CTkFloatingDropdown

class FormBase(ctk.CTkFrame):
    def __init__(self, master, lista_categorias):
        super().__init__(master, fg_color="transparent")
        self.lista_categorias = lista_categorias
        self.montar_comuns()

    def criar_input(self, t, r, c, w=None):
        ctk.CTkLabel(self, text=t, text_color="#ccc").grid(row=r, column=c, sticky="w", padx=10, pady=(5,0))
        entry = ctk.CTkEntry(self, width=w if w else 140)
        entry.grid(row=r+1, column=c, sticky="ew", padx=10, pady=(0,10))
        return entry

    def montar_comuns(self):
        self.ent_cod = self.criar_input("ID (Cód. Interno):", 0, 0)
        
        ctk.CTkLabel(self, text="Unidade:", text_color="#ccc").grid(row=0, column=1, sticky="w", padx=10)
        self.combo_un = ctk.CTkComboBox(self, values=["UN", "KG", "L", "PCT", "CX", "G", "ML"])
        self.combo_un.grid(row=1, column=1, sticky="ew", padx=10)

        self.ent_nome = self.criar_input("Nome:", 2, 0)
        self.ent_nome.grid(columnspan=2)

        self.ent_grupo = self.criar_input("Grupo / Família:", 4, 0)
        self.ent_grupo.grid(columnspan=2)

        self.ent_ean = self.criar_input("EAN (Barras):", 6, 0)
        self.ent_ean.grid(columnspan=2)

        self.ent_cat = self.criar_input("Categoria:", 8, 0)
        self.ent_cat.grid(columnspan=2)
        self.dropdown_cat = CTkFloatingDropdown(self.ent_cat, self.lista_categorias)

        self.ent_minimo = self.criar_input("Estoque Mínimo:", 10, 0)
        
        self.switch_controla = ctk.CTkSwitch(self, text="Controlar Estoque")
        self.switch_controla.select()
        self.switch_controla.grid(row=11, column=1, padx=10, pady=20)

    def get_dados_comuns(self):
        return {
            "id": self.ent_cod.get().strip(),
            "nome": self.ent_nome.get().strip(),
            "grupo": self.ent_grupo.get().strip().upper(),
            "codigos_barras": [e.strip() for e in self.ent_ean.get().split(',') if e.strip()],
            "categoria": self.ent_cat.get(),
            "unidade": self.combo_un.get(),
            "minimo": self.ent_minimo.get().replace(",", ".") or "0",
            "controla_estoque": bool(self.switch_controla.get())
        }
    
    def limpar_comuns(self):
        for e in [self.ent_cod, self.ent_nome, self.ent_grupo, self.ent_ean, self.ent_cat, self.ent_minimo]:
            e.delete(0, 'end')
        self.dropdown_cat.fechar_lista()

    def preencher_comuns(self, dados):
        """Carrega os dados do dicionário para os campos visuais"""
        self.limpar_comuns()
        self.ent_cod.insert(0, dados.get('id', ''))
        self.ent_nome.insert(0, dados.get('nome', ''))
        self.ent_grupo.insert(0, dados.get('grupo', ''))
        
        eans = dados.get('codigos_barras', [])
        if isinstance(eans, list):
            self.ent_ean.insert(0, ", ".join(eans))
        else:
            self.ent_ean.insert(0, str(eans))
            
        self.combo_un.set(dados.get('unidade', 'UN'))
        self.ent_cat.insert(0, dados.get('categoria', ''))
        self.ent_minimo.insert(0, dados.get('estoque_minimo', 0))
        
        if dados.get('controla_estoque', True): self.switch_controla.select()
        else: self.switch_controla.deselect()

# --- FORMULÁRIOS ESPECÍFICOS ---

class FormRevenda(FormBase):
    def __init__(self, master, cats):
        super().__init__(master, cats)
        self.ent_custo = self.criar_input("Custo (R$):", 12, 0)
        self.ent_preco = self.criar_input("Venda (R$):", 12, 1)

    def get_dados(self):
        d = self.get_dados_comuns()
        d.update({
            "tipo": "PRODUTO",
            "custo": self.ent_custo.get().replace(",", ".") or "0",
            "preco": self.ent_preco.get().replace(",", ".") or "0"
        })
        return d

    def preencher(self, dados):
        self.preencher_comuns(dados)
        self.ent_custo.delete(0, 'end'); self.ent_custo.insert(0, dados.get('custo', '0.00'))
        self.ent_preco.delete(0, 'end'); self.ent_preco.insert(0, dados.get('preco', '0.00'))

class FormInsumo(FormBase):
    def __init__(self, master, cats):
        super().__init__(master, cats)
        self.ent_custo = self.criar_input("Custo (R$):", 12, 0)

    def get_dados(self):
        d = self.get_dados_comuns()
        d.update({
            "tipo": "INSUMO",
            "custo": self.ent_custo.get().replace(",", ".") or "0",
            "preco": "0.00"
        })
        return d

    def preencher(self, dados):
        self.preencher_comuns(dados)
        self.ent_custo.delete(0, 'end'); self.ent_custo.insert(0, dados.get('custo', '0.00'))

class FormInterno(FormBase):
    def __init__(self, master, cats):
        super().__init__(master, cats)
        self.ent_preco = self.criar_input("Venda (R$):", 12, 0)
        self.ent_preco.grid(columnspan=2)
        ctk.CTkLabel(self, text="ℹ️ O Custo deste item é calculado na Ficha Técnica.", text_color="orange").grid(row=14, column=0, columnspan=2, pady=5)

    def get_dados(self):
        d = self.get_dados_comuns()
        d.update({
            "tipo": "INTERNO",
            "custo": "0.00",
            "preco": self.ent_preco.get().replace(",", ".") or "0"
        })
        return d

    def preencher(self, dados):
        self.preencher_comuns(dados)
        self.ent_preco.delete(0, 'end'); self.ent_preco.insert(0, dados.get('preco', '0.00'))