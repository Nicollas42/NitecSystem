# simulacao_padaria_extrema.py
import sys
import os
import random
import time
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.controllers.estoque_controller import EstoqueController
from src.models import database

# --- CONFIGURAÇÃO ---
QTD_VENDAS = 300  
controller = EstoqueController()
produtos_criados = [] 

def header(texto):
    print(f"\n{'='*80}\n{texto}\n{'='*80}")

def log(texto):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {texto}")

# ==============================================================================
# 0. RESET TOTAL
# ==============================================================================
header("0. RESETANDO SISTEMA (CLEAN SLATE)")
arquivos = ["produtos.json", "movimentos.json", "vendas.json", "receitas.json", "sobras.json"]
for arq in arquivos:
    caminho = os.path.join(database.DATA_DIR, arq)
    if os.path.exists(caminho):
        os.remove(caminho)
        with open(caminho, 'w') as f: 
            f.write('{}' if arq in ['receitas.json', 'produtos.json'] else '[]')
log("🗑️  Todos os dados foram apagados. Sistema zerado.")

# ==============================================================================
# 1. CADASTRO (INSUMOS E PRODUTOS COM GRUPOS)
# ==============================================================================
header("1. CADASTRO DE ITENS")

# Insumos (Matéria Prima)
insumos = [
    ("100", "FARINHA DE TRIGO", "KG", 3.50),
    ("101", "AÇÚCAR", "KG", 2.80),
    ("102", "OVOS", "UN", 0.50),
    ("103", "LEITE", "L", 4.00),
    ("104", "FERMENTO", "G", 0.05),
    ("105", "CHOCOLATE", "KG", 40.00),
    ("106", "RECHEIO FRANGO", "KG", 18.00),
    ("107", "PRESUNTO", "KG", 25.00),
    ("108", "QUEIJO", "KG", 30.00),
]

for i in insumos:
    controller.salvar_produto({
        "id": i[0], "nome": i[1], "unidade": i[2], "categoria": "Insumos",
        "custo": str(i[3]), "preco": "0.00", "minimo": "50",
        "tipo": "INSUMO", "controla_estoque": True, "grupo": ""
    })
    # Compra Inicial (Enche o Fundo)
    controller.movimentar_estoque(i[0], 5000, "ENTRADA_COMPRA", "Estoque Inicial", "Admin", "fundo")

# Produtos de Venda (Agrupados)
grupos = [
    ("PÃO FRANCÊS", [("201", "Pão Francês Tradicional", 16.90, "KG"), ("202", "Pão Francês Integral", 18.90, "KG")]),
    ("BOLO CASEIRO", [("301", "Bolo de Chocolate", 25.00, "UN"), ("302", "Bolo de Cenoura", 25.00, "UN")]),
    ("SALGADOS", [("401", "Coxinha Frango", 6.50, "UN"), ("402", "Risole Presunto", 6.50, "UN"), ("403", "Kibe", 6.50, "UN")]),
    ("REFRIGERANTE 2L", [("501", "Coca-Cola Original", 14.00, "UN"), ("502", "Guaraná Antarctica", 12.00, "UN"), ("503", "Fanta Laranja", 12.00, "UN"), ("504", "Sprite", 12.00, "UN")])
]

# Produtos Soltos
soltos = [
    ("601", "Café Expresso", 5.00, "UN", "Bebidas"),
    ("602", "Pão de Queijo", 39.90, "KG", "Panificação")
]

# Cadastro Grupos
for grp, itens in grupos:
    for pid, nome, preco, un in itens:
        controller.salvar_produto({
            "id": pid, "nome": nome, "grupo": grp, "unidade": un, "categoria": "Venda",
            "preco": str(preco), "minimo": "10", "custo": "0.00", 
            "tipo": "PRODUTO", "controla_estoque": True, "codigos_barras": [f"789{pid}"]
        })
        produtos_criados.append(pid)
        # Se for refri (Revenda), compra pro fundo
        if "REFRIGERANTE" in grp:
            controller.movimentar_estoque(pid, 1000, "ENTRADA_COMPRA", "Ambev", "Estoquista", "fundo")

# Cadastro Soltos
for pid, nome, preco, un, cat in soltos:
    controller.salvar_produto({
        "id": pid, "nome": nome, "grupo": "", "unidade": un, "categoria": cat,
        "preco": str(preco), "minimo": "10", "custo": "0.00", 
        "tipo": "PRODUTO", "controla_estoque": True, "codigos_barras": [f"789{pid}"]
    })
    produtos_criados.append(pid)
    # Pão de queijo produziremos, Café é serviço (mas vamos simular estoque pra não bugar)
    if "Café" in nome:
        controller.movimentar_estoque(pid, 5000, "ENTRADA_COMPRA", "Insumo Café", "Admin", "fundo")


log("✅ Itens cadastrados e insumos comprados.")

# ==============================================================================
# 2. PRODUÇÃO (FUNDO)
# ==============================================================================
header("2. FÁBRICA: PRODUÇÃO PARA ESTOQUE")

# Receitas Fictícias para gerar custo
controller.salvar_receita("201", "50", [{"id": "100", "qtd": 30}, {"id": "104", "qtd": 0.5}])
controller.salvar_receita("301", "10", [{"id": "100", "qtd": 5}, {"id": "105", "qtd": 2}, {"id": "102", "qtd": 10}])
controller.salvar_receita("401", "100", [{"id": "100", "qtd": 5}, {"id": "106", "qtd": 3}])

log("🏭 Produzindo estoque massivo para o depósito (Fundo)...")
for pid in produtos_criados:
    if pid.startswith("5") or pid == "601": continue # Pula Refri e Café
    
    # Produz quantidade suficiente para não negativar fácil
    controller.registrar_producao(pid, 500, "Padeiro Chefe") 

log("✅ Produção concluída.")

# ==============================================================================
# 3. ABASTECIMENTO INICIAL (FUNDO -> FRENTE)
# ==============================================================================
header("3. ABASTECIMENTO DA VITRINE")

for pid in produtos_criados:
    # Coloca 50 na frente pra começar
    controller.transferir_fundo_para_frente(pid, 50, "Repositor", "Abertura Loja")

log("✅ Vitrine abastecida.")

# ==============================================================================
# 4. SIMULAÇÃO DE VENDAS COM PROTEÇÃO DE ESTOQUE
# ==============================================================================
header(f"4. INICIANDO {QTD_VENDAS} VENDAS COM PROTEÇÃO DE ESTOQUE")

operadores = ["Ana Caixa", "Bruno Caixa"]
pagamentos = ["Pix", "Crédito", "Débito", "Dinheiro"]
total_faturado = 0
vendas_rejeitadas = 0

for i in range(1, QTD_VENDAS + 1):
    qtd_itens = random.randint(1, 4)
    carrinho_ids = random.sample(produtos_criados, k=qtd_itens)
    
    lista_venda_db = []
    total_cupom = 0
    
    # RECARREGA DB PARA TER DADOS ATUAIS
    produtos_db = database.carregar_produtos()
    
    for pid in carrinho_ids:
        prod = produtos_db[pid]
        
        # Define quanto o cliente QUER comprar
        demanda = random.randint(1, 3) if prod['unidade'] == "UN" else round(random.uniform(0.2, 1.0), 3)
        
        est_frente = prod.get('estoque_atual', 0)
        est_fundo = prod.get('estoque_fundo', 0)
        
        qtd_final = 0
        
        # 1. Tem na frente?
        if est_frente >= demanda:
            qtd_final = demanda
            
        # 2. Não tem na frente, mas tem no fundo? (Transfere e Vende)
        elif (est_frente + est_fundo) >= demanda:
            falta_na_frente = demanda - est_frente
            # Transfere o necessário + um pouco de margem (ex: 10 un)
            qtd_transferir = falta_na_frente + 10
            
            # Garante que não transfere mais do que tem no fundo
            if qtd_transferir > est_fundo:
                qtd_transferir = est_fundo
            
            controller.transferir_fundo_para_frente(pid, qtd_transferir, "Auto-Caixa", "Reposição Automática")
            print(f"   🔄 [Reposição] {prod['nome']}: Trouxe {qtd_transferir:.2f} do Fundo.")
            
            # Agora atualiza a variável local pra simular a venda
            est_frente += qtd_transferir 
            est_fundo -= qtd_transferir
            
            # Verifica novamente se agora atende
            if est_frente >= demanda:
                qtd_final = demanda
            else:
                qtd_final = est_frente # Vende só o que conseguiu trazer
                
        # 3. Não tem em lugar nenhum (Vende só o saldo ou perde a venda)
        else:
            qtd_final = est_frente # Zera o estoque da frente
            if qtd_final <= 0:
                # print(f"   ❌ [Sem Estoque] Cliente queria {demanda} de {prod['nome']}, mas não tem nada.")
                qtd_final = 0
        
        # Concretiza o item no carrinho se houver quantidade > 0
        if qtd_final > 0:
            total_item = qtd_final * prod['preco']
            total_cupom += total_item
            lista_venda_db.append({
                "produto": prod['nome'], "qtd": qtd_final, "total": total_item
            })

    # Finaliza a venda se houver itens
    if lista_venda_db:
        op = random.choice(operadores)
        pag = random.choice(pagamentos)
        database.registrar_venda(total_cupom, lista_venda_db, op, pag)
        total_faturado += total_cupom
        
        if i % 50 == 0:
            log(f"Venda #{i} realizada. Total: R$ {total_cupom:.2f}")
    else:
        vendas_rejeitadas += 1

# ==============================================================================
# 5. FINALIZAÇÃO
# ==============================================================================
header("🏁 SIMULAÇÃO CONCLUÍDA")
print(f"💰 Faturamento: R$ {total_faturado:,.2f}")
print(f"🚫 Vendas perdidas por falta de estoque: {vendas_rejeitadas}")
print("Verifique a Visão Geral. Não deve haver números negativos significativos.")