# src/controllers/estoque_controller.py
import datetime
import os # Importante para manipular caminhos
from src.models import database

# Constantes
TIPO_ENTRADA_COMPRA = "ENTRADA_COMPRA" 
TIPO_SAIDA_VENDA = "SAIDA_VENDA"
TIPO_SAIDA_PRODUCAO = "SAIDA_PRODUCAO" 
TIPO_ENTRADA_PRODUCAO = "ENTRADA_PRODUCAO" 
TIPO_AJUSTE_PERDA = "SAIDA_PERDA"
TIPO_AJUSTE_SOBRA = "ENTRADA_AJUSTE"

class EstoqueController:
    def __init__(self):
        self.db = database
        # Caminho manual para receitas (para não precisar editar o database.py agora)
        self.ARQ_RECEITAS = os.path.join(self.db.DATA_DIR, "receitas.json")

    def carregar_receitas(self):
        return self.db.carregar_json(self.ARQ_RECEITAS)

    def salvar_receita(self, id_produto, rendimento, ingredientes):
        """
        Salva a ficha técnica e ATUALIZA O CUSTO do produto final
        """
        receitas = self.carregar_receitas()
        produtos = self.db.carregar_produtos()
        
        # 1. Salva a Receita
        receitas[id_produto] = {
            "id_produto": id_produto,
            "nome": produtos[id_produto]['nome'],
            "rendimento": float(rendimento),
            "ingredientes": ingredientes # Lista de {id, nome, qtd}
        }
        self.db.salvar_json(self.ARQ_RECEITAS, receitas)

        # 2. Calcula o Custo Unitário
        custo_total_receita = 0.0
        for ing in ingredientes:
            # Busca o custo atual do insumo no cadastro de produtos
            insumo = produtos.get(ing['id'])
            if insumo:
                custo_ingrediente = insumo.get('custo', 0.0)
                custo_total_receita += (custo_ingrediente * float(ing['qtd']))
        
        custo_unitario = custo_total_receita / float(rendimento)

        # 3. Atualiza o Custo no Cadastro do Produto Final
        if id_produto in produtos:
            produtos[id_produto]['custo'] = round(custo_unitario, 4)
            self.db.salvar_produtos(produtos)

        return True, f"Receita salva! Custo atualizado para R$ {custo_unitario:.2f}/un"

    # ... (Mantenha os métodos salvar_produto, transferir, movimentar aqui iguais ao anterior) ...

    def salvar_produto(self, dados_produto):
        # ... (código existente do passo anterior) ...
        # (Para economizar espaço, mantenha a versão que você já atualizou no passo anterior)
        # Apenas certifique-se de que o método 'movimentar_estoque' tenha a correção do 'if "ENTRADA" in'
        return self.db_salvar_produto_implementacao_anterior(dados_produto) 

    # Implementação auxiliar para manter compatibilidade se você copiar/colar tudo
    def db_salvar_produto_implementacao_anterior(self, dados_produto):
        produtos = self.db.carregar_produtos()
        cod = dados_produto['id']
        estoque_frente = produtos[cod].get('estoque_atual', 0.0) if cod in produtos else 0.0
        estoque_fundo = produtos[cod].get('estoque_fundo', 0.0) if cod in produtos else 0.0
        novo_produto = {
            "id": cod, "nome": dados_produto['nome'].strip().upper(),
            "unidade": dados_produto.get('unidade', 'UN'), 
            "categoria": dados_produto.get('categoria', 'Outros'),
            "tipo": dados_produto.get('tipo', 'PRODUTO'),
            "controla_estoque": dados_produto.get('controla_estoque', True),
            "estoque_atual": estoque_frente, "estoque_fundo": estoque_fundo,
            "estoque_minimo": float(str(dados_produto.get('minimo', 0)).replace(',', '.')),
            "preco": float(str(dados_produto.get('preco', 0)).replace(',', '.')),
            "custo": float(str(dados_produto.get('custo', 0)).replace(',', '.')),
            "ativo": True
        }
        produtos[cod] = novo_produto
        self.db.salvar_produtos(produtos)
        return True

    def transferir_fundo_para_frente(self, produto_id, qtd, usuario="admin", motivo=None):
        # ... (Mesmo código anterior) ...
        produtos = self.db.carregar_produtos()
        if produto_id not in produtos: return False, "Erro"
        prod = produtos[produto_id]
        qtd = float(str(qtd).replace(',', '.'))
        if prod['estoque_fundo'] < qtd: return False, "Saldo insuficiente"
        prod['estoque_fundo'] -= qtd; prod['estoque_atual'] += qtd
        self.db.salvar_produtos(produtos)
        motivo = motivo if motivo else "Fundo -> Frente"
        self.db.registrar_movimentacao("TRANSFERENCIA", produto_id, prod['nome'], qtd, motivo, usuario, 0, 0)
        return True, "Sucesso"

    def movimentar_estoque(self, produto_id, qtd, tipo_mov, motivo="", usuario="Admin", local="fundo"):
        # ... (Mesmo código CORRIGIDO do passo anterior) ...
        produtos = self.db.carregar_produtos()
        prod = produtos.get(produto_id)
        if not prod: return False, "Erro"
        chave = 'estoque_atual' if local == "frente" else 'estoque_fundo'
        qtd = float(str(qtd).replace(',', '.'))
        ant = prod.get(chave, 0.0)
        
        if "ENTRADA" in tipo_mov.upper(): # A CORREÇÃO CRÍTICA ESTÁ AQUI
            novo = ant + qtd
        else:
            novo = ant - qtd
            
        prod[chave] = round(novo, 4)
        self.db.salvar_produtos(produtos)
        self.db.registrar_movimentacao(f"{tipo_mov}_{local.upper()}", produto_id, prod['nome'], qtd, motivo, usuario, ant, novo)
        return True, "Sucesso"

    def registrar_producao(self, id_produto_final, qtd_produzida, usuario):
        try:
            receitas = self.carregar_receitas()
            
            if id_produto_final not in receitas:
                # Produção sem receita (apenas entrada manual)
                self.movimentar_estoque(id_produto_final, qtd_produzida, TIPO_ENTRADA_PRODUCAO, "Produção S/ Receita", usuario, "fundo")
                return True, "Produção registrada (Sem baixa de insumos - Receita não encontrada)"
                
            receita = receitas[id_produto_final]
            rendimento_base = float(receita.get('rendimento', 1))
            fator_multiplicador = float(qtd_produzida) / rendimento_base
            
            # 1. Baixa os Insumos (Do Fundo)
            for ing in receita['ingredientes']:
                qtd_necessaria = float(ing['qtd']) * fator_multiplicador
                # Importante: SAIDA_PRODUCAO vai subtrair do estoque
                self.movimentar_estoque(ing['id'], qtd_necessaria, TIPO_SAIDA_PRODUCAO, f"Prod. {qtd_produzida} {receita['nome']}", usuario, "fundo")
            
            # 2. Entrada do Produto Final (No Fundo)
            # Importante: ENTRADA_PRODUCAO vai somar no estoque
            self.movimentar_estoque(id_produto_final, qtd_produzida, TIPO_ENTRADA_PRODUCAO, "Produção Concluída", usuario, "fundo")
            
            return True, f"Produção de {qtd_produzida} {receita['nome']} finalizada!"
        except Exception as e:
            return False, f"Erro na produção: {str(e)}"