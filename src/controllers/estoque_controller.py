# src/controllers/estoque_controller.py
import datetime
from datetime import datetime as dt
from django.db import transaction
from django.forms.models import model_to_dict
from gestao.models import Produto, Maquina, Receita, Movimentacao, Tarifa, Venda

# Constantes de Movimentação
TIPO_ENTRADA_COMPRA = "ENTRADA_COMPRA" 
TIPO_SAIDA_VENDA = "SAIDA_VENDA"
TIPO_SAIDA_PRODUCAO = "SAIDA_PRODUCAO" 
TIPO_ENTRADA_PRODUCAO = "ENTRADA_PRODUCAO" 
TIPO_AJUSTE_PERDA = "SAIDA_PERDA"
TIPO_AJUSTE_SOBRA = "ENTRADA_AJUSTE"

class EstoqueController:
    def __init__(self):
        pass

    def _converter_decimal(self, obj_dict):
        """Converte Decimals do Django para float (para o Tkinter não quebrar)"""
        for k, v in obj_dict.items():
            if hasattr(v, 'to_eng_string'): # Checa se é Decimal
                obj_dict[k] = float(v)
        return obj_dict

    # --- LEITURA DE DADOS (CONSULTAS) ---
    def carregar_produtos(self):
        """Busca todos os produtos ativos do PostgreSQL"""
        produtos = Produto.objects.filter(ativo=True)
        dic_final = {}
        for p in produtos:
            dado = model_to_dict(p)
            dado = self._converter_decimal(dado)
            dado['id'] = str(dado['id'])
            dic_final[dado['id']] = dado
        return dic_final

    def carregar_movimentacoes(self):
        """Busca histórico completo de movimentações"""
        movs = Movimentacao.objects.all().order_by('-data')
        lista = []
        for m in movs:
            dado = model_to_dict(m)
            dado = self._converter_decimal(dado)
            if m.data:
                dado['data'] = m.data.strftime("%Y-%m-%d %H:%M:%S")
            # Garante campos para evitar erros na UI
            dado['cod'] = str(m.cod_produto.id) if m.cod_produto else ""
            dado['nome'] = m.nome_produto or ""
            dado['usuario'] = m.usuario or "Sistema"
            dado['motivo'] = m.motivo or ""
            lista.append(dado)
        return lista

    def carregar_vendas(self):
        """Busca histórico completo de vendas"""
        vendas = Venda.objects.all().order_by('-data')
        lista = []
        for v in vendas:
            dado = model_to_dict(v)
            dado = self._converter_decimal(dado)
            if v.data:
                dado['data'] = v.data.strftime("%d/%m/%Y %H:%M")
            lista.append(dado)
        return lista

    # --- VENDAS (CAIXA) ---
    def registrar_venda(self, total, itens, operador, pagamento):
        try:
            with transaction.atomic():
                # 1. Salva a Venda
                venda = Venda.objects.create(
                    data=dt.now(),
                    total=total,
                    pagamento=pagamento,
                    operador=operador,
                    itens=itens
                )

                # 2. Baixa Estoque (Frente)
                for item in itens:
                    prod = None
                    cod = item.get('codigo')
                    
                    # Tenta buscar pelo ID direto
                    if cod:
                        try: prod = Produto.objects.get(id=cod)
                        except: pass
                    
                    # Se não achar, tenta pelo nome (fallback)
                    if not prod:
                        nome = item.get('produto')
                        prod = Produto.objects.filter(nome=nome).first()

                    if prod:
                        qtd = float(item['qtd'])
                        prod.estoque_atual = float(prod.estoque_atual) - qtd
                        prod.save()
                        
                        Movimentacao.objects.create(
                            data=dt.now(),
                            cod_produto=prod,
                            nome_produto=prod.nome,
                            qtd=qtd,
                            tipo="SAIDA_VENDA_FRENTE",
                            motivo=f"Venda #{venda.id}",
                            usuario=operador,
                            saldo_anterior=float(prod.estoque_atual) + qtd,
                            saldo_novo=float(prod.estoque_atual)
                        )
            return True, f"Venda {venda.id} registrada!"
        except Exception as e:
            return False, f"Erro ao gravar venda: {e}"

    # --- MÁQUINAS E TARIFAS ---
    def carregar_tarifas(self):
        padrao = {"energia_kwh": 0.90, "gas_kg": 8.50, "agua_m3": 12.00, "mao_obra_h": 15.00}
        tarifas_db = Tarifa.objects.all()
        if not tarifas_db.exists(): 
            return padrao
        return {t.chave: float(t.valor) for t in tarifas_db}

    def salvar_tarifas(self, tarifas_dict):
        try:
            with transaction.atomic():
                for k, v in tarifas_dict.items():
                    Tarifa.objects.update_or_create(chave=k, defaults={'valor': v})
            return True, "Tarifas atualizadas!"
        except Exception as e: 
            return False, f"Erro: {e}"

    def carregar_maquinas(self):
        maquinas = Maquina.objects.all()
        dic_final = {}
        for m in maquinas:
            dado = model_to_dict(m)
            dic_final[m.id] = self._converter_decimal(dado)
        return dic_final

    def salvar_maquina(self, id_maq, nome, potencia_w, consumo_gas_kg_h):
        try:
            Maquina.objects.update_or_create(
                id=id_maq,
                defaults={'nome': nome, 'potencia_w': potencia_w, 'gas_kg_h': consumo_gas_kg_h}
            )
            return True, "Máquina salva!"
        except Exception as e: 
            return False, str(e)

    # --- RECEITAS ---
    def carregar_receitas(self):
        receitas = Receita.objects.all()
        dic_final = {}
        for r in receitas:
            dado = model_to_dict(r)
            dado = self._converter_decimal(dado)
            dado['custos'] = {
                "insumos": dado.pop('custo_insumos', 0),
                "maquinas": dado.pop('custo_maquinas', 0),
                "mao_obra": dado.pop('custo_mao_obra', 0),
                "total_lote": dado.pop('custo_total_lote', 0),
                "unitario": dado.pop('custo_unitario', 0)
            }
            if hasattr(r.id_produto, 'id'): 
                dado['id_produto'] = str(r.id_produto.id)
            dic_final[dado['id_produto']] = dado
        return dic_final

    def salvar_receita_avancada(self, id_produto, rendimento, ingredientes, maquinas_uso, tempo_mao_obra_min, margem_lucro, imposto_perc=0.0, novo_preco_venda=0.0):
        try:
            try: 
                produto = Produto.objects.get(id=id_produto)
            except Produto.DoesNotExist: 
                return False, "Produto não encontrado."
            
            tarifas = self.carregar_tarifas()
            
            # 1. Custos Insumos
            custo_insumos = 0.0
            ingredientes_completos = []
            
            for ing in ingredientes:
                try:
                    item_db = Produto.objects.get(id=str(ing['id']))
                    nome_final = ing.get('nome') or item_db.nome
                    unidade_final = ing.get('un') or item_db.unidade
                    custo_unit_ing = float(item_db.custo)
                except: 
                    continue

                qtd = float(ing['qtd'])
                total_ing = qtd * custo_unit_ing
                custo_insumos += total_ing
                ingredientes_completos.append({
                    "id": str(ing['id']), 
                    "nome": nome_final, 
                    "qtd": qtd,
                    "un": unidade_final, 
                    "custo_aprox": round(total_ing, 4)
                })

            # 2. Custos Máquinas
            custo_maquinas = 0.0
            maquinas_completas = []
            for uso in maquinas_uso:
                try:
                    maq = Maquina.objects.get(id=uso['id'])
                    tempo_h = float(uso['tempo_min']) / 60.0
                    kwh = (float(maq.potencia_w) / 1000) * tempo_h
                    gas = float(maq.gas_kg_h) * tempo_h
                    custo = (kwh * tarifas['energia_kwh']) + (gas * tarifas['gas_kg'])
                    custo_maquinas += custo
                    maquinas_completas.append({
                        "id": uso['id'], 
                        "nome": maq.nome, 
                        "tempo_min": uso['tempo_min']
                    })
                except: 
                    continue

            # 3. Mão de Obra e Totais
            tempo_h_mo = float(tempo_mao_obra_min) / 60.0
            custo_mod = tempo_h_mo * tarifas['mao_obra_h']
            
            custo_total_lote = custo_insumos + custo_maquinas + custo_mod
            rend_float = float(rendimento)
            custo_unitario = custo_total_lote / rend_float if rend_float > 0 else 0

            # 4. Precificação
            margem = float(margem_lucro) / 100.0
            imposto = float(imposto_perc) / 100.0
            
            divisor = 1 - imposto
            if divisor <= 0: divisor = 0.01
            
            preco_sugerido = (custo_unitario * (1 + margem)) / divisor
            
            preco_final = preco_sugerido
            if novo_preco_venda:
                try:
                    val_manual = float(str(novo_preco_venda).replace(',', '.'))
                    if val_manual > 0: 
                        preco_final = val_manual
                except: pass

            # 5. Salva Receita
            Receita.objects.update_or_create(
                id_produto=produto,
                defaults={
                    'nome': produto.nome, 
                    'rendimento': rend_float, 
                    'tempo_preparo': float(tempo_mao_obra_min),
                    'margem_lucro': float(margem_lucro), 
                    'imposto_perc': float(imposto_perc),
                    'custo_insumos': custo_insumos, 
                    'custo_maquinas': custo_maquinas, 
                    'custo_mao_obra': custo_mod, 
                    'custo_total_lote': custo_total_lote, 
                    'custo_unitario': custo_unitario,
                    'ingredientes': ingredientes_completos, 
                    'maquinas_uso': maquinas_completas
                }
            )

            # 6. Atualiza Produto Principal
            produto.custo = custo_unitario
            produto.preco = preco_final
            produto.save()

            return True, f"Custo: R$ {custo_unitario:.2f} | Venda: R$ {preco_final:.2f}"
        except Exception as e: 
            return False, f"Erro: {e}"

    # --- PRODUTOS E MOVIMENTAÇÃO ---
    def salvar_produto(self, dados):
        try:
            pid = str(dados['id']).strip()
            if not pid or not dados['nome']: 
                return False, "ID e Nome obrigatórios."
            
            # Verifica duplicidade de nome (exceto se for o mesmo ID)
            if Produto.objects.filter(nome__iexact=dados['nome'].strip()).exclude(id=pid).exists():
                return False, "Já existe um produto com este Nome."

            Produto.objects.update_or_create(
                id=pid,
                defaults={
                    'nome': dados['nome'].strip().upper(),
                    'grupo': dados.get('grupo', '').strip().upper(),
                    'tipo': dados.get('tipo', 'PRODUTO'),
                    'unidade': dados.get('unidade', 'UN'),
                    'categoria': dados.get('categoria', ''),
                    'preco': float(str(dados.get('preco', 0)).replace(',', '.')),
                    'custo': float(str(dados.get('custo', 0)).replace(',', '.')),
                    'estoque_minimo': float(str(dados.get('minimo', 0)).replace(',', '.')),
                    'controla_estoque': dados.get('controla_estoque', True),
                    'codigos_barras': dados.get('codigos_barras', []),
                    'data_cadastro': dt.now().date(),
                    'ativo': True
                }
            )
            return True, "Produto salvo no PostgreSQL!"
        except Exception as e: 
            return False, str(e)

    def movimentar_estoque(self, produto_id, qtd, tipo_mov, motivo="", usuario="Admin", local="fundo"):
        try:
            with transaction.atomic():
                try: 
                    prod = Produto.objects.select_for_update().get(id=produto_id)
                except Produto.DoesNotExist: 
                    return False, "Produto não encontrado."

                qtd_float = float(str(qtd).replace(',', '.'))
                saldo_ant = float(prod.estoque_atual) if local == "frente" else float(prod.estoque_fundo)
                
                # Define se soma ou subtrai
                novo_saldo = saldo_ant + qtd_float if "ENTRADA" in tipo_mov.upper() else saldo_ant - qtd_float
                
                if local == "frente": 
                    prod.estoque_atual = novo_saldo
                else: 
                    prod.estoque_fundo = novo_saldo
                prod.save()

                Movimentacao.objects.create(
                    data=dt.now(), 
                    cod_produto=prod, 
                    nome_produto=prod.nome, 
                    qtd=qtd_float,
                    tipo=f"{tipo_mov}_{local.upper()}", 
                    motivo=motivo, 
                    usuario=usuario,
                    saldo_anterior=saldo_ant, 
                    saldo_novo=novo_saldo
                )
            return True, "OK"
        except Exception as e: 
            return False, f"Erro mov: {e}"

    def transferir_fundo_para_frente(self, pid, qtd, user="admin", mot=None):
        try:
            prod = Produto.objects.get(id=pid)
            qtd_float = float(str(qtd).replace(',', '.'))
            if float(prod.estoque_fundo) < qtd_float: 
                return False, "Saldo Fundo Insuficiente"
            
            # Movimentação atômica
            self.movimentar_estoque(pid, qtd, "SAIDA_TRANSFERENCIA", mot, user, "fundo")
            self.movimentar_estoque(pid, qtd, "ENTRADA_TRANSFERENCIA", mot, user, "frente")
            return True, "OK"
        except Exception as e: 
            return False, str(e)

    def registrar_producao(self, id_final, qtd, usuario):
        try:
            if not Receita.objects.filter(id_produto_id=id_final).exists():
                self.movimentar_estoque(id_final, qtd, TIPO_ENTRADA_PRODUCAO, "Produção Avulsa", usuario, "fundo")
                return True, "Produção sem baixa (Sem receita)"
            
            receita = Receita.objects.get(id_produto_id=id_final)
            fator = float(qtd) / float(receita.rendimento)
            
            if receita.ingredientes:
                for ing in receita.ingredientes:
                    qtd_baixa = float(ing['qtd']) * fator
                    self.movimentar_estoque(str(ing['id']), qtd_baixa, TIPO_SAIDA_PRODUCAO, f"Prod {qtd} {receita.nome}", usuario, "fundo")
            
            self.movimentar_estoque(id_final, qtd, TIPO_ENTRADA_PRODUCAO, "Produção Concluída", usuario, "fundo")
            return True, "Produção OK"
        except Exception as e: 
            return False, f"Erro Prod: {e}"