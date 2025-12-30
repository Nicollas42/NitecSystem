# src/controllers/estoque_controller.py
import datetime
import os 
from datetime import datetime as dt 
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
        self.ARQ_RECEITAS = os.path.join(self.db.DATA_DIR, "receitas.json")
        self.ARQ_MAQUINAS = os.path.join(self.db.DATA_DIR, "maquinas.json")
        self.ARQ_TARIFAS = os.path.join(self.db.DATA_DIR, "tarifas.json")

    # --- MÁQUINAS E TARIFAS ---
    def carregar_tarifas(self):
        padrao = {"energia_kwh": 0.90, "gas_kg": 8.50, "agua_m3": 12.00, "mao_obra_h": 15.00}
        return self.db.carregar_json(self.ARQ_TARIFAS) or padrao

    def salvar_tarifas(self, tarifas_dict):
        self.db.salvar_json(self.ARQ_TARIFAS, tarifas_dict)
        return True, "Tarifas atualizadas!"

    def carregar_maquinas(self):
        return self.db.carregar_json(self.ARQ_MAQUINAS) or {}

    def salvar_maquina(self, id_maq, nome, potencia_w, consumo_gas_kg_h):
        maquinas = self.carregar_maquinas()
        maquinas[id_maq] = {
            "id": id_maq, "nome": nome, 
            "potencia_w": float(potencia_w), 
            "gas_kg_h": float(consumo_gas_kg_h)
        }
        self.db.salvar_json(self.ARQ_MAQUINAS, maquinas)
        return True, "Máquina salva!"

    # --- RECEITAS ---
    def carregar_receitas(self):
        return self.db.carregar_json(self.ARQ_RECEITAS)

    def salvar_receita(self, id_produto, rendimento, ingredientes):
        return self.salvar_receita_avancada(id_produto, rendimento, ingredientes, [], 0, 100)

    def salvar_receita_avancada(self, id_produto, rendimento, ingredientes, maquinas_uso, tempo_mao_obra_min, margem_lucro):
        id_produto = str(id_produto)
        receitas = self.carregar_receitas()
        produtos = self.db.carregar_produtos()
        tarifas = self.carregar_tarifas()
        
        if id_produto not in produtos: return False, "Produto não encontrado."

        # --- CORREÇÃO IMPORTANTE: Enriquecer ingredientes com Nome e Unidade ---
        ingredientes_completos = []
        custo_insumos = 0.0
        
        for ing in ingredientes:
            item_db = produtos.get(str(ing['id']))
            if item_db:
                # Garante que temos o nome e unidade salvos na receita
                nome_final = ing.get('nome') or item_db['nome']
                unidade_final = ing.get('un') or item_db.get('unidade', 'UN')
                
                # Cálculo de Custo
                qtd = float(ing['qtd'])
                custo_unit = float(item_db.get('custo', 0))
                custo_total_ing = qtd * custo_unit
                custo_insumos += custo_total_ing
                
                ingredientes_completos.append({
                    "id": str(ing['id']),
                    "nome": nome_final,
                    "qtd": qtd,
                    "un": unidade_final,
                    "custo_aprox": round(custo_total_ing, 4)
                })
        # -----------------------------------------------------------------------

        # 2. Custos de Máquinas
        custo_maquinas = 0.0
        bd_maquinas = self.carregar_maquinas()
        maquinas_completas = []
        
        for uso in maquinas_uso:
            maq = bd_maquinas.get(uso['id'])
            if maq:
                tempo_h = float(uso['tempo_min']) / 60.0
                kwh = (maq['potencia_w'] / 1000) * tempo_h
                custo_luz = kwh * tarifas['energia_kwh']
                gas_kg = maq['gas_kg_h'] * tempo_h
                custo_gas = gas_kg * tarifas['gas_kg']
                
                total_maq = custo_luz + custo_gas
                custo_maquinas += total_maq
                
                maquinas_completas.append({
                    "id": uso['id'],
                    "nome": maq['nome'], # Salva o nome da máquina também
                    "tempo_min": uso['tempo_min']
                })

        # 3. Mão de Obra
        horas_homen = float(tempo_mao_obra_min) / 60.0
        custo_mod = horas_homen * tarifas['mao_obra_h']

        # 4. Totais
        custo_total_lote = custo_insumos + custo_maquinas + custo_mod
        rendimento_float = float(rendimento)
        custo_unitario = custo_total_lote / rendimento_float if rendimento_float > 0 else 0

        # 5. Precificação
        margem = float(margem_lucro) / 100.0
        preco_sugerido = custo_unitario * (1 + margem)

        receitas[id_produto] = {
            "id_produto": id_produto,
            "nome": produtos[id_produto]['nome'],
            "rendimento": rendimento_float,
            "tempo_preparo": float(tempo_mao_obra_min),
            "custos": {
                "insumos": round(custo_insumos, 4),
                "maquinas": round(custo_maquinas, 4),
                "mao_obra": round(custo_mod, 4),
                "total_lote": round(custo_total_lote, 4),
                "unitario": round(custo_unitario, 4)
            },
            "ingredientes": ingredientes_completos, # Lista corrigida
            "maquinas_uso": maquinas_completas,     # Lista corrigida
            "margem_lucro": float(margem_lucro)
        }
        self.db.salvar_json(self.ARQ_RECEITAS, receitas)

        produtos[id_produto]['custo'] = round(custo_unitario, 4)
        produtos[id_produto]['preco'] = round(preco_sugerido, 2)
        self.db.salvar_produtos(produtos)

        return True, f"Custo: R$ {custo_unitario:.2f} | Sugerido: R$ {preco_sugerido:.2f}"

    # ... MÉTODOS PADRÃO (PRODUTOS E ESTOQUE) ...
    def salvar_produto(self, dados_produto):
        produtos = self.db.carregar_produtos()
        novo_id = str(dados_produto['id'])
        # ... (Logica de salvar igual) ...
        # (Para economizar espaço, se já estiver funcionando, mantenha o resto do arquivo igual ao anterior)
        # O IMPORTANTE FOI A ALTERAÇÃO NO salvar_receita_avancada ACIMA
        
        # Vou colar o resto apenas para garantir integridade se você substituir tudo:
        novo_nome = dados_produto['nome'].strip().upper()
        novo_grupo = str(dados_produto.get('grupo', '')).strip().upper()
        novos_eans = dados_produto.get('codigos_barras', []) 
        if isinstance(novos_eans, str): novos_eans = []

        for pid, prod in produtos.items():
            if pid == novo_id: continue
            if prod['nome'].strip().upper() == novo_nome: return False, f"Nome já existe (ID {pid})."
            if set(novos_eans).intersection(set(prod.get('codigos_barras', []))): return False, "EAN duplicado."

        item_atual = produtos.get(novo_id, {})
        produtos[novo_id] = {
            "id": novo_id, "nome": novo_nome, "grupo": novo_grupo, "codigos_barras": novos_eans,
            "unidade": dados_produto.get('unidade', 'UN'), "categoria": dados_produto.get('categoria', 'Outros'),
            "tipo": dados_produto.get('tipo', 'PRODUTO'), "controla_estoque": dados_produto.get('controla_estoque', True),
            "estoque_atual": item_atual.get('estoque_atual', 0.0), "estoque_fundo": item_atual.get('estoque_fundo', 0.0),
            "estoque_minimo": float(str(dados_produto.get('minimo', 0)).replace(',', '.')),
            "preco": float(str(dados_produto.get('preco', 0)).replace(',', '.')),
            "custo": float(str(dados_produto.get('custo', 0)).replace(',', '.')),
            "data_cadastro": item_atual.get('data_cadastro', dt.now().strftime("%d/%m/%Y")), "ativo": True
        }
        self.db.salvar_produtos(produtos)
        return True, "Salvo!"

    def movimentar_estoque(self, produto_id, qtd, tipo_mov, motivo="", usuario="Admin", local="fundo"):
        produtos = self.db.carregar_produtos()
        if produto_id not in produtos: return False, "Produto não encontrado."
        prod = produtos[produto_id]
        chave = 'estoque_atual' if local == "frente" else 'estoque_fundo'
        try: qtd = float(str(qtd).replace(',', '.'))
        except: return False, "Qtd inválida."
        saldo_ant = prod.get(chave, 0.0)
        novo = saldo_ant + qtd if "ENTRADA" in tipo_mov.upper() else saldo_ant - qtd
        prod[chave] = round(novo, 4)
        self.db.salvar_produtos(produtos)
        self.db.registrar_movimentacao(f"{tipo_mov}_{local.upper()}", produto_id, prod['nome'], qtd, motivo, usuario, saldo_ant, novo)
        return True, "OK"

    def transferir_fundo_para_frente(self, pid, qtd, user="admin", mot=None):
        produtos = self.db.carregar_produtos()
        if pid not in produtos: return False, "Erro"
        try: qtd = float(str(qtd).replace(',', '.'))
        except: return False, "Erro"
        if produtos[pid].get('estoque_fundo', 0) < qtd: return False, "Saldo Fundo Insuficiente"
        self.movimentar_estoque(pid, qtd, "SAIDA_TRANSFERENCIA", mot, user, "fundo")
        self.movimentar_estoque(pid, qtd, "ENTRADA_TRANSFERENCIA", mot, user, "frente")
        return True, "OK"

    def registrar_producao(self, id_final, qtd, usuario):
        id_final = str(id_final)
        receitas = self.carregar_receitas()
        if id_final not in receitas:
            self.movimentar_estoque(id_final, qtd, TIPO_ENTRADA_PRODUCAO, "Produção Avulsa", usuario, "fundo")
            return True, "Produção sem baixa"
        rec = receitas[id_final]
        fator = float(qtd) / float(rec.get('rendimento', 1))
        for ing in rec.get('ingredientes', []):
            self.movimentar_estoque(str(ing['id']), float(ing['qtd']) * fator, TIPO_SAIDA_PRODUCAO, f"Prod {qtd} {rec['nome']}", usuario, "fundo")
        self.movimentar_estoque(id_final, qtd, TIPO_ENTRADA_PRODUCAO, "Produção Concluída", usuario, "fundo")
        return True, "Produção OK"