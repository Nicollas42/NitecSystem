# src/views/view_caixa.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
import time

# --- CORREÇÃO DOS IMPORTS ---
from src.controllers import config_manager
from src.models import database

class CaixaFrame(ctk.CTkFrame):
    def __init__(self, master, usuario_dados, callback_voltar):
        super().__init__(master)
        self.usuario = usuario_dados
        self.voltar_menu = callback_voltar
        
        self.config = config_manager.carregar_config()
        self.cor_destaque = self.config["cor_destaque"]
        
        self.produtos_db = database.carregar_produtos()
        
        self.carrinho = [] 
        self.contador_id = 0
        self.ultimo_item_focado = None 
        self.total_a_pagar = 0.0

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)

        self.montar_interface()

    def montar_interface(self):
        # CABEÇALHO
        top = ctk.CTkFrame(self, height=50, corner_radius=0)
        top.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        ctk.CTkButton(top, text="🔙 Voltar ao Menu", width=100, fg_color="#555", 
                      command=self.tentar_sair).pack(side="left", padx=(10, 5), pady=10)
        
        ctk.CTkButton(top, text="?", width=30, fg_color="#333", hover_color="#444", 
                      command=self.mostrar_ajuda).pack(side="left", padx=5)

        ctk.CTkLabel(top, text="PDV ABERTO", font=("Arial", 16, "bold")).pack(side="left", padx=20)
        
        self.lbl_relogio = ctk.CTkLabel(top, text="--:--:--", font=("Consolas", 14, "bold"), text_color=self.cor_destaque)
        self.lbl_relogio.pack(side="right", padx=20)
        self.atualizar_relogio()

        # ESQUERDA
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        f_input = ctk.CTkFrame(left, height=100)
        f_input.grid(row=0, column=0, sticky="ew", pady=(0,10))
        
        self.lbl_status_leitor = ctk.CTkLabel(f_input, text="CLIQUE AQUI PARA LER", text_color="orange", font=("Arial", 10, "bold"))
        self.lbl_status_leitor.pack(anchor="w", padx=12, pady=(5,0))

        ctk.CTkLabel(f_input, text="CÓDIGO (F1)", font=("Arial", 12)).pack(anchor="w", padx=10)
        
        self.entry_cod = ctk.CTkEntry(f_input, height=45, font=("Arial", 18), border_width=2)
        self.entry_cod.pack(fill="x", padx=10, pady=5)
        self.entry_cod.bind('<Return>', self.adicionar_item)
        self.entry_cod.bind('<FocusIn>', self.ao_focar_input)
        self.entry_cod.bind('<FocusOut>', self.ao_desfocar_input)
        self.entry_cod.focus()

        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.tree = ttk.Treeview(left, columns=('id', 'desc', 'qtd', 'un', 'preco', 'total'), show='headings', selectmode='browse')
        
        self.tree.tag_configure('active', background=self.cor_destaque, foreground='black')
        self.tree.tag_configure('flash', background='white', foreground='black')
        self.tree.tag_configure('partial', background='#F1C40F', foreground='black')
        self.tree.tag_configure('cancelled', background='#C0392B', foreground='white')

        cols = ('id', 'desc', 'qtd', 'un', 'preco', 'total')
        for c in cols: self.tree.heading(c, text=c.upper())
        self.tree.column('desc', width=200); self.tree.column('id', width=30)
        self.tree.grid(row=1, column=0, sticky="nsew")

        # DIREITA
        right = ctk.CTkFrame(self)
        right.grid(row=1, column=1, sticky="nsew", padx=(0,10), pady=10)
        self.lbl_total = ctk.CTkLabel(right, text="R$ 0.00", font=("Arial", 40, "bold"), text_color=self.cor_destaque)
        self.lbl_total.pack(pady=40)

        ctk.CTkButton(right, text="FINALIZAR (F5)", height=60, fg_color=self.cor_destaque, 
                      command=self.abrir_tela_pagamento).pack(side="bottom", fill="x", padx=20, pady=(10, 20))
        
        ctk.CTkButton(right, text="CANCELAR ITEM (Del)", fg_color="#E67E22", 
                      command=self.cancelar_item).pack(side="bottom", fill="x", padx=20, pady=5)
        
        ctk.CTkButton(right, text="CANCELAR VENDA (Esc)", fg_color="#C0392B", 
                      command=self.cancelar_venda_total).pack(side="bottom", fill="x", padx=20, pady=5)

        root = self.winfo_toplevel()
        root.bind('<F5>', lambda e: self.abrir_tela_pagamento())
        root.bind('<F1>', lambda e: self.entry_cod.focus_set())
        root.bind('<Escape>', lambda e: self.cancelar_venda_total())
        root.bind('<Delete>', lambda e: self.cancelar_item())

    def destroy(self):
        root = self.winfo_toplevel()
        try:
            root.unbind('<F5>')
            root.unbind('<F1>')
            root.unbind('<Escape>')
            root.unbind('<Delete>')
        except: pass
        super().destroy()

    def atualizar_relogio(self):
        self.lbl_relogio.configure(text=datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self.atualizar_relogio)

    def ao_focar_input(self, event):
        self.entry_cod.configure(border_color="#2ECC71")
        self.lbl_status_leitor.configure(text="🟢 PRONTO PARA LER O CÓDIGO", text_color="#2ECC71")

    def ao_desfocar_input(self, event):
        self.entry_cod.configure(border_color="#E74C3C")
        self.lbl_status_leitor.configure(text="🔴 CLIQUE AQUI PARA ATIVAR O LEITOR", text_color="#E74C3C")

    def adicionar_item(self, event=None):
        cod = self.entry_cod.get().strip()
        if not cod: return
        self.entry_cod.delete(0, 'end')
        
        if cod.startswith("2") and len(cod) == 12:
            plu = str(int(cod[1:6]))
            if plu in self.produtos_db:
                peso = float(cod[6:11]) / 1000
                self.lancar(self.produtos_db[plu], cod, peso)
                return

        if cod in self.produtos_db:
            prod = self.produtos_db[cod]
            if prod['un'] in ['KG', 'G']: self.popup_peso(prod, cod)
            else: self.lancar(prod, cod, 1)
        else:
            self.master.bell()
    
    def popup_peso(self, prod, cod):
        unidade = prod['un']
        titulo = f"Peso para {prod['nome']} ({unidade}):"
        d = ctk.CTkInputDialog(text=titulo, title="Pesagem")
        d.geometry(f"+{self.winfo_rootx() + 300}+{self.winfo_rooty() + 200}")
        peso_input = d.get_input()
        if peso_input: 
            try: 
                peso_float = float(peso_input.replace(",", "."))
                self.lancar(prod, cod, peso_float)
            except: pass
        self.entry_cod.focus_set()

    def lancar(self, prod, cod, qtd):
        item_existente = None
        for item in self.carrinho:
            if item['codigo'] == cod:
                item_existente = item
                break
        
        est_atual = prod.get("estoque", 0)
        nome_exibicao = prod['nome']
        qtd_total_validacao = qtd
        if item_existente: qtd_total_validacao += item_existente['qtd']

        if est_atual <= 0: nome_exibicao += " ⚠️ [SEM ESTOQUE]"
        elif est_atual < qtd_total_validacao: nome_exibicao += " ⚠️ [ESTOQUE BAIXO]"

        iid_linha = None 

        if item_existente:
            nova_qtd = item_existente['qtd'] + qtd
            novo_total = round(nova_qtd * prod['preco'], 2)
            
            item_existente['qtd'] = nova_qtd
            item_existente['total'] = novo_total
            
            qtd_fmt = f"{nova_qtd:.3f}" if prod['un'] in ['KG', 'G'] else f"{int(nova_qtd)}"
            
            self.tree.item(item_existente['tree_id'], values=(item_existente['id_visual'], nome_exibicao, qtd_fmt, prod['un'], f"{prod['preco']:.2f}", f"{novo_total:.2f}"))
            iid_linha = item_existente['tree_id']
            
        else:
            self.contador_id += 1
            total = round(qtd * prod['preco'], 2)
            qtd_fmt = f"{qtd:.3f}" if prod['un'] in ['KG', 'G'] else f"{int(qtd)}"
            
            iid_linha = self.tree.insert('', 'end', values=(self.contador_id, nome_exibicao, qtd_fmt, prod['un'], f"{prod['preco']:.2f}", f"{total:.2f}"))
            
            self.carrinho.append({
                'tree_id': iid_linha,
                'id_visual': self.contador_id,
                'codigo': cod,
                'nome': prod['nome'],
                'qtd': qtd,
                'preco': prod['preco'],
                'total': total,
                'un': prod['un']
            })

        self.atualizar_total()
        self.tree.yview_moveto(1)
        self.aplicar_destaque(iid_linha)
        try: self.tree.selection_remove(self.tree.selection())
        except: pass
        self.entry_cod.focus_set()

    def aplicar_destaque(self, iid_atual):
        if self.ultimo_item_focado and self.ultimo_item_focado != iid_atual:
            try:
                tags_antigas = self.tree.item(self.ultimo_item_focado, "tags")
                if 'cancelled' not in tags_antigas and 'partial' not in tags_antigas:
                    self.tree.item(self.ultimo_item_focado, tags=()) 
            except: pass 

        self.tree.item(iid_atual, tags=('flash',))

        def fixar_verde():
            try: self.tree.item(iid_atual, tags=('active',))
            except: pass

        self.after(150, fixar_verde)
        self.ultimo_item_focado = iid_atual

    def atualizar_total(self):
        t = sum(i['total'] for i in self.carrinho)
        self.lbl_total.configure(text=f"R$ {t:.2f}")

    def cancelar_item(self):
        sel = self.tree.selection()
        if not sel: 
            messagebox.showwarning("Aviso", "Selecione um item na lista para cancelar.")
            return
        
        item_visual = sel[0]
        dados_visuais = self.tree.item(item_visual)['values']
        id_visual_alvo = int(dados_visuais[0])

        item_alvo = None
        for item in self.carrinho:
            if item['id_visual'] == id_visual_alvo:
                item_alvo = item
                break
        
        if not item_alvo: return
        qtd_atual = item_alvo['qtd']
        
        if qtd_atual <= 0: 
            messagebox.showinfo("Info", "Este item já está totalmente cancelado.")
            return

        d = ctk.CTkInputDialog(text=f"Retirar quantos?\n(Atual: {qtd_atual})", title="Retirada Parcial/Total")
        d.geometry(f"+{self.winfo_rootx() + 300}+{self.winfo_rooty() + 200}")
        resp = d.get_input()
        
        if not resp: return

        try:
            qtd_retirar = float(resp.replace(",", "."))
            if qtd_retirar <= 0: return
            if qtd_retirar > qtd_atual:
                messagebox.showerror("Erro", "Não pode retirar mais do que existe.")
                return
        except:
            messagebox.showerror("Erro", "Quantidade inválida.")
            return

        nova_qtd = qtd_atual - qtd_retirar
        novo_total = round(nova_qtd * item_alvo['preco'], 2)
        
        item_alvo['qtd'] = nova_qtd
        item_alvo['total'] = novo_total
        
        qtd_fmt = f"{nova_qtd:.3f}" if item_alvo['un'] in ['KG', 'G'] else f"{int(nova_qtd)}"
        self.tree.item(item_visual, values=(item_alvo['id_visual'], item_alvo['nome'], qtd_fmt, item_alvo['un'], f"{item_alvo['preco']:.2f}", f"{novo_total:.2f}"))

        if nova_qtd == 0:
            self.tree.item(item_visual, tags=('cancelled',))
            if self.ultimo_item_focado == item_visual: self.ultimo_item_focado = None
        else:
            self.tree.item(item_visual, tags=('partial',))
            if self.ultimo_item_focado == item_visual: self.ultimo_item_focado = None

        self.atualizar_total()
        self.tree.selection_remove(item_visual)
        self.entry_cod.focus_set()

    def cancelar_venda_total(self):
        if not self.carrinho: return
        if messagebox.askyesno("Cancelar Venda", "Tem certeza que deseja ABORTAR e LIMPAR toda a venda atual?"):
            self.carrinho = []
            self.contador_id = 0
            self.ultimo_item_focado = None
            for i in self.tree.get_children(): self.tree.delete(i)
            self.atualizar_total()
            self.entry_cod.focus_set()

    def abrir_tela_pagamento(self):
        itens_validos = [i for i in self.carrinho if i['qtd'] > 0]
        if not itens_validos:
            messagebox.showwarning("Vazio", "Passe produtos antes de finalizar.")
            self.entry_cod.focus_set()
            return
        
        self.total_a_pagar = sum(i['total'] for i in itens_validos)

        self.janela_pag = ctk.CTkToplevel(self)
        self.janela_pag.title("Forma de Pagamento")
        self.janela_pag.geometry("500x450")
        self.janela_pag.transient(self)
        self.janela_pag.grab_set()

        ctk.CTkLabel(self.janela_pag, text="TOTAL A PAGAR", font=("Arial", 14)).pack(pady=(20,5))
        ctk.CTkLabel(self.janela_pag, text=f"R$ {self.total_a_pagar:.2f}", font=("Arial", 40, "bold"), text_color=self.cor_destaque).pack(pady=(0,20))

        container = ctk.CTkFrame(self.janela_pag, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20)

        f_btns = ctk.CTkFrame(container)
        f_btns.pack(side="left", fill="both", expand=True, padx=10)
        
        ctk.CTkLabel(f_btns, text="Pagamento Direto:").pack(pady=10)
        
        ctk.CTkButton(f_btns, text="💠 PIX (QR Code)", height=40, fg_color="#8E44AD", 
                      command=self.tela_pix_espera).pack(fill="x", pady=5, padx=10)
        
        ctk.CTkButton(f_btns, text="💳 DÉBITO", height=40, fg_color="#2980B9", 
                      command=lambda: self.confirmar_pagamento("Débito")).pack(fill="x", pady=5, padx=10)
        
        ctk.CTkButton(f_btns, text="💳 CRÉDITO", height=40, fg_color="#3498DB", 
                      command=lambda: self.confirmar_pagamento("Crédito")).pack(fill="x", pady=5, padx=10)

        f_money = ctk.CTkFrame(container)
        f_money.pack(side="right", fill="both", expand=True, padx=10)
        
        ctk.CTkLabel(f_money, text="💵 DINHEIRO").pack(pady=10)
        
        self.entry_recebido = ctk.CTkEntry(f_money, placeholder_text="Valor Recebido", font=("Arial", 16))
        self.entry_recebido.pack(pady=5, padx=10)
        self.entry_recebido.bind("<KeyRelease>", self.calcular_troco_tempo_real)
        
        self.lbl_troco = ctk.CTkLabel(f_money, text="Troco: R$ 0.00", font=("Arial", 16, "bold"), text_color="gray")
        self.lbl_troco.pack(pady=20)

        self.btn_confirmar_dinheiro = ctk.CTkButton(f_money, text="CONFIRMAR", state="disabled", fg_color="gray", 
                                                    command=lambda: self.confirmar_pagamento("Dinheiro"))
        self.btn_confirmar_dinheiro.pack(side="bottom", pady=20, padx=10, fill="x")

        self.entry_recebido.focus_set()

    def tela_pix_espera(self):
        self.janela_pag.destroy()
        
        self.win_pix = ctk.CTkToplevel(self)
        self.win_pix.title("Pagamento via PIX")
        self.win_pix.geometry("400x500")
        self.win_pix.transient(self)
        self.win_pix.grab_set()

        ctk.CTkLabel(self.win_pix, text="Escaneie o QR Code", font=("Arial", 18, "bold")).pack(pady=(30,10))
        
        frame_qr = ctk.CTkFrame(self.win_pix, width=200, height=200, fg_color="black")
        frame_qr.pack(pady=10)
        ctk.CTkLabel(frame_qr, text="[ QR CODE AQUI ]", text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        self.lbl_status_pix = ctk.CTkLabel(self.win_pix, text="Aguardando confirmação do banco...", font=("Arial", 14), text_color="orange")
        self.lbl_status_pix.pack(pady=20)

        self.pontos = 0
        self.animar_texto_espera()

        ctk.CTkButton(self.win_pix, text="(DEV) Simular Pagamento Aprovado", fg_color="#555", 
                      command=self.simular_aprovacao_pix).pack(side="bottom", pady=20)

    def animar_texto_espera(self):
        if not self.win_pix.winfo_exists(): return
        self.pontos = (self.pontos + 1) % 4
        texto = "Aguardando confirmação do banco" + "." * self.pontos
        self.lbl_status_pix.configure(text=texto)
        self.after(500, self.animar_texto_espera)

    def simular_aprovacao_pix(self):
        self.lbl_status_pix.configure(text="✅ PAGAMENTO APROVADO!", text_color="#2ECC71")
        self.win_pix.update()
        self.after(1000, lambda: [self.win_pix.destroy(), self.finalizar_venda_banco("Pix")])

    def calcular_troco_tempo_real(self, event):
        texto = self.entry_recebido.get().replace(",", ".")
        try:
            recebido = float(texto)
            troco = recebido - self.total_a_pagar
            if troco >= 0:
                self.lbl_troco.configure(text=f"Troco: R$ {troco:.2f}", text_color=self.cor_destaque)
                self.btn_confirmar_dinheiro.configure(state="normal", fg_color=self.cor_destaque)
            else:
                self.lbl_troco.configure(text=f"Falta: R$ {abs(troco):.2f}", text_color="#C0392B")
                self.btn_confirmar_dinheiro.configure(state="disabled", fg_color="gray")
        except:
            self.lbl_troco.configure(text="Valor Inválido", text_color="gray")
            self.btn_confirmar_dinheiro.configure(state="disabled", fg_color="gray")

    def confirmar_pagamento(self, metodo):
        self.finalizar_venda_banco(metodo)
        self.janela_pag.destroy()

    def finalizar_venda_banco(self, metodo_pagamento):
        itens_validos = [i for i in self.carrinho if i['qtd'] > 0]
        total_final = sum(i['total'] for i in itens_validos)
        
        itens_para_salvar = []
        for item in itens_validos:
            itens_para_salvar.append({
                "produto": item['nome'], 
                "qtd": item['qtd'], 
                "total": item['total']
            })

        database.registrar_venda(total_final, itens_para_salvar, self.usuario['nome'], pagamento=metodo_pagamento)

        messagebox.showinfo("Sucesso", f"Venda Finalizada via {metodo_pagamento.upper()}!")
        
        self.carrinho = []
        self.contador_id = 0
        self.ultimo_item_focado = None
        for i in self.tree.get_children(): self.tree.delete(i)
        self.atualizar_total()
        self.entry_cod.focus_set()
        self.produtos_db = database.carregar_produtos()

    def tentar_sair(self):
        if self.carrinho:
            messagebox.showwarning("Atenção", "Venda em andamento!\n\nUse o botão 'CANCELAR VENDA' (Esc) se quiser abandonar a compra.")
            return
        self.voltar_menu()

    def mostrar_ajuda(self):
        msg = """
        🛒 CAIXA

        1. Leitor / Celular:
           - A borda VERDE indica pronto para ler.

        2. Pagamento (F5):
           - Pix: Gera QR Code simulado e aguarda aprovação.
           - Dinheiro: Calcula troco e valida valor.

        3. Atalhos:
           - F1: Ativar Leitor
           - F5: Pagamento
           - Esc: Cancelar Tudo
           - Del: Cancelar Item
        """
        messagebox.showinfo("Ajuda", msg)