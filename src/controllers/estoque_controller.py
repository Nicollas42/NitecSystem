# src/controllers/estoque_controller.py
import datetime
from src.models import database

# Tipos de Movimentação
TIPO_ENTRADA_COMPRA = "ENTRADA_COMPRA" # Nota Fiscal
TIPO_SAIDA_VENDA = "SAIDA_VENDA"
TIPO_SAIDA_PRODUCAO = "SAIDA_PRODUCAO" # Usado na receita
TIPO_ENTRADA_PRODUCAO = "ENTRADA_PRODUCAO" # Produto final pronto
TIPO_AJUSTE_PERDA = "SAIDA_PERDA"
TIPO_AJUSTE_SOBRA = "ENTRADA_AJUSTE"

class EstoqueController:
    
    def __init__(self):
        self.db = database # Referência ao módulo de banco de dados

    def cadastrar_produto(self, dados_produto):
        """
        Cria um produto com a estrutura completa profissional.
        """
        novo_produto = {
            "id": dados_produto['id'],
            "nome": dados_produto['nome'].strip().upper(),
            "categoria": dados_produto['categoria'],
            "tipo": dados_produto['tipo'], # 'VENDA', 'INSUMO', 'AMBOS'
            "unidade": dados_produto['unidade'], # 'KG', 'UN', 'L'
            "controla_estoque": dados_produto.get('controla_estoque', True),
            "estoque_atual": 0.0,
            "estoque_minimo": float(dados_produto.get('estoque_minimo', 0)),
            "custo_medio": 0.0, # Começa zerado
            "ativo": True
        }
        
        # Salva no banco
        produtos = self.db.carregar_produtos()
        if dados_produto['id'] in produtos:
            raise ValueError("ID já existe!")
        
        produtos[dados_produto['id']] = novo_produto
        self.db.salvar_produtos(produtos)
        return True

    def realizar_movimentacao(self, produto_id, qtd, tipo_mov, custo_unitario=None, motivo="", usuario="sistema"):
        """
        A REGRA DE OURO: Nada muda o estoque sem passar por aqui.
        Calcula custo médio ponderado na entrada.
        Registra log.
        """
        produtos = self.db.carregar_produtos()
        
        if produto_id not in produtos:
            raise ValueError("Produto não encontrado")
        
        prod = produtos[produto_id]
        estoque_atual = prod['estoque_atual']
        custo_atual = prod['custo_medio']
        
        # Lógica de Custo Médio (Apenas em entradas de compra)
        if tipo_mov == TIPO_ENTRADA_COMPRA and custo_unitario is not None:
            # Fórmula do Custo Médio Ponderado
            novo_total_valor = (estoque_atual * custo_atual) + (qtd * custo_unitario)
            nova_qtd_total = estoque_atual + qtd
            
            if nova_qtd_total > 0:
                novo_custo_medio = novo_total_valor / nova_qtd_total
            else:
                novo_custo_medio = custo_unitario
                
            prod['custo_medio'] = round(novo_custo_medio, 4)
            nova_qtd = nova_qtd_total
            
        else:
            # Movimentações normais (saídas ou ajustes)
            if "ENTRADA" in tipo_mov:
                nova_qtd = estoque_atual + qtd
            else:
                nova_qtd = estoque_atual - qtd
        
        # Atualiza o Produto
        prod['estoque_atual'] = round(nova_qtd, 4)
        self.db.salvar_produtos(produtos)
        
        # LOG DA MOVIMENTAÇÃO (RASTREABILIDADE)
        log = {
            "data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "produto_id": produto_id,
            "produto_nome": prod['nome'],
            "tipo": tipo_mov,
            "quantidade": qtd,
            "estoque_anterior": estoque_atual,
            "estoque_novo": nova_qtd,
            "custo_medio_momento": prod['custo_medio'],
            "motivo": motivo,
            "usuario": usuario
        }
        
        self.db.registrar_movimentacao(log)
        
        # Checagem de Alerta
        if prod['controla_estoque'] and nova_qtd <= prod['estoque_minimo']:
            return {"status": "sucesso", "alerta": True, "msg": f"⚠️ ALERTA: {prod['nome']} abaixo do mínimo!"}
            
        return {"status": "sucesso", "alerta": False}

    def registrar_producao(self, id_produto_final, qtd_produzida, usuario):
        """
        Produção Própria:
        1. Olha a ficha técnica.
        2. Remove os insumos do estoque.
        3. Adiciona o produto final.
        """
        fichas = self.db.carregar_fichas_tecnicas()
        
        if id_produto_final not in fichas:
            raise ValueError("Este produto não tem Ficha Técnica cadastrada.")
            
        receita = fichas[id_produto_final] # Ex: {"ingredientes": [{"id": "101", "qtd": 0.5}], "rendimento": 1}
        fator = qtd_produzida / receita['rendimento']
        
        # 1. Consumir Insumos
        for ingrediente in receita['ingredientes']:
            qtd_necessaria = ingrediente['qtd'] * fator
            
            # Chama a movimentação de SAÍDA para cada insumo
            self.realizar_movimentacao(
                ingrediente['id'], 
                qtd_necessaria, 
                TIPO_SAIDA_PRODUCAO, 
                motivo=f"Produção de {qtd_produzida} {receita['unidade']} de {id_produto_final}",
                usuario=usuario
            )
            
        # 2. Entrada do Produto Final
        self.realizar_movimentacao(
            id_produto_final, 
            qtd_produzida, 
            TIPO_ENTRADA_PRODUCAO,
            motivo="Produção Interna Concluída",
            usuario=usuario
        )