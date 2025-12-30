# src/views/estoque/aba_visao_geral.py
import customtkinter as ctk
from tkinter import ttk
from src.utils.formata_numeros_br import formata_numeros_br

class AbaVisaoGeral(ctk.CTkFrame):
    def __init__(self, master, callback_atualizar):
        super().__init__(master)
        self.atualizar_sistema = callback_atualizar
        self.produtos = {}
        
        self.montar_layout()

    def montar_layout(self):
        # CABEÇALHO COM FILTROS
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=10)
        
        top_line = ctk.CTkFrame(header, fg_color="transparent")
        top_line.pack(fill="x")
        ctk.CTkLabel(top_line, text="📋 Visão Geral do Estoque", font=("Arial", 18, "bold"), text_color="#2CC985").pack(side="left")
        ctk.CTkButton(top_line, text="🔄 Atualizar", width=100, fg_color="#2980B9", 
                      command=self.atualizar_sistema).pack(side="right")

        # ÁREA DE FILTROS
        filter_frame = ctk.CTkFrame(header, border_width=1, border_color="#444")
        filter_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkLabel(filter_frame, text="Filtros:", font=("Arial", 12, "bold")).pack(side="left", padx=10, pady=5)
        
        self.ent_busca = ctk.CTkEntry(filter_frame, placeholder_text="Buscar por Nome, Grupo ou EAN...", width=300)
        self.ent_busca.pack(side="left", padx=5, pady=5)
        self.ent_busca.bind("<KeyRelease>", self.aplicar_filtro)
        
        self.combo_status = ctk.CTkComboBox(filter_frame, values=["TODOS", "OK", "BAIXO", "ZERADO"], width=100, command=self.aplicar_filtro)
        self.combo_status.set("TODOS")
        self.combo_status.pack(side="left", padx=5, pady=5)
        
        ctk.CTkButton(filter_frame, text="Limpar", width=60, fg_color="#555", command=self.limpar_filtros).pack(side="left", padx=5)

        # TABELA
        table_container = ctk.CTkFrame(self, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.cols = ("id", "nome", "ean", "frente", "fundo", "un", "custo", "venda", "status")
        
        self.tree = ttk.Treeview(table_container, columns=self.cols, show="tree headings") 
        
        self.tree.heading("#0", text="PRODUTO / AGRUPAMENTO")
        self.tree.column("#0", width=250, anchor="w") 

        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="VARIAÇÃO")
        self.tree.heading("ean", text="EAN") 
        self.tree.heading("frente", text="LOJA (FRENTE)")
        self.tree.heading("fundo", text="DEP. (FUNDO)")
        self.tree.heading("un", text="UN")
        self.tree.heading("custo", text="CUSTO")
        self.tree.heading("venda", text="VENDA")
        self.tree.heading("status", text="STATUS")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("nome", width=180)
        self.tree.column("ean", width=100, anchor="center")
        self.tree.column("frente", width=90, anchor="center")
        self.tree.column("fundo", width=90, anchor="center")
        self.tree.column("un", width=50, anchor="center")
        self.tree.column("custo", width=70, anchor="center")
        self.tree.column("venda", width=70, anchor="center")
        self.tree.column("status", width=90, anchor="center")

        scroll = ctk.CTkScrollbar(table_container, command=self.tree.yview)
        self.tree.configure(yscroll=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        
        self.tree.tag_configure("baixo", foreground="#E74C3C")  
        self.tree.tag_configure("ok", foreground="#2ECC71")
        self.tree.tag_configure("zerado", foreground="#95A5A6")
        self.tree.tag_configure("grupo", background="#333", foreground="white", font=("Arial", 10, "bold")) # Cor de fundo discreta

    def limpar_filtros(self):
        self.ent_busca.delete(0, 'end')
        self.combo_status.set("TODOS")
        self.renderizar_arvore(self.dados_processados)

    def atualizar(self, produtos_dict):
        """
        Recebe os dados brutos, processa em uma estrutura hierárquica e salva em self.dados_processados.
        Depois chama o renderizar.
        """
        self.produtos = produtos_dict
        
        # 1. Estruturar Dados (Grupos e Soltos)
        grupos_temp = {}
        lista_mista = [] # Vai conter tanto dicionários de Itens Soltos quanto de Grupos
        
        # Agrupa primeiro
        for item in produtos_dict.values():
            nome_grupo = item.get('grupo', '').strip()
            if nome_grupo:
                if nome_grupo not in grupos_temp:
                    grupos_temp[nome_grupo] = []
                grupos_temp[nome_grupo].append(item)
            else:
                # Item solto: adiciona direto na lista mista com type='item'
                item_copy = item.copy()
                item_copy['_tipo_lista'] = 'item'
                item_copy['_nome_ordenacao'] = item['nome']
                lista_mista.append(item_copy)
        
        # Processa os Grupos para criar objetos de "Cabeçalho de Grupo"
        for nome_gp, lista_itens in grupos_temp.items():
            total_frente = sum(i.get('estoque_atual', 0) for i in lista_itens)
            total_fundo = sum(i.get('estoque_fundo', 0) for i in lista_itens)
            minimo_grupo = sum(i.get('estoque_minimo', 0) for i in lista_itens)
            
            status_gp = "OK"
            if (total_frente + total_fundo) <= 0: status_gp = "ZERADO"
            elif total_frente <= minimo_grupo: status_gp = "BAIXO"

            obj_grupo = {
                '_tipo_lista': 'grupo',
                '_nome_ordenacao': nome_gp, # Para ordenar alfabeticamente junto com itens soltos
                'nome_grupo': nome_gp,
                'frente': total_frente,
                'fundo': total_fundo,
                'unidade': lista_itens[0].get('unidade', 'UN'),
                'status': status_gp,
                'filhos': lista_itens # A lista de itens reais fica aqui dentro
            }
            lista_mista.append(obj_grupo)
            
        # Ordena a lista mista pelo nome (misturando grupos e itens soltos)
        lista_mista.sort(key=lambda x: x['_nome_ordenacao'])
        
        self.dados_processados = lista_mista
        self.renderizar_arvore(lista_mista)

    def aplicar_filtro(self, event=None):
        texto = self.ent_busca.get().lower().strip()
        status_filtro = self.combo_status.get()
        
        if not texto and status_filtro == "TODOS":
            self.renderizar_arvore(self.dados_processados)
            return

        dados_filtrados = []
        
        for obj in self.dados_processados:
            if obj['_tipo_lista'] == 'item':
                # Verifica Item Solto
                match_txt = (texto in obj['nome'].lower() or 
                             texto in str(obj['id']) or 
                             any(texto in str(ean) for ean in obj.get('codigos_barras', [])))
                match_status = (status_filtro == "TODOS") or (self.calcular_status_item(obj) == status_filtro)
                
                if match_txt and match_status:
                    dados_filtrados.append(obj)
            
            elif obj['_tipo_lista'] == 'grupo':
                # Verifica Grupo
                # 1. O grupo bate com o texto?
                match_grupo_nome = texto in obj['nome_grupo'].lower()
                
                # 2. Algum filho bate com o texto?
                filhos_filtrados = []
                for filho in obj['filhos']:
                    match_filho_txt = (texto in filho['nome'].lower() or 
                                       texto in str(filho['id']) or 
                                       any(texto in str(ean) for ean in filho.get('codigos_barras', [])))
                    
                    # Status do filho
                    st_filho = self.calcular_status_item(filho)
                    match_filho_st = (status_filtro == "TODOS") or (st_filho == status_filtro)
                    
                    if (match_grupo_nome or match_filho_txt) and match_filho_st:
                        filhos_filtrados.append(filho)
                
                # Se tiver filhos correspondentes, ou se o grupo bateu no nome e tem filtro de status 'TODOS' (ou status do grupo bate)
                if filhos_filtrados:
                    # Cria uma cópia do grupo só com os filhos filtrados para exibição
                    grupo_copia = obj.copy()
                    grupo_copia['filhos'] = filhos_filtrados
                    grupo_copia['_expandir'] = True # Flag para expandir automaticamente
                    dados_filtrados.append(grupo_copia)

        self.renderizar_arvore(dados_filtrados)

    def renderizar_arvore(self, lista_dados):
        for i in self.tree.get_children(): self.tree.delete(i)
        
        for obj in lista_dados:
            if obj['_tipo_lista'] == 'grupo':
                # Renderiza Grupo
                frente_fmt = formata_numeros_br(obj['frente'], moeda=False)
                fundo_fmt = formata_numeros_br(obj['fundo'], moeda=False)
                
                # Deve expandir?
                expandir = obj.get('_expandir', False)
                
                pai_id = self.tree.insert("", "end", text=f"📂 {obj['nome_grupo']}", open=expandir,
                                          values=("---", "---", "---", 
                                                  frente_fmt, fundo_fmt, 
                                                  obj['unidade'], "---", "---", obj['status']),
                                          tags=('grupo',))
                
                for filho in obj['filhos']:
                    self.inserir_linha_item(filho, pai_id)
            else:
                # Renderiza Item Solto
                self.inserir_linha_item(obj, "")

    def inserir_linha_item(self, p, parent):
        st = self.calcular_status_item(p)
        tag = st.lower()
        
        est_frente = p.get('estoque_atual', 0)
        est_fundo = p.get('estoque_fundo', 0)
        
        custo = formata_numeros_br(p.get('custo', 0), moeda=True)
        venda = formata_numeros_br(p.get('preco', 0), moeda=True)
        frente_fmt = formata_numeros_br(est_frente, moeda=False)
        fundo_fmt = formata_numeros_br(est_fundo, moeda=False)
        
        ean_raw = p.get('codigos_barras', [])
        ean_str = ean_raw[0] if (isinstance(ean_raw, list) and len(ean_raw) > 0) else str(ean_raw)
        
        # Se tem parent, é filho, então não tem texto na coluna #0 (Tree)
        texto_tree = "" 
        # Se não tem parent, é item solto, então o nome vai na coluna #0 para alinhar com os grupos
        if parent == "":
            texto_tree = p['nome']
            nome_col_1 = "---" # Se o nome tá na #0, a coluna Nome (1) fica vazia ou repetida? 
                               # Melhor: Coluna #0 é sempre "Entidade Principal". 
                               # Se for grupo, #0 é Nome Grupo. 
                               # Se for item solto, #0 é Nome Item.
            # Ajuste visual: Vamos manter o nome na coluna 1 também para padronizar com os filhos?
            # Ou limpamos a coluna 1 para itens soltos? Vamos manter na 1 para consistência.
            texto_tree = p['nome'] 
        
        self.tree.insert(parent, "end", text=texto_tree if parent == "" else "",
                         values=(p['id'], p['nome'], ean_str, 
                                 frente_fmt, fundo_fmt, 
                                 p.get('unidade'), f"R$ {custo}", f"R$ {venda}", st),
                         tags=(tag,))

    def calcular_status_item(self, p):
        est = p.get('estoque_atual', 0) + p.get('estoque_fundo', 0)
        minimo = p.get('estoque_minimo', 0)
        if est <= 0: return "ZERADO"
        if p.get('estoque_atual', 0) <= minimo: return "BAIXO"
        return "OK"