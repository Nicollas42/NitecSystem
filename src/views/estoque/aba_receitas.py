# src/views/estoque/aba_receitas.py
import customtkinter as ctk
from tkinter import ttk, messagebox

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


class AbaReceitas(ctk.CTkFrame):
    def __init__(self, master, controller, produtos_ref, callback_atualizar):
        super().__init__(master)
        self.controller = controller
        self.produtos = produtos_ref
        self.callback_atualizar = callback_atualizar
        
        self.ingredientes_temp = [] 
        self.id_produto_atual = None
        self.lista_insumos_nomes = []
        self.janela_ajuda = None
        
        self.montar_layout()

    def montar_layout(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        # --- ESQUERDA: LISTA DE PRODUTOS ---
        frame_esq = ctk.CTkFrame(self, fg_color="#2b2b2b")
        frame_esq.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Cabeçalho da Lista (Título + Ajuda)
        header_esq = ctk.CTkFrame(frame_esq, fg_color="transparent")
        header_esq.pack(fill="x", pady=10)
        
        ctk.CTkLabel(header_esq, text="1. Escolha o Produto Final", font=("Arial", 14, "bold"), text_color="#2CC985").pack(side="left", padx=(10, 5))
        ctk.CTkButton(header_esq, text="?", width=25, height=25, fg_color="#2980B9", hover_color="#1F618D",
                      command=self.mostrar_ajuda).pack(side="left")
        
        self.lista_produtos = ttk.Treeview(frame_esq, columns=("nome",), show="headings")
        self.lista_produtos.heading("nome", text="Produtos (Venda)")
        self.lista_produtos.pack(fill="both", expand=True, padx=10, pady=10)
        self.lista_produtos.bind("<<TreeviewSelect>>", self.carregar_receita_existente)

        # --- DIREITA: EDITOR DE RECEITA ---
        frame_dir = ctk.CTkFrame(self)
        frame_dir.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Cabeçalho da Direita
        f_head = ctk.CTkFrame(frame_dir, fg_color="transparent")
        f_head.pack(fill="x", padx=10, pady=10)
        
        self.lbl_produto_selecionado = ctk.CTkLabel(f_head, text="Nenhum Produto Selecionado", font=("Arial", 18, "bold"))
        self.lbl_produto_selecionado.pack(anchor="w")

        f_rend = ctk.CTkFrame(f_head, fg_color="transparent")
        f_rend.pack(fill="x", pady=5)
        ctk.CTkLabel(f_rend, text="Rendimento desta Receita (Qtd Produzida):").pack(side="left")
        self.ent_rendimento = ctk.CTkEntry(f_rend, width=80, placeholder_text="Ex: 10")
        self.ent_rendimento.pack(side="left", padx=10)
        self.lbl_unidade_rend = ctk.CTkLabel(f_rend, text="UN")
        self.lbl_unidade_rend.pack(side="left")

        # Área de Adicionar Insumo
        f_add = ctk.CTkFrame(frame_dir, border_width=1, border_color="#444")
        f_add.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(f_add, text="2. Adicionar Insumo", font=("Arial", 12, "bold"), text_color="#E67E22").pack(pady=5)
        
        # Dropdown Padronizado
        self.ent_insumo = ctk.CTkEntry(f_add, width=250, placeholder_text="Digite o nome do insumo...")
        self.ent_insumo.pack(side="left", padx=10, pady=10)
        
        self.dropdown_insumos = CTkFloatingDropdown(self.ent_insumo, [], width=350, command=self.verificar_unidade)
        self.ent_insumo.bind("<FocusOut>", lambda e: self.verificar_unidade())
        self.ent_insumo.bind("<Return>", lambda e: self.verificar_unidade())

        self.ent_qtd_ing = ctk.CTkEntry(f_add, width=80, placeholder_text="Qtd")
        self.ent_qtd_ing.pack(side="left", padx=5)
        
        self.lbl_un_ing = ctk.CTkLabel(f_add, text="UN")
        self.lbl_un_ing.pack(side="left", padx=5)

        ctk.CTkButton(f_add, text="Adicionar (+)", width=100, fg_color="#27AE60", command=self.adicionar_ingrediente).pack(side="left", padx=10)

        # --- NOVA LISTA DE INSUMOS ---
        f_list_container = ctk.CTkFrame(frame_dir, fg_color="transparent")
        f_list_container.pack(fill="both", expand=True, padx=10)

        # Cabeçalho da Lista
        header_list = ctk.CTkFrame(f_list_container, fg_color="#333", height=30)
        header_list.pack(fill="x")
        
        header_list.columnconfigure(0, weight=1)
        header_list.columnconfigure(1, weight=0, minsize=100)
        header_list.columnconfigure(2, weight=0, minsize=100)
        header_list.columnconfigure(3, weight=0, minsize=50)
        header_list.columnconfigure(4, weight=0, minsize=25)

        ctk.CTkLabel(header_list, text="Insumo", font=("Arial", 12, "bold"), anchor="w").grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(header_list, text="Qtd", font=("Arial", 12, "bold"), anchor="center").grid(row=0, column=1)
        ctk.CTkLabel(header_list, text="Custo Parc.", font=("Arial", 12, "bold"), anchor="center").grid(row=0, column=2)
        ctk.CTkLabel(header_list, text="Ação", font=("Arial", 12, "bold"), anchor="center").grid(row=0, column=3)

        # Scrollable Frame
        self.scroll_ing = ctk.CTkScrollableFrame(f_list_container, fg_color="transparent")
        self.scroll_ing.pack(fill="both", expand=True)

        # Rodapé
        f_footer = ctk.CTkFrame(frame_dir, height=60, fg_color="#333")
        f_footer.pack(fill="x", side="bottom")
        
        self.lbl_custo_total = ctk.CTkLabel(f_footer, text="Custo Total: R$ 0.00", font=("Arial", 14, "bold"))
        self.lbl_custo_total.pack(side="left", padx=20, pady=15)
        
        ctk.CTkButton(f_footer, text="💾 SALVAR FICHA", fg_color="#2980B9", width=150,
                      command=self.salvar_receita).pack(side="right", padx=10, pady=10)
                      
        ctk.CTkButton(f_footer, text="❌ EXCLUIR RECEITA", fg_color="#7B241C", hover_color="#50120E", width=150,
                      command=self.excluir_receita_atual).pack(side="right", padx=10, pady=10)

    def atualizar(self):
        self.lista_produtos.delete(*self.lista_produtos.get_children())
        self.lista_insumos_nomes = []
        
        for cod, p in self.produtos.items():
            if p.get('tipo') == 'PRODUTO':
                self.lista_produtos.insert("", "end", values=(p['nome'],), tags=(cod,))
            elif p.get('tipo') == 'INSUMO':
                self.lista_insumos_nomes.append(p['nome'])
        
        self.dropdown_insumos.atualizar_dados(self.lista_insumos_nomes)

    def verificar_unidade(self, item_selecionado=None):
        nome = item_selecionado if item_selecionado else self.ent_insumo.get()
        for cod, p in self.produtos.items():
            if p['nome'] == nome and p.get('tipo') == 'INSUMO':
                self.lbl_un_ing.configure(text=p.get('unidade', 'UN'))
                return
        self.lbl_un_ing.configure(text="UN")

    def carregar_receita_existente(self, event):
        sel = self.lista_produtos.selection()
        if not sel: return
        item = self.lista_produtos.item(sel[0])
        
        cod_prod = str(item['tags'][0]) 
        nome_prod = item['values'][0]
        
        self.id_produto_atual = cod_prod
        self.lbl_produto_selecionado.configure(text=f"Editando: {nome_prod}")
        
        if cod_prod in self.produtos:
            self.lbl_unidade_rend.configure(text=self.produtos[cod_prod].get('unidade', 'UN'))
        
        self.ingredientes_temp = []
        self.ent_rendimento.delete(0, "end")
        
        todas_receitas = self.controller.carregar_receitas()
        if cod_prod in todas_receitas:
            rec = todas_receitas[cod_prod]
            self.ent_rendimento.insert(0, rec.get('rendimento', 1))
            self.ingredientes_temp = rec.get('ingredientes', [])
        else:
            self.ent_rendimento.insert(0, "1")
        
        self.renderizar_ingredientes()

    def adicionar_ingrediente(self):
        if not self.id_produto_atual:
            messagebox.showwarning("Aviso", "Selecione um produto na lista à esquerda primeiro.")
            return

        nome = self.ent_insumo.get()
        qtd_txt = self.ent_qtd_ing.get().replace(",", ".")
        
        if not nome or not qtd_txt: 
            messagebox.showwarning("Aviso", "Preencha o insumo e a quantidade.")
            return
        
        try:
            qtd = float(qtd_txt)
        except:
            messagebox.showerror("Erro", "Quantidade inválida.")
            return
        
        id_insumo = next((k for k, v in self.produtos.items() if v['nome'] == nome), None)
        if not id_insumo:
            messagebox.showerror("Erro", "Insumo não encontrado no cadastro.")
            return

        self.ingredientes_temp.append({
            "id": id_insumo,
            "nome": nome,
            "qtd": qtd
        })
        self.ent_qtd_ing.delete(0, "end")
        self.ent_insumo.delete(0, "end")
        self.ent_insumo.focus_set()
        self.renderizar_ingredientes()

    def remover_ingrediente(self, index):
        if 0 <= index < len(self.ingredientes_temp):
            del self.ingredientes_temp[index]
            self.renderizar_ingredientes()

    def renderizar_ingredientes(self):
        for widget in self.scroll_ing.winfo_children():
            widget.destroy()

        custo_total = 0.0
        
        self.scroll_ing.columnconfigure(0, weight=1)
        self.scroll_ing.columnconfigure(1, weight=0, minsize=100)
        self.scroll_ing.columnconfigure(2, weight=0, minsize=100)
        self.scroll_ing.columnconfigure(3, weight=0, minsize=50)

        for i, ing in enumerate(self.ingredientes_temp):
            id_insumo = str(ing.get('id', ''))
            p_insumo = self.produtos.get(id_insumo, {})
            
            # --- CORREÇÃO DE SEGURANÇA AQUI ---
            # 1. Tenta pegar o nome salvo na receita
            # 2. Se não tiver, tenta pegar do cadastro atual de produtos
            # 3. Se não tiver em lugar nenhum, mostra o ID ou "Desconhecido"
            nome_display = ing.get('nome') or p_insumo.get('nome') or f"Item {id_insumo}"
            # ----------------------------------

            unidade = p_insumo.get('unidade', 'UN')
            custo_unit = float(p_insumo.get('custo', 0.0))
            qtd = float(ing.get('qtd', 0))
            subtotal = custo_unit * qtd
            custo_total += subtotal
            
            qtd_fmt = f"{int(qtd)}" if qtd.is_integer() else f"{qtd:.3f}"
            
            ctk.CTkLabel(self.scroll_ing, text=nome_display, anchor="w").grid(row=i, column=0, sticky="ew", padx=10, pady=5)
            ctk.CTkLabel(self.scroll_ing, text=f"{qtd_fmt} {unidade}", anchor="center").grid(row=i, column=1)
            ctk.CTkLabel(self.scroll_ing, text=f"R$ {subtotal:.2f}", anchor="center").grid(row=i, column=2)
            
            btn_del = ctk.CTkButton(self.scroll_ing, text="🗑️", width=30, height=30, 
                                    fg_color="transparent", 
                                    text_color="#C0392B",
                                    hover_color="#333333",
                                    font=("Arial", 16),
                                    command=lambda idx=i: self.remover_ingrediente(idx))
            btn_del.grid(row=i, column=3)
            
            if i < len(self.ingredientes_temp) - 1:
                sep = ctk.CTkFrame(self.scroll_ing, height=1, fg_color="#444")
                sep.grid(row=i+1000, column=0, columnspan=4, sticky="ew", pady=(0, 5))

        self.lbl_custo_total.configure(text=f"Custo Total: R$ {custo_total:.2f}")

    def salvar_receita(self):
        if not self.id_produto_atual: return
        rend_txt = self.ent_rendimento.get().replace(",", ".")
        if not rend_txt: 
            messagebox.showerror("Erro", "Defina o rendimento.")
            return
        if not self.ingredientes_temp:
            messagebox.showwarning("Aviso", "A lista de ingredientes está vazia.")
            return
        ok, msg = self.controller.salvar_receita(str(self.id_produto_atual), rend_txt, self.ingredientes_temp)
        if ok:
            messagebox.showinfo("Sucesso", msg)
            self.callback_atualizar()

    def excluir_receita_atual(self):
        if not self.id_produto_atual: return
        if not messagebox.askyesno("Excluir Receita", "Tem certeza que deseja apagar esta Ficha Técnica?"):
            return
        ok, msg = self.controller.deletar_receita(self.id_produto_atual)
        if ok:
            messagebox.showinfo("Sucesso", msg)
            self.ingredientes_temp = []
            self.ent_rendimento.delete(0, "end")
            self.lbl_produto_selecionado.configure(text="Nenhum Produto Selecionado")
            self.renderizar_ingredientes()
            self.id_produto_atual = None
            self.callback_atualizar()
        else:
            messagebox.showerror("Erro", msg)

    def mostrar_ajuda(self):
        if self.janela_ajuda and self.janela_ajuda.winfo_exists():
            self.janela_ajuda.lift(); self.janela_ajuda.focus_force(); return
        
        self.janela_ajuda = ctk.CTkToplevel(self)
        self.janela_ajuda.title("Manual - Ficha Técnica")
        self.janela_ajuda.geometry("600x650") # Aumentei um pouco para caber o texto
        self.janela_ajuda.transient(self)
        self.janela_ajuda.lift()
        self.janela_ajuda.focus_force()
        
        ctk.CTkLabel(self.janela_ajuda, text="📖 COMO USAR A FICHA TÉCNICA", font=("Arial", 20, "bold"), text_color="#2CC985").pack(pady=(20, 10))
        
        # Scrollable frame para garantir que todo o texto caiba
        scroll_frame = ctk.CTkScrollableFrame(self.janela_ajuda, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        texto_ajuda = """
🎯 PARA QUE SERVE ESTA TELA?
Aqui você ensina ao sistema como seus produtos são feitos.
Isso permite duas coisas mágicas:
1. Cálculo Automático de Custo: O sistema soma o valor da farinha, ovos, etc., e diz quanto custa fabricar 1 unidade.
2. Baixa Automática de Estoque: Quando você produzir pão, o sistema descontará a farinha sozinho.

🛠️ O QUE VOCÊ PODE FAZER AQUI?
• Criar uma receita do zero.
• Corrigir uma receita (ex: mudou a quantidade de sal).
• Atualizar custos (basta abrir e salvar novamente).
• Excluir receitas antigas.

📝 PASSO A PASSO COM EXEMPLO
Imagine que vamos cadastrar o "PÃO DE QUEIJO":

1️⃣ SELECIONE O PRODUTO (Esquerda)
   Clique em "Pão de Queijo" na lista lateral.

2️⃣ DEFINA O RENDIMENTO (Campo Superior)
   Pergunta: "Essa receita que vou digitar rende quanto?"
   Exemplo: Se você vai digitar os ingredientes de uma masseira cheia que rende 10kg de pão, digite "10".
   *Dica: O rendimento deve estar na mesma unidade do produto (KG, UN, L).*

3️⃣ ADICIONE OS INSUMOS (Direita)
   Digite "Polvilho", coloque a quantidade (ex: 5 KG) e clique em Adicionar.
   Repita para o Queijo, Ovos, Leite, etc.

4️⃣ SALVAR
   Ao clicar em SALVAR, o sistema calcula o preço de custo unitário e atualiza o cadastro do produto.

⚠️ REGRAS IMPORTANTES
• O Custo do Insumo (R$) vem do cadastro dele. Se estiver zerado lá, ficará zerado aqui.
• Se errar um ingrediente, clique na 🗑️ (Lixeira) ao lado dele e adicione novamente.
"""
        lbl = ctk.CTkLabel(scroll_frame, text=texto_ajuda, justify="left", anchor="nw", padx=20, font=("Consolas", 14))
        lbl.pack(fill="both", expand=True)