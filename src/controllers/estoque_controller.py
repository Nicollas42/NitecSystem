# src/controllers/estoque_controller.py
import datetime
import os 
from src.models import database

# Constantes de Movimentação
TIPO_ENTRADA_COMPRA = "ENTRADA_COMPRA" 
TIPO_SAIDA_VENDA = "SAIDA_VENDA"
TIPO_SAIDA_PRODUCAO = "SAIDA_PRODUCAO" 
TIPO_ENTRADA_PRODUCAO = "ENTRADA_PRODUCAO" 
TIPO_AJUSTE_PERDA = "SAIDA_PERDA"
TIPO_AJUSTE_SOBRA = "ENTRADA_AJUSTE"

class EstoqueController:
    """
    Controlador responsável pela lógica de negócio do estoque, incluindo
    movimentações, transferências, gestão de receitas e registro de produção.
    """

    def __init__(self):
        """
        Inicializa o controlador carregando as referências do banco de dados.
        """
        self.db = database
        self.ARQ_RECEITAS = os.path.join(self.db.DATA_DIR, "receitas.json")

    def carregar_receitas(self):
        """
        Carrega o arquivo JSON contendo todas as fichas técnicas.

        :return: Dicionário com as receitas cadastradas.
        """
        return self.db.carregar_json(self.ARQ_RECEITAS)

    def salvar_receita(self, id_produto, rendimento, ingredientes):
        """
        Salva ou atualiza uma ficha técnica e recalcula automaticamente o 
        Preço de Custo do produto final com base nos ingredientes.

        :param id_produto: ID do produto final (ex: Pão Francês).
        :param rendimento: Quantidade que a receita rende (base de cálculo).
        :param ingredientes: Lista de dicionários com 'id' e 'qtd' dos insumos.
        :return: Tupla (bool, str) indicando sucesso ou mensagem de erro.
        """
        id_produto = str(id_produto)
        
        receitas = self.carregar_receitas()
        produtos = self.db.carregar_produtos()
        
        if id_produto not in produtos:
            return False, f"Produto ID {id_produto} não encontrado no cadastro."

        # 1. Estrutura e Salva a Receita
        receitas[id_produto] = {
            "id_produto": id_produto,
            "nome": produtos[id_produto]['nome'],
            "rendimento": float(rendimento),
            "ingredientes": ingredientes 
        }
        self.db.salvar_json(self.ARQ_RECEITAS, receitas)

        # 2. Calcula o Custo Unitário (Baseado no custo atual dos insumos)
        custo_total_receita = 0.0
        for ing in ingredientes:
            insumo_id = str(ing['id'])
            insumo = produtos.get(insumo_id)
            if insumo:
                custo_ingrediente = float(insumo.get('custo', 0.0))
                qtd_usada = float(ing['qtd'])
                custo_total_receita += (custo_ingrediente * qtd_usada)
        
        # Evita divisão por zero
        rendimento_float = float(rendimento)
        if rendimento_float > 0:
            custo_unitario = custo_total_receita / rendimento_float
        else:
            custo_unitario = 0.0

        # 3. Atualiza o Custo no Cadastro do Produto Final
        produtos[id_produto]['custo'] = round(custo_unitario, 4)
        self.db.salvar_produtos(produtos)

        return True, f"Receita salva! Custo atualizado para R$ {custo_unitario:.2f}/un"

    def salvar_produto(self, dados_produto):
        """
        Cadastra ou atualiza um produto/insumo no banco de dados.

        :param dados_produto: Dicionário contendo os campos do formulário.
        :return: True (Sempre assume sucesso na validação simples).
        """
        produtos = self.db.carregar_produtos()
        cod = str(dados_produto['id'])

        # Mantém estoques existentes se for edição
        estoque_frente = produtos[cod].get('estoque_atual', 0.0) if cod in produtos else 0.0
        estoque_fundo = produtos[cod].get('estoque_fundo', 0.0) if cod in produtos else 0.0

        novo_produto = {
            "id": cod,
            "nome": dados_produto['nome'].strip().upper(),
            "unidade": dados_produto.get('unidade', 'UN'), 
            "categoria": dados_produto.get('categoria', 'Outros'),
            "tipo": dados_produto.get('tipo', 'PRODUTO'), # INSUMO ou PRODUTO
            "controla_estoque": dados_produto.get('controla_estoque', True),
            "estoque_atual": estoque_frente, 
            "estoque_fundo": estoque_fundo,
            "estoque_minimo": float(str(dados_produto.get('minimo', 0)).replace(',', '.')),
            "preco": float(str(dados_produto.get('preco', 0)).replace(',', '.')),
            "custo": float(str(dados_produto.get('custo', 0)).replace(',', '.')),
            "ativo": True
        }
        produtos[cod] = novo_produto
        self.db.salvar_produtos(produtos)
        return True

    def transferir_fundo_para_frente(self, produto_id, qtd, usuario="admin", motivo=None):
        """
        Transfere mercadoria do Depósito (Fundo) para a Loja (Frente).

        :param produto_id: ID do produto.
        :param qtd: Quantidade a ser transferida.
        :param usuario: Nome do usuário realizando a ação.
        :param motivo: Texto opcional explicando a ação.
        :return: Tupla (bool, str).
        """
        produtos = self.db.carregar_produtos()
        produto_id = str(produto_id)
        
        if produto_id not in produtos:
            return False, "Produto não encontrado."
            
        prod = produtos[produto_id]
        try:
            qtd_num = float(str(qtd).replace(',', '.'))
        except ValueError:
            return False, "Quantidade inválida."

        saldo_fundo = prod.get('estoque_fundo', 0.0)
        saldo_frente = prod.get('estoque_atual', 0.0)

        if saldo_fundo < qtd_num:
            return False, f"Saldo insuficiente no FUNDO ({saldo_fundo})."

        prod['estoque_fundo'] = round(saldo_fundo - qtd_num, 4)
        prod['estoque_atual'] = round(saldo_frente + qtd_num, 4)
        
        self.db.salvar_produtos(produtos)
        
        motivo_final = motivo if motivo else "Fundo -> Frente"

        self.db.registrar_movimentacao(
            "TRANSFERENCIA", produto_id, prod['nome'], qtd_num, 
            motivo_final, usuario, saldo_frente, prod['estoque_atual']
        )
        
        return True, f"Transferência de {qtd_num} realizada!"
    
    def movimentar_estoque(self, produto_id, qtd, tipo_mov, motivo="", usuario="Admin", local="fundo"):
        """
        Realiza uma movimentação genérica de entrada ou saída manual.

        :param produto_id: ID do item.
        :param qtd: Quantidade movimentada.
        :param tipo_mov: Constante de tipo (ENTRADA, SAIDA, PERDA).
        :param motivo: Descrição da movimentação.
        :param usuario: Usuário responsável.
        :param local: 'frente' ou 'fundo'.
        :return: Tupla (bool, str).
        """
        produtos = self.db.carregar_produtos()
        produto_id = str(produto_id)
        
        if produto_id not in produtos:
            return False, "Produto não encontrado."
            
        prod = produtos[produto_id]
        chave_estoque = 'estoque_atual' if local == "frente" else 'estoque_fundo'
        
        try:
            qtd_num = float(str(qtd).replace(',', '.'))
        except ValueError:
            return False, "Quantidade inválida."

        saldo_anterior = prod.get(chave_estoque, 0.0)
        
        # Verifica se é entrada ou saída baseado na string do tipo
        if "ENTRADA" in tipo_mov.upper():
            novo_saldo = saldo_anterior + qtd_num
        else:
            novo_saldo = saldo_anterior - qtd_num

        prod[chave_estoque] = round(novo_saldo, 4)
        self.db.salvar_produtos(produtos)
        
        self.db.registrar_movimentacao(
            f"{tipo_mov}_{local.upper()}", produto_id, prod['nome'], qtd_num, 
            motivo, usuario, saldo_anterior, novo_saldo
        )
        
        return True, f"{tipo_mov} realizada. Novo saldo: {novo_saldo:.2f}"
    
    def registrar_producao(self, id_produto_final, qtd_produzida, usuario):
        """
        Registra a produção de um item final e baixa automaticamente os insumos
        proporcionalmente à ficha técnica.

        :param id_produto_final: ID do produto que foi fabricado (ex: Pão).
        :param qtd_produzida: Quantidade fabricada (ex: 50 un).
        :param usuario: Usuário responsável.
        :return: Tupla (bool, str).
        """
        id_produto_final = str(id_produto_final)
        try:
            receitas = self.carregar_receitas()
            
            # Se não tem receita, faz apenas entrada simples
            if id_produto_final not in receitas:
                self.movimentar_estoque(
                    id_produto_final, qtd_produzida, TIPO_ENTRADA_PRODUCAO, 
                    "Produção S/ Receita", usuario, "fundo"
                )
                return True, "Produção registrada (Sem baixa de insumos - Receita não encontrada)"
                
            receita = receitas[id_produto_final]
            rendimento_base = float(receita.get('rendimento', 1))
            
            # FATOR PROPORCIONAL: Se a receita é pra 10 e fiz 5, o fator é 0.5
            fator_multiplicador = float(qtd_produzida) / rendimento_base
            
            # 1. Baixa os Insumos (Proporcionalmente)
            for ing in receita['ingredientes']:
                qtd_necessaria = float(ing['qtd']) * fator_multiplicador
                self.movimentar_estoque(
                    str(ing['id']), qtd_necessaria, TIPO_SAIDA_PRODUCAO, 
                    f"Prod. {qtd_produzida} {receita['nome']}", usuario, "fundo"
                )
            
            # 2. Dá entrada no Produto Final (Geralmente vai pro Fundo/Depósito primeiro)
            self.movimentar_estoque(
                id_produto_final, qtd_produzida, TIPO_ENTRADA_PRODUCAO, 
                "Produção Concluída", usuario, "fundo"
            )
            
            return True, f"Produção de {qtd_produzida} {receita['nome']} finalizada com sucesso!"
            
        except Exception as e:
            return False, f"Erro crítico na produção: {str(e)}"