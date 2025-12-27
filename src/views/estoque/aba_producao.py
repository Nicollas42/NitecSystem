# src/views/estoque/aba_producao.py
import customtkinter as ctk
from tkinter import ttk, messagebox

class AbaProducao(ctk.CTkFrame):
    """
    Classe responsável pela interface de registro de produção diária.
    Gerencia a seleção de produtos com ficha técnica e envia ordem de produção.
    """

    def __init__(self, master, controller, produtos_ref, callback_atualizar):
        super().__init__(master)
        self.controller = controller
        self.produtos = produtos_ref
        self.callback_atualizar = callback_atualizar
        self.receitas_cache = {}
        self.id_selecionado = None 
        self.janela_ajuda = None
        
        self.montar_layout()

    def montar_layout(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # --- ESQUERDA: LISTA DE O QUE PRODUZIR ---
        frame_esq = ctk.CTkFrame(self, fg_color="#2b2b2b")
        frame_esq.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # --- HEADER DO LADO ESQUERDO (TÍTULO + AJUDA) ---
        header_esq = ctk.CTkFrame(frame_esq, fg_color="transparent")
        header_esq.pack(fill="x", pady=15)

        ctk.CTkLabel(header_esq, text="1. O que será produzido?", font=("Arial", 16, "bold"), text_color="#2CC985").pack(side="left", padx=(10, 5))
        ctk.CTkButton(header_esq, text="?", width=25, height=25, fg_color="#2980B9", hover_color="#1F618D",
                      command=self.mostrar_ajuda).pack(side="left")
        
        ctk.CTkLabel(frame_esq, text="(Mostrando apenas produtos com Ficha Técnica)", font=("Arial", 10), text_color="gray").pack()

        self.tree_prod = ttk.Treeview(frame_esq, columns=("nome",), show="headings")
        self.tree_prod.heading("nome", text="Produtos Prontos para Produção")
        self.tree_prod.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tree_prod.bind("<<TreeviewSelect>>", self.selecionar_produto)

        # --- DIREITA: DETALHES E AÇÃO ---
        frame_dir = ctk.CTkFrame(self)
        frame_dir.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.lbl_titulo = ctk.CTkLabel(frame_dir, text="Selecione um produto...", font=("Arial", 20, "bold"))
        self.lbl_titulo.pack(pady=(20, 10))

        # Info do Rendimento Base
        self.lbl_subtitulo = ctk.CTkLabel(frame_dir, text="", font=("Arial", 12, "bold"), text_color="#aaa")
        self.lbl_subtitulo.pack(pady=(0, 5))

        ctk.CTkLabel(frame_dir, text="Insumos que serão consumidos:", font=("Arial", 12)).pack(anchor="w", padx=40)
        
        # Lista com rolagem para mostrar os ingredientes
        self.scroll_ingredientes = ctk.CTkScrollableFrame(frame_dir, height=150, fg_color="#333", border_width=1, border_color="#444")
        self.scroll_ingredientes.pack(fill="x", padx=40, pady=5)

        # --- CAMPO DE QUANTIDADE COM UNIDADE ---
        self.frame_qtd = ctk.CTkFrame(frame_dir, fg_color="transparent")
        self.frame_qtd.pack(pady=20)
        
        ctk.CTkLabel(self.frame_qtd, text="Quantidade Produzida Hoje:").pack(pady=(0, 5))
        
        # Container horizontal para alinhar Entrada + Label da Unidade
        f_input_row = ctk.CTkFrame(self.frame_qtd, fg_color="transparent")
        f_input_row.pack()

        self.ent_qtd = ctk.CTkEntry(f_input_row, width=150, font=("Arial", 24), justify="center")
        self.ent_qtd.pack(side="left", padx=5)
        self.ent_qtd.bind("<Return>", lambda e: self.confirmar_producao())

        # Label da Unidade ao lado do campo (Ex: KG)
        self.lbl_unidade_input = ctk.CTkLabel(f_input_row, text="UN", font=("Arial", 18, "bold"), text_color="#aaa")
        self.lbl_unidade_input.pack(side="left", padx=5)
        # ---------------------------------------
        
        self.btn_produzir = ctk.CTkButton(frame_dir, text="🏭 REGISTRAR PRODUÇÃO", height=60, fg_color="#E67E22",
                                          state="disabled", command=self.confirmar_producao)
        self.btn_produzir.pack(pady=20, padx=40, fill="x")

        # Aviso
        ctk.CTkLabel(frame_dir, text="⚠️ Isso irá baixar os insumos do estoque automaticamente.", 
                     text_color="#E74C3C", font=("Arial", 11)).pack(side="bottom", pady=20)

    def atualizar(self):
        self.tree_prod.delete(*self.tree_prod.get_children())
        self.receitas_cache = self.controller.carregar_receitas()
        
        # Limpa a área da direita
        for w in self.scroll_ingredientes.winfo_children(): w.destroy()
        self.lbl_titulo.configure(text="Selecione um produto...")
        self.lbl_subtitulo.configure(text="")
        
        for id_prod, receita in self.receitas_cache.items():
            nome = receita.get('nome', '???')
            self.tree_prod.insert("", "end", values=(nome,), tags=(str(id_prod),))

    def selecionar_produto(self, event):
        sel = self.tree_prod.selection()
        if not sel: return
        
        item = self.tree_prod.item(sel[0])
        id_prod = str(item['tags'][0]) 
        nome = item['values'][0]
        
        self.id_selecionado = id_prod
        self.lbl_titulo.configure(text=nome)
        
        # Limpa lista anterior
        for w in self.scroll_ingredientes.winfo_children(): w.destroy()

        receita = self.receitas_cache.get(id_prod)
        
        if receita:
            # Info do Rendimento
            rend = receita.get('rendimento', 1)
            unidade_prod = self.produtos.get(id_prod, {}).get('unidade', 'UN')
            
            self.lbl_subtitulo.configure(text=f"Receita Base para: {rend} {unidade_prod}")
            
            # ATUALIZA A UNIDADE AO LADO DO CAMPO DE DIGITAÇÃO
            self.lbl_unidade_input.configure(text=unidade_prod)

            # Lista os Ingredientes
            ingredientes = receita.get('ingredientes', [])
            
            if not ingredientes:
                ctk.CTkLabel(self.scroll_ingredientes, text="Sem ingredientes cadastrados.").pack()
            
            for ing in ingredientes:
                id_insumo = str(ing.get('id'))
                nome_insumo = ing.get('nome') or self.produtos.get(id_insumo, {}).get('nome', 'Item Desconhecido')
                qtd_insumo = float(ing.get('qtd', 0))
                unidade_insumo = self.produtos.get(id_insumo, {}).get('unidade', 'UN')
                
                qtd_fmt = f"{int(qtd_insumo)}" if qtd_insumo.is_integer() else f"{qtd_insumo:.3f}"
                texto_linha = f"• {qtd_fmt} {unidade_insumo} - {nome_insumo}"
                
                lbl = ctk.CTkLabel(self.scroll_ingredientes, text=texto_linha, anchor="w")
                lbl.pack(fill="x", padx=5, pady=2)

            self.btn_produzir.configure(state="normal")
            self.ent_qtd.focus_set()
        else:
            self.lbl_subtitulo.configure(text="Erro: Receita não encontrada.")
            self.btn_produzir.configure(state="disabled")

    def confirmar_producao(self):
        if not self.id_selecionado: return
        
        qtd_str = self.ent_qtd.get().replace(",", ".")
        try:
            qtd = float(qtd_str)
            if qtd <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Digite uma quantidade válida (maior que zero).")
            return

        nome = self.lbl_titulo.cget("text")
        unidade = self.lbl_unidade_input.cget("text") # Pega a unidade atual
        
        # MENSAGEM CORRIGIDA COM UNIDADE
        msg_confirm = f"Confirma a produção de {qtd} {unidade} de {nome}?\n\nOs estoques de farinha/insumos serão descontados proporcionalmente."
        
        if not messagebox.askyesno("Confirmar Produção", msg_confirm):
            return

        ok, msg = self.controller.registrar_producao(self.id_selecionado, qtd, "Admin")
        
        if ok:
            messagebox.showinfo("Sucesso", msg)
            self.ent_qtd.delete(0, "end")
            self.lbl_titulo.configure(text="Selecione um produto...")
            self.lbl_subtitulo.configure(text="")
            self.lbl_unidade_input.configure(text="UN")
            for w in self.scroll_ingredientes.winfo_children(): w.destroy()
            self.btn_produzir.configure(state="disabled")
            self.id_selecionado = None
            self.callback_atualizar()
        else:
            messagebox.showerror("Erro", msg)

    def mostrar_ajuda(self):
        if self.janela_ajuda and self.janela_ajuda.winfo_exists():
            self.janela_ajuda.lift(); self.janela_ajuda.focus_force(); return
        
        self.janela_ajuda = ctk.CTkToplevel(self)
        self.janela_ajuda.title("Manual - Produção")
        self.janela_ajuda.geometry("550x450")
        self.janela_ajuda.transient(self)
        self.janela_ajuda.lift()
        self.janela_ajuda.focus_force()
        
        ctk.CTkLabel(self.janela_ajuda, text="🏭 REGISTRO DE PRODUÇÃO", font=("Arial", 20, "bold"), text_color="#2CC985").pack(pady=20)
        
        texto_ajuda = """
🎯 PARA QUE SERVE ESTA TELA?
Para dizer ao sistema que você fabricou produtos. 
Isso atualiza o estoque automaticamente em duas pontas.

🛠️ COMO USAR:

1️⃣ SELECIONE O PRODUTO (Lista à Esquerda)
   Clique no item que você acabou de fabricar (Ex: Pão Francês).
   *Nota: Só aparecem produtos que têm Ficha Técnica cadastrada.*

2️⃣ CONFIRA A RECEITA (Painel à Direita)
   O sistema mostrará a lista de ingredientes que serão usados.

3️⃣ INFORME A QUANTIDADE
   Digite quanto você produziu hoje.
   Exemplo: Se a masseira rendeu 50 KG de pão, digite "50".

4️⃣ CLIQUE EM "REGISTRAR PRODUÇÃO"
   O sistema fará o cálculo proporcional (Regra de 3) e:
   🔻 Descontará a Farinha, Sal, Fermento do estoque.
   🔺 Adicionará o Pão Francês pronto no estoque.
"""
        lbl = ctk.CTkLabel(self.janela_ajuda, text=texto_ajuda, justify="left", anchor="nw", padx=20, font=("Consolas", 13))
        lbl.pack(fill="both", expand=True)