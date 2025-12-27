# src/controllers/estoque_controller.py
import datetime
from src.models import database

TIPO_ENTRADA_COMPRA = "ENTRADA_COMPRA" 
TIPO_SAIDA_VENDA = "SAIDA_VENDA"
TIPO_SAIDA_PRODUCAO = "SAIDA_PRODUCAO" 
TIPO_ENTRADA_PRODUCAO = "ENTRADA_PRODUCAO" 
TIPO_AJUSTE_PERDA = "SAIDA_PERDA"
TIPO_AJUSTE_SOBRA = "ENTRADA_AJUSTE"

class EstoqueController:
    def __init__(self):
        self.db = database

    def salvar_produto(self, dados_produto):
        produtos = self.db.carregar_produtos()
        cod = dados_produto['id']

        # Preserva os dois saldos se o produto já existir
        estoque_frente = produtos[cod].get('estoque_atual', 0.0) if cod in produtos else 0.0
        estoque_fundo = produtos[cod].get('estoque_fundo', 0.0) if cod in produtos else 0.0

        novo_produto = {
            "id": cod,
            "nome": dados_produto['nome'].strip().upper(),
            "unidade": dados_produto.get('unidade', 'UN'), 
            "controla_estoque": dados_produto.get('controla_estoque', True),
            "estoque_atual": estoque_frente, # FRENTE DA LOJA
            "estoque_fundo": estoque_fundo,   # DEPOSITO / FUNDO
            "estoque_minimo": float(str(dados_produto.get('minimo', 0)).replace(',', '.')),
            "preco": float(str(dados_produto.get('preco', 0)).replace(',', '.')),
            "ativo": True
        }
        produtos[cod] = novo_produto
        self.db.salvar_produtos(produtos)
        return True

    def transferir_para_frente(self, produto_id, qtd, usuario):
        """Move produtos do FUNDO para a FRENTE (Exposição)"""
        produtos = self.db.carregar_produtos()
        if produto_id not in produtos: return False, "Produto inexistente"
        
        prod = produtos[produto_id]
        qtd_num = float(qtd)
        
        if prod['estoque_fundo'] < qtd_num:
            return False, f"Saldo insuficiente no FUNDO ({prod['estoque_fundo']})"

        # Lógica de transferência
        prod['estoque_fundo'] -= qtd_num
        prod['estoque_atual'] += qtd_num
        
        self.db.salvar_produtos(produtos)
        self.db.registrar_movimentacao("TRANSFERENCIA", produto_id, prod['nome'], qtd_num, 
                                      "Fundo -> Frente", usuario, prod['estoque_fundo']+qtd_num, prod['estoque_fundo'])
        return True, "Transferência concluída!"


    def transferir_fundo_para_frente(self, produto_id, qtd, usuario="admin", motivo=None):
        """Move o saldo do estoque interno para a exposição com motivo personalizado"""
        produtos = self.db.carregar_produtos()
        
        if produto_id not in produtos:
            return False, "Produto não encontrado."
            
        prod = produtos[produto_id]
        try:
            qtd_num = float(str(qtd).replace(',', '.'))
        except:
            return False, "Quantidade inválida."

        saldo_fundo = prod.get('estoque_fundo', 0.0)
        saldo_frente = prod.get('estoque_atual', 0.0)

        if saldo_fundo < qtd_num:
            return False, f"Saldo insuficiente no FUNDO ({saldo_fundo})."

        # Executa a transferência
        prod['estoque_fundo'] = round(saldo_fundo - qtd_num, 4)
        prod['estoque_atual'] = round(saldo_frente + qtd_num, 4)
        
        self.db.salvar_produtos(produtos)
        
        # Define o motivo automático se não for passado
        motivo_final = motivo if motivo else "Fundo -> Frente"

        # Registra com destaque para auditoria
        self.db.registrar_movimentacao(
            "TRANSFERENCIA", produto_id, prod['nome'], qtd_num, 
            motivo_final, usuario, saldo_frente, prod['estoque_atual']
        )
        
        return True, f"Transferência de {qtd_num} realizada!"
    
    
    
    def movimentar_estoque(self, produto_id, qtd, tipo_mov, motivo="", usuario="Admin", local="fundo"):
        """
        Realiza movimentações de estoque (ENTRADA, SAIDA, PERDA)
        'local' pode ser 'frente' (estoque_atual) ou 'fundo' (estoque_fundo)
        """
        produtos = self.db.carregar_produtos()
        if produto_id not in produtos:
            return False, "Produto não encontrado."
            
        prod = produtos[produto_id]
        chave_estoque = 'estoque_atual' if local == "frente" else 'estoque_fundo'
        
        try:
            qtd_num = float(str(qtd).replace(',', '.'))
        except:
            return False, "Quantidade inválida."

        saldo_anterior = prod.get(chave_estoque, 0.0)
        
        # Define se soma ou subtrai baseado no tipo
        if tipo_mov == "ENTRADA":
            novo_saldo = saldo_anterior + qtd_num
        else: # SAIDA ou PERDA
            novo_saldo = saldo_anterior - qtd_num

        # Atualiza o saldo no dicionário
        prod[chave_estoque] = round(novo_saldo, 4)
        
        self.db.salvar_produtos(produtos)
        
        # Log detalhado para o Livro Razão
        self.db.registrar_movimentacao(
            f"{tipo_mov}_{local.upper()}", produto_id, prod['nome'], qtd_num, 
            motivo, usuario, saldo_anterior, novo_saldo
        )
        
        return True, f"{tipo_mov} realizada no {local.upper()}. Novo saldo: {novo_saldo}"
    
    def registrar_producao(self, id_produto_final, qtd_produzida, usuario):
        """
        Funcionalidade de Produção Própria com baixa automática de insumos.
        """
        # Esta função exige que você tenha o método carregar_fichas_tecnicas no seu database.py
        try:
            fichas = self.db.carregar_json(self.db.ARQ_SOBRAS) # Exemplo: Ajustar para caminho de fichas se existir
            if id_produto_final not in fichas:
                raise ValueError("Produto sem Ficha Técnica.")
                
            receita = fichas[id_produto_final]
            fator = qtd_produzida / receita['rendimento']
            
            for ing in receita['ingredientes']:
                qtd_nec = ing['qtd'] * fator
                self.realizar_movimentacao(ing['id'], qtd_nec, TIPO_SAIDA_PRODUCAO, motivo=f"Prod. {id_produto_final}", usuario=usuario)
                
            self.realizar_movimentacao(id_produto_final, qtd_produzida, TIPO_ENTRADA_PRODUCAO, motivo="Produção Concluída", usuario=usuario)
            return True
        except Exception as e:
            print(f"Erro na produção: {e}")
            return False