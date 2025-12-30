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
    """
    Controlador responsável pela lógica de negócio do estoque.
    """

    def __init__(self):
        self.db = database
        self.ARQ_RECEITAS = os.path.join(self.db.DATA_DIR, "receitas.json")

    def carregar_receitas(self):
        return self.db.carregar_json(self.ARQ_RECEITAS)

    def salvar_receita(self, id_produto, rendimento, ingredientes):
        id_produto = str(id_produto)
        receitas = self.carregar_receitas()
        produtos = self.db.carregar_produtos()
        
        if id_produto not in produtos:
            return False, f"Produto ID {id_produto} não encontrado no cadastro."

        receitas[id_produto] = {
            "id_produto": id_produto,
            "nome": produtos[id_produto]['nome'],
            "rendimento": float(rendimento),
            "ingredientes": ingredientes 
        }
        self.db.salvar_json(self.ARQ_RECEITAS, receitas)

        # Recalcula Custo
        custo_total_receita = 0.0
        for ing in ingredientes:
            insumo_id = str(ing['id'])
            insumo = produtos.get(insumo_id)
            if insumo:
                custo_ingrediente = float(insumo.get('custo', 0.0))
                qtd_usada = float(ing['qtd'])
                custo_total_receita += (custo_ingrediente * qtd_usada)
        
        rendimento_float = float(rendimento)
        if rendimento_float > 0:
            custo_unitario = custo_total_receita / rendimento_float
        else:
            custo_unitario = 0.0

        produtos[id_produto]['custo'] = round(custo_unitario, 4)
        self.db.salvar_produtos(produtos)

        return True, f"Receita salva! Custo atualizado para R$ {custo_unitario:.2f}/un"

    def salvar_produto(self, dados_produto):
        """
        Cadastra ou atualiza com validação de duplicidade (Nome e EAN).
        """
        produtos = self.db.carregar_produtos()
        novo_id = str(dados_produto['id'])
        novo_nome = dados_produto['nome'].strip().upper()
        
        # --- CORREÇÃO: Captura e trata o Grupo ---
        novo_grupo = str(dados_produto.get('grupo', '')).strip().upper()
        # -----------------------------------------

        novos_eans = dados_produto.get('codigos_barras', []) 
        if isinstance(novos_eans, str): novos_eans = []

        # --- VALIDAÇÃO DE DUPLICIDADE ---
        for pid, prod in produtos.items():
            if pid == novo_id: continue

            nome_existente = prod['nome'].strip().upper()
            if nome_existente == novo_nome:
                return False, f"O nome '{novo_nome}' já está em uso pelo item {pid}."

            eans_existentes = prod.get('codigos_barras', [])
            conflitos = set(novos_eans).intersection(set(eans_existentes))
            
            if conflitos:
                cod_conflitante = list(conflitos)[0]
                return False, f"O código de barras '{cod_conflitante}' já pertence ao item:\n{pid} - {prod['nome']}"
        # --------------------------------

        # Recupera dados existentes para preservar
        item_atual = produtos.get(novo_id, {})
        estoque_frente = item_atual.get('estoque_atual', 0.0)
        estoque_fundo = item_atual.get('estoque_fundo', 0.0)
        
        data_cadastro = item_atual.get('data_cadastro', dt.now().strftime("%d/%m/%Y"))

        novo_produto = {
            "id": novo_id,
            "nome": novo_nome,
            "grupo": novo_grupo,  # <--- CAMPO ADICIONADO AQUI
            "codigos_barras": novos_eans,
            "unidade": dados_produto.get('unidade', 'UN'), 
            "categoria": dados_produto.get('categoria', 'Outros'),
            "tipo": dados_produto.get('tipo', 'PRODUTO'),
            "controla_estoque": dados_produto.get('controla_estoque', True),
            "estoque_atual": estoque_frente, 
            "estoque_fundo": estoque_fundo,
            "estoque_minimo": float(str(dados_produto.get('minimo', 0)).replace(',', '.')),
            "preco": float(str(dados_produto.get('preco', 0)).replace(',', '.')),
            "custo": float(str(dados_produto.get('custo', 0)).replace(',', '.')),
            "data_cadastro": data_cadastro, 
            "ativo": True
        }
        produtos[novo_id] = novo_produto
        self.db.salvar_produtos(produtos)
        
        return True, "Produto salvo com sucesso!"

    def transferir_fundo_para_frente(self, produto_id, qtd, usuario="admin", motivo=None):
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
        id_produto_final = str(id_produto_final)
        try:
            receitas = self.carregar_receitas()
            
            if id_produto_final not in receitas:
                self.movimentar_estoque(
                    id_produto_final, qtd_produzida, TIPO_ENTRADA_PRODUCAO, 
                    "Produção S/ Receita", usuario, "fundo"
                )
                return True, "Produção registrada (Sem baixa de insumos - Receita não encontrada)"
                
            receita = receitas[id_produto_final]
            rendimento_base = float(receita.get('rendimento', 1))
            
            fator_multiplicador = float(qtd_produzida) / rendimento_base
            
            for ing in receita['ingredientes']:
                qtd_necessaria = float(ing['qtd']) * fator_multiplicador
                self.movimentar_estoque(
                    str(ing['id']), qtd_necessaria, TIPO_SAIDA_PRODUCAO, 
                    f"Prod. {qtd_produzida} {receita['nome']}", usuario, "fundo"
                )
            
            self.movimentar_estoque(
                id_produto_final, qtd_produzida, TIPO_ENTRADA_PRODUCAO, 
                "Produção Concluída", usuario, "fundo"
            )
            
            return True, f"Produção de {qtd_produzida} {receita['nome']} finalizada com sucesso!"
            
        except Exception as e:
            return False, f"Erro crítico na produção: {str(e)}"