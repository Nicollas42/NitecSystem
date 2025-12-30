import customtkinter as ctk
from tkinter import ttk

class TabMaquinas(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.maquinas_lista = []
        self.montar_layout()

    def montar_layout(self):
        # Botões de Configuração
        f_top = ctk.CTkFrame(self, fg_color="transparent")
        f_top.pack(fill="x", pady=5)
        
        ctk.CTkButton(f_top, text="⚙️ Tarifas", fg_color="#555", width=100, 
                      command=self.popup_tarifas).pack(side="right", padx=5)
        ctk.CTkButton(f_top, text="➕ Máquina", fg_color="#555", width=100, 
                      command=self.popup_criar_maquina).pack(side="right", padx=5)

        # Adicionar Uso
        f_add = ctk.CTkFrame(self, fg_color="transparent")
        f_add.pack(fill="x", pady=10)
        
        ctk.CTkLabel(f_add, text="Equipamento:").pack(side="left")
        
        # INICIALIZA VAZIO - SERÁ CARREGADO DEPOIS
        self.combo_maquinas = ctk.CTkComboBox(f_add, values=["Carregando..."], width=200)
        self.combo_maquinas.pack(side="left", padx=5)
        
        ctk.CTkLabel(f_add, text="Tempo (min):").pack(side="left")
        self.ent_tempo = ctk.CTkEntry(f_add, width=60)
        self.ent_tempo.pack(side="left", padx=5)
        
        ctk.CTkButton(f_add, text="+ Usar", width=60, command=self.adicionar).pack(side="left", padx=5)

        # Tabela
        self.tree = ttk.Treeview(self, columns=("nome", "tempo"), show="headings", height=6)
        self.tree.heading("nome", text="Equipamento")
        self.tree.heading("tempo", text="Tempo de Uso")
        self.tree.column("nome", width=250)
        self.tree.column("tempo", width=100, anchor="center")
        self.tree.pack(fill="both", expand=True, pady=5)
        
        ctk.CTkButton(self, text="Remover Máquina", fg_color="#C0392B", height=25, 
                      command=self.remover).pack(pady=5)

        # Mão de Obra
        f_mo = ctk.CTkFrame(self, border_width=1, border_color="#555")
        f_mo.pack(fill="x", pady=10, padx=5)
        ctk.CTkLabel(f_mo, text="👨‍🍳 Mão de Obra (Tempo Humano em Minutos):").pack(side="left", padx=10)
        self.ent_tempo_humano = ctk.CTkEntry(f_mo, width=80)
        self.ent_tempo_humano.pack(side="left", padx=10, pady=10)

    def atualizar_dados(self, dados_maquinas, tempo_homem):
        self.maquinas_lista = dados_maquinas
        self.ent_tempo_humano.delete(0, 'end')
        self.ent_tempo_humano.insert(0, tempo_homem)
        self.carregar_combo()
        self.renderizar()

    def get_tempo_humano(self):
        return self.ent_tempo_humano.get()

    def carregar_combo(self):
        maquinas = self.controller.carregar_maquinas()
        print(f"DEBUG [TabMaquinas]: Carregando combo. Máquinas no DB: {len(maquinas)}")
        
        lista = [f"{v['id']} - {v['nome']}" for v in maquinas.values()]
        
        if not lista:
            print("DEBUG [TabMaquinas]: Nenhuma máquina encontrada! Lista vazia.")
            self.combo_maquinas.configure(values=["Nenhuma Máquina"])
            self.combo_maquinas.set("Nenhuma Máquina")
        else:
            self.combo_maquinas.configure(values=lista)
            self.combo_maquinas.set(lista[0]) # Pega o primeiro item

    def adicionar(self):
        sel = self.combo_maquinas.get()
        tempo = self.ent_tempo.get()
        print(f"DEBUG [TabMaquinas]: Tentando adicionar '{sel}' tempo '{tempo}'")
        
        if not sel or " - " not in sel:
            print("DEBUG [TabMaquinas]: Seleção inválida.")
            return

        if sel and tempo:
            id_maq = sel.split(" - ")[0]
            nome_maq = sel.split(" - ")[1]
            self.maquinas_lista.append({"id": id_maq, "nome": nome_maq, "tempo_min": tempo})
            self.renderizar()

    def remover(self):
        sel = self.tree.selection()
        if sel:
            idx = self.tree.index(sel[0])
            del self.maquinas_lista[idx]
            self.renderizar()

    def renderizar(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for maq in self.maquinas_lista:
            self.tree.insert("", "end", values=(maq['nome'], f"{maq['tempo_min']} min"))

    # --- POPUPS ---
    def popup_tarifas(self):
        t = ctk.CTkToplevel(self)
        t.title("Configurar Tarifas")
        t.geometry("300x250")
        vals = self.controller.carregar_tarifas()
        entries = {}
        campos = [("Energia (R$/kWh)", "energia_kwh"), ("Gás (R$/kg)", "gas_kg"), 
                  ("Água (R$/m³)", "agua_m3"), ("Mão de Obra (R$/h)", "mao_obra_h")]
        for i, (txt, key) in enumerate(campos):
            ctk.CTkLabel(t, text=txt).pack()
            e = ctk.CTkEntry(t)
            e.insert(0, vals.get(key, 0))
            e.pack()
            entries[key] = e
        def salvar():
            novos = {k: float(e.get().replace(",", ".")) for k, e in entries.items()}
            self.controller.salvar_tarifas(novos)
            t.destroy()
        ctk.CTkButton(t, text="Salvar", command=salvar).pack(pady=20)

    def popup_criar_maquina(self):
        t = ctk.CTkToplevel(self)
        t.title("Nova Máquina")
        t.geometry("300x300")
        ctk.CTkLabel(t, text="Nome").pack(); e_nome = ctk.CTkEntry(t); e_nome.pack()
        ctk.CTkLabel(t, text="Potência (W)").pack(); e_watts = ctk.CTkEntry(t); e_watts.pack()
        ctk.CTkLabel(t, text="Consumo Gás (kg/h)").pack(); e_gas = ctk.CTkEntry(t); e_gas.insert(0,"0"); e_gas.pack()
        def salvar():
            import random
            mid = str(random.randint(1000, 9999))
            self.controller.salvar_maquina(mid, e_nome.get(), e_watts.get(), e_gas.get())
            self.carregar_combo() # Recarrega a lista
            t.destroy()
        ctk.CTkButton(t, text="Criar", command=salvar).pack(pady=20)