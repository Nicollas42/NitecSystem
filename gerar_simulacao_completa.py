# gerar_simulacao_completa.py
import sys
import os
import random
import time

# Adiciona o diretório atual ao path para importar os módulos 'src'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.controllers.estoque_controller import EstoqueController
from src.models import database

# Inicializa
controller = EstoqueController()
mapa_nomes = {} # Auxiliar para montar receitas

def header(texto):
    print(f"\n{'='*60}\n{texto}\n{'='*60}")

def log(texto):
    print(f" -> {texto}")

# ==============================================================================
# ETAPA 1: CADASTRO DE ITENS (INSUMOS E PRODUTOS)
# ==============================================================================
header("1. CADASTRANDO ITEM POR ITEM...")

# Insumos (Matéria Prima)
insumos_data = [
    ("1001", "FARINHA DE TRIGO ESPECIAL", "KG", "Insumos", 4.50, 100),
    ("1002", "FERMENTO BIOLÓGICO SECO", "KG", "Insumos", 12.00, 10),
    ("1003", "SAL REFINADO", "KG", "Insumos", 2.00, 50),
    ("1004", "AÇÚCAR CRISTAL", "KG", "Insumos", 3.80, 50),
    ("1005", "ÁGUA MINERAL", "L", "Insumos", 0.50, 200),
    ("1006", "OVOS VERMELHOS", "UN", "Insumos", 0.60, 360),
    ("1007", "LEITE INTEGRAL", "L", "Laticínios", 4.20, 100),
    ("1008", "MANTEIGA SEM SAL", "KG", "Laticínios", 35.00, 20),
    ("1009", "ÓLEO DE SOJA", "L", "Insumos", 7.00, 60),
    ("1010", "QUEIJO MINAS PADRÃO", "KG", "Frios", 45.00, 15),
    ("1011", "PRESUNTO COZIDO", "KG", "Frios", 30.00, 15),
    ("1012", "CENOURA FRESCA", "KG", "Hortifruti", 3.50, 20),
    ("1013", "CHOCOLATE EM PÓ", "KG", "Confeitaria", 25.00, 10),
    ("1014", "FERMENTO QUÍMICO (PÓ)", "G", "Insumos", 0.03, 2000),
    ("1015", "EMBALAGEM SACO PAPEL", "UN", "Embalagens", 0.10, 5000),
    ("1016", "COPO DESCARTÁVEL", "UN", "Embalagens", 0.05, 1000),
    ("1017", "CAFÉ EM PÓ", "KG", "Insumos", 22.00, 10),
    ("1018", "PEITO DE FRANGO", "KG", "Frios", 18.00, 30),
]

# Produtos Finais (Venda)
produtos_data = [
    ("2001", "PÃO FRANCÊS", "PRODUTO", "KG", "Panificação", 16.90, 5),
    ("2002", "PÃO DE QUEIJO", "PRODUTO", "KG", "Panificação", 39.90, 3),
    ("2003", "BOLO DE CENOURA", "PRODUTO", "UN", "Confeitaria", 22.00, 5),
    ("2004", "COXINHA DE FRANGO", "PRODUTO", "UN", "Salgados", 6.50, 10),
    ("2005", "MISTO QUENTE", "PRODUTO", "UN", "Salgados", 12.00, 0),
    ("2006", "CAFÉ EXPRESSO", "PRODUTO", "UN", "Bebidas", 5.00, 0),
    ("2007", "COCA COLA 2L", "PRODUTO", "UN", "Bebidas", 14.00, 10), # Revenda
]

# Cadastrando Insumos
for i in insumos_data:
    dados = {
        "id": i[0], "nome": i[1], "unidade": i[2], "categoria": i[3],
        "custo": str(i[4]), "preco": "0.00", "minimo": str(i[5]),
        "tipo": "INSUMO", "controla_estoque": True
    }
    controller.salvar_produto(dados)
    mapa_nomes[i[0]] = i[1] # Guarda nome para usar na receita
    
    # SIMULAÇÃO DE COMPRA (Chegada do fornecedor)
    qtd_compra = random.randint(50, 500)
    controller.movimentar_estoque(i[0], qtd_compra, "ENTRADA_COMPRA", "Nota Fiscal 001", "Sistema", "fundo")
    log(f"Comprado: {i[1]} (+{qtd_compra} {i[2]})")

# Cadastrando Produtos
for p in produtos_data:
    dados = {
        "id": p[0], "nome": p[1], "tipo": p[2], "unidade": p[3], "categoria": p[4],
        "preco": str(p[5]), "minimo": str(p[6]), "custo": "0.00", 
        "controla_estoque": True # Todos controlam estoque nesta simulação
    }
    controller.salvar_produto(dados)
    mapa_nomes[p[0]] = p[1]
    
    # Se for revenda (Coca Cola), já entra direto no estoque
    if p[1] == "COCA COLA 2L":
        controller.movimentar_estoque(p[0], 50, "ENTRADA_COMPRA", "Fornecedor Bebidas", "Sistema", "fundo")

log("✅ Cadastro Concluído.")

# ==============================================================================
# ETAPA 2: CRIAÇÃO DAS FICHAS TÉCNICAS
# ==============================================================================
header("2. O PADEIRO ESCREVE AS RECEITAS...")

def item_rec(id_ins, qtd):
    return {"id": id_ins, "nome": mapa_nomes.get(id_ins, "???"), "qtd": qtd}

# Pão Francês (Base 50kg)
rec_pao = [
    item_rec("1001", 30.0), # Farinha
    item_rec("1005", 18.0), # Água
    item_rec("1003", 0.6),  # Sal
    item_rec("1002", 0.9)   # Fermento
]
controller.salvar_receita("2001", "50", rec_pao)

# Bolo Cenoura (Base 10un)
rec_bolo = [
    item_rec("1012", 3.0),  # Cenoura
    item_rec("1006", 30.0), # Ovos
    item_rec("1009", 2.0),  # Óleo
    item_rec("1004", 4.0),  # Açúcar
    item_rec("1001", 4.0),  # Farinha
    item_rec("1013", 1.0)   # Chocolate
]
controller.salvar_receita("2003", "10", rec_bolo)

# Coxinha (Base 100un)
rec_coxinha = [
    item_rec("1001", 3.0), # Farinha
    item_rec("1018", 4.0), # Frango
    item_rec("1005", 3.0)  # Água (Caldo)
]
controller.salvar_receita("2004", "100", rec_coxinha)

# Café Expresso (Base 1un)
rec_cafe = [
    item_rec("1017", 0.02), # 20g Café
    item_rec("1004", 0.01), # 10g Açúcar
    item_rec("1016", 1.0)   # 1 Copo
]
controller.salvar_receita("2006", "1", rec_cafe)

log("✅ Receitas Criadas e Custos Calculados.")

# ==============================================================================
# ETAPA 3: PRODUÇÃO (FÁBRICA)
# ==============================================================================
header("3. PRODUÇÃO: O FORNO ESTÁ LIGADO!")

# O sistema vai baixar Farinha do FUNDO e colocar Pão no FUNDO
producoes = [
    ("2001", 60, "Padeiro João"), # 60kg Pão
    ("2003", 15, "Confeiteira Maria"), # 15 Bolos
    ("2004", 200, "Salgadeira Ana"), # 200 Coxinhas
    ("2002", 20, "Padeiro João") # 20kg Pão de Queijo (S/ Receita para teste)
]

for pid, qtd, user in producoes:
    ok, msg = controller.registrar_producao(pid, qtd, user)
    log(f"Produzido: {qtd} {mapa_nomes[pid]} -> {msg}")

log("✅ Estoque de Insumos baixado. Estoque de Produtos (Fundo) criado.")

# ==============================================================================
# ETAPA 4: ABASTECIMENTO (FUNDO -> FRENTE)
# ==============================================================================
header("4. ABASTECIMENTO: ENCHENDO A VITRINE")

# Movendo mercadoria para a loja para poder vender
reposicoes = [
    ("2001", 40), # Pão Francês
    ("2003", 10), # Bolo
    ("2004", 80), # Coxinha
    ("2007", 24), # Coca Cola
    ("2002", 10)  # Pão de Queijo
]

for pid, qtd in reposicoes:
    controller.transferir_fundo_para_frente(pid, qtd, "Gerente", "Abertura de Loja")
    log(f"Enviado para Loja: {qtd} {mapa_nomes[pid]}")

# ==============================================================================
# ETAPA 5: VENDAS NO CAIXA (O GRAN FINALE)
# ==============================================================================
header("5. CAIXA ABERTO: CLIENTES COMPRANDO!")

# Função auxiliar para simular o que o arquivo view_caixa.py faz
def simular_venda_pdv(itens_carrinho, operador="Ana Caixa", pag="Dinheiro"):
    # 1. Calcula Total
    total_venda = 0.0
    lista_para_salvar = []
    
    produtos_db = database.carregar_produtos()
    
    print(f"🛒 Cliente no Caixa ({operador}):")
    
    for id_prod, qtd_venda in itens_carrinho:
        prod = produtos_db.get(id_prod)
        if prod:
            preco = prod['preco']
            subtotal = preco * qtd_venda
            total_venda += subtotal
            
            # Verifica se é Café (Produção na hora da venda)
            if prod['nome'] == "CAFÉ EXPRESSO":
                # Produz 1 na hora pra ter estoque pra vender
                controller.registrar_producao(id_prod, qtd_venda, "Barista")
                controller.transferir_fundo_para_frente(id_prod, qtd_venda, "Barista", "Venda Balcão")
            
            log(f"   - Bipou: {qtd_venda}x {prod['nome']} (R$ {subtotal:.2f})")
            
            lista_para_salvar.append({
                "produto": prod['nome'],
                "qtd": qtd_venda,
                "total": subtotal
            })
            
    # 2. Chama o Database para registrar Financeiro e Baixar Estoque da Frente
    database.registrar_venda(total_venda, lista_para_salvar, operador, pag)
    print(f"   💰 TOTAL: R$ {total_venda:.2f} (Pago com {pag}) - ✅ VENDA FINALIZADA\n")

# --- CLIENTE 1: Café da Manhã ---
carrinho_1 = [
    ("2001", 0.500), # 500g Pão Francês
    ("2002", 0.300), # 300g Pão de Queijo
    ("2006", 2)      # 2 Cafés (Produção automática)
]
simular_venda_pdv(carrinho_1, "Ana Caixa", "Débito")

# --- CLIENTE 2: Lanche da Tarde ---
carrinho_2 = [
    ("2004", 5), # 5 Coxinhas
    ("2007", 2), # 2 Cocas
    ("2003", 1)  # 1 Bolo Inteiro
]
simular_venda_pdv(carrinho_2, "Ana Caixa", "Pix")

# --- CLIENTE 3: Levar pra casa ---
carrinho_3 = [
    ("2001", 1.0), # 1kg Pão
    ("2005", 2)    # 2 Misto Quente
]
simular_venda_pdv(carrinho_3, "Carlos Dono", "Dinheiro")

header("🏁 SIMULAÇÃO COMPLETA FINALIZADA!")
print("Agora abra o sistema e verifique:")
print("1. [Dashboard] Cards Financeiros atualizados.")
print("2. [Estoque -> Histórico] Todas as movimentações coloridas.")
print("3. [Financeiro] As 3 vendas registradas.")
print("4. [Visão Geral] Estoques da Frente reduzidos pelas vendas.")