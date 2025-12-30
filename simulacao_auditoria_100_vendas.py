# simulacao_auditoria_100_vendas.py
import sys
import os
import random
from datetime import datetime, timedelta

# Adiciona o diretório atual ao path para importar os módulos 'src'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.controllers.estoque_controller import EstoqueController
from src.models import database

controller = EstoqueController()

def header(texto): print(f"\n{'='*70}\n{texto}\n{'='*70}")
def log(texto): print(f" -> {texto}")

# ==============================================================================
# 1. RESET GERAL
# ==============================================================================
header("1. LIMPEZA DOS DADOS (RESET DE FÁBRICA)")
arquivos = ["produtos.json", "movimentos.json", "vendas.json", "receitas.json", 
            "sobras.json", "maquinas.json", "tarifas.json"]

for arq in arquivos:
    caminho = os.path.join(database.DATA_DIR, arq)
    if os.path.exists(caminho):
        os.remove(caminho)
        # Recria arquivos vazios
        conteudo = '{}' if arq in ['receitas.json', 'produtos.json', 'maquinas.json', 'tarifas.json'] else '[]'
        with open(caminho, 'w') as f: f.write(conteudo)

log("🗑️  Sistema limpo.")

# ==============================================================================
# 2. CONFIGURAÇÃO DA FÁBRICA
# ==============================================================================
header("2. CONFIGURANDO TARIFAS E MÁQUINAS")

controller.salvar_tarifas({
    "energia_kwh": 1.00,   # Facilitar conta: R$ 1,00/kWh
    "gas_kg": 10.00,       # Facilitar conta: R$ 10,00/kg
    "agua_m3": 15.00,      
    "mao_obra_h": 20.00    # Facilitar conta: R$ 20,00/h
})

maquinas = [
    ("MQ01", "Forno Turbo", 500, 1.0),   # 500W, 1.0kg gás/h
    ("MQ02", "Batedeira", 1000, 0),      # 1000W
    ("MQ03", "Fritadeira", 4000, 0)      # 4000W
]
for m in maquinas: controller.salvar_maquina(*m)
log("⚙️ Fábrica configurada (Valores redondos para facilitar auditoria).")

# ==============================================================================
# 3. CADASTRO DE ITENS
# ==============================================================================
header("3. CADASTRANDO PRODUTOS")

# Insumos
insumos = [
    ("100", "FARINHA", "KG", 5.00),    # R$ 5,00/kg
    ("101", "RECHEIO", "KG", 25.00),   # R$ 25,00/kg
    ("102", "OLEO", "L", 8.00),        # R$ 8,00/L
    ("9000", "AGUA FILTRADA", "L", 0.05) # R$ 0,05/L
]
for i in insumos:
    controller.salvar_produto({"id": i[0], "nome": i[1], "unidade": i[2], "categoria": "Insumos", "custo": str(i[3]), "tipo": "INSUMO"})
    controller.movimentar_estoque(i[0], 5000, "ENTRADA_COMPRA", "Estoque Inicial", "Admin", "fundo")

# Revenda (Lucro Simples)
# Coca-Cola: Compra por 7.00, Vende por 14.00 (Lucro Bruto: R$ 7,00 por unidade)
controller.salvar_produto({
    "id": "501", "nome": "COCA-COLA 2L", "unidade": "UN", "grupo": "BEBIDAS", "categoria": "Revenda",
    "custo": "7.00", "preco": "14.00", "tipo": "PRODUTO", "controla_estoque": True,
    "codigos_barras": ["789501"]
})
controller.movimentar_estoque("501", 500, "ENTRADA_COMPRA", "Fornecedor", "Admin", "fundo")

# Internos
internos = [
    ("201", "COXINHA", "UN", "SALGADOS"),
    ("202", "PAO CASEIRO", "KG", "PADARIA")
]
for p in internos:
    controller.salvar_produto({"id": p[0], "nome": p[1], "unidade": p[2], "grupo": p[3], "categoria": "Producao", "tipo": "INTERNO", "custo": "0", "preco": "0"})

log("✅ Itens cadastrados.")

# ==============================================================================
# 4. ENGENHARIA E CUSTOS (GABARITO)
# ==============================================================================
header("4. CALCULANDO CUSTOS (ATENÇÃO AOS VALORES!)")

# Precisamos do dicionário de produtos atualizado para a função helper
prods_db = database.carregar_produtos()
def criar_ing(cod, qtd):
    return {"id": cod, "qtd": qtd, "nome": prods_db[cod]['nome'], "un": prods_db[cod]['unidade']}

# --- COXINHA (Receita para 100 unidades) ---
# Matéria Prima:
# 3kg Farinha (3 * 5.00) = 15.00
# 4kg Recheio (4 * 25.00) = 100.00
# 2L Óleo (2 * 8.00) = 16.00
# 1L Água (1 * 0.05) = 0.05
# TOTAL MP: 131.05
#
# Máquinas:
# Fritadeira (4000W = 4kW) por 1h. Tarifa R$ 1,00/kWh. Custo Luz = 4 * 1.00 = 4.00
#
# Mão de Obra:
# 1h30 (90 min). Tarifa R$ 20,00/h. Custo MOD = 1.5 * 20.00 = 30.00
#
# CUSTO TOTAL LOTE: 131.05 + 4.00 + 30.00 = 165.05
# CUSTO UNITÁRIO (100 un): R$ 1.65 (arredondado)
# Margem 200% -> Preço Venda Sugerido: 1.65 * (1 + 2) = R$ 4.95
# Vamos definir um preço fixo de R$ 5.00 para facilitar a conta.

controller.salvar_receita_avancada(
    id_produto="201", rendimento="100",
    ingredientes=[criar_ing("100", 3), criar_ing("101", 4), criar_ing("102", 2), criar_ing("9000", 1)],
    maquinas_uso=[{"id": "MQ03", "tempo_min": 60}],
    tempo_mao_obra_min=90, margem_lucro=203 # Ajuste fino para bater perto de R$ 5,00
)
# Força preço exato de R$ 5,00 para ficar bonito no relatório
prod_coxinha = database.carregar_produtos()["201"]
prod_coxinha['preco'] = 5.00
database.salvar_produtos(database.carregar_produtos() | {"201": prod_coxinha}) # Merge update

log("📝 Coxinha: Custo ~R$ 1,65 | Venda R$ 5,00 | Lucro Unit ~R$ 3,35")


# --- PÃO CASEIRO (Receita para 10 KG) ---
# Matéria Prima:
# 6kg Farinha (6 * 5.00) = 30.00
# 4L Água (4 * 0.05) = 0.20
# Total MP: 30.20
#
# Máquinas:
# Forno (500W, 1kg Gás/h) por 1h (60min).
# Luz: 0.5kW * 1h * R$1 = 0.50
# Gás: 1kg * 1h * R$10 = 10.00
# Maq Total: 10.50
#
# Mão de Obra: 30 min (0.5h). 0.5 * 20.00 = 10.00
#
# TOTAL LOTE: 30.20 + 10.50 + 10.00 = 50.70
# CUSTO KG (10 kg): R$ 5.07
# Venda sugerida: R$ 15.00

controller.salvar_receita_avancada(
    id_produto="202", rendimento="10",
    ingredientes=[criar_ing("100", 6), criar_ing("9000", 4)],
    maquinas_uso=[{"id": "MQ01", "tempo_min": 60}],
    tempo_mao_obra_min=30, margem_lucro=195
)
# Força preço R$ 15,00
prod_pao = database.carregar_produtos()["202"]
prod_pao['preco'] = 15.00
database.salvar_produtos(database.carregar_produtos() | {"202": prod_pao})

log("📝 Pão Caseiro: Custo ~R$ 5,07 | Venda R$ 15,00 | Lucro Unit ~R$ 9,93")

# ==============================================================================
# 5. PRODUÇÃO E DISTRIBUIÇÃO
# ==============================================================================
header("5. PRODUZINDO E TRANSFERINDO")

# Produz estoque suficiente para 100 vendas
controller.registrar_producao("201", 500, "Salgadeira") # 500 Coxinhas
controller.registrar_producao("202", 200, "Padeiro")    # 200 Kg Pão

controller.transferir_fundo_para_frente("201", 500, "Gerente")
controller.transferir_fundo_para_frente("202", 200, "Gerente")
controller.transferir_fundo_para_frente("501", 500, "Gerente") # Coca

log("✅ Estoque abastecido na Frente de Loja.")

# ==============================================================================
# 6. SIMULAÇÃO DE 100 VENDAS (A PROVA REAL)
# ==============================================================================
header("6. EXECUTANDO 100 VENDAS...")

# Perfis de Compra
# 1. Lanche: 2 Coxinhas + 1 Coca
# 2. Padaria: 1kg Pão
# 3. Misto: 1 Coxinha + 0.5kg Pão + 1 Coca

prods = database.carregar_produtos()
total_faturado = 0
contagem_itens = {"201": 0, "202": 0, "501": 0}

for i in range(1, 101):
    perfil = random.choice([1, 2, 3])
    itens_venda = []
    
    if perfil == 1: # Lanche
        itens_venda.append({"id": "201", "qtd": 2})
        itens_venda.append({"id": "501", "qtd": 1})
    elif perfil == 2: # Padaria
        itens_venda.append({"id": "202", "qtd": 1.0})
    elif perfil == 3: # Misto
        itens_venda.append({"id": "201", "qtd": 1})
        itens_venda.append({"id": "202", "qtd": 0.5})
        itens_venda.append({"id": "501", "qtd": 1})

    # Processa Venda
    valor_venda = 0
    lista_final = []
    
    for item in itens_venda:
        pid = item['id']
        qtd = item['qtd']
        nome = prods[pid]['nome']
        preco = prods[pid]['preco']
        total_item = qtd * preco
        
        valor_venda += total_item
        lista_final.append({"produto": nome, "qtd": qtd, "total": total_item})
        
        # Estatísticas para o Gabarito
        contagem_itens[pid] += qtd

    database.registrar_venda(valor_venda, lista_final, "Ana Caixa", "Dinheiro")
    total_faturado += valor_venda
    
    if i % 20 == 0:
        print(f"   ... {i} vendas processadas.")

# ==============================================================================
# 7. O GABARITO (PARA CONFERÊNCIA)
# ==============================================================================
header("🏁 GABARITO DA AUDITORIA (CONFIRA NO SISTEMA)")

print(f"💰 FATURAMENTO TOTAL ESPERADO: R$ {total_faturado:,.2f}\n")

print(f"{'PRODUTO':<20} | {'QTD VENDIDA':<12} | {'CUSTO UNIT':<12} | {'VENDA UNIT':<12} | {'LUCRO ESPERADO':<15}")
print("-" * 85)

lucro_total_esperado = 0

for pid in ["201", "202", "501"]:
    p = prods[pid]
    qtd = contagem_itens[pid]
    custo = p['custo']
    venda = p['preco']
    
    receita_item = qtd * venda
    custo_item = qtd * custo
    lucro_item = receita_item - custo_item
    lucro_total_esperado += lucro_item
    
    print(f"{p['nome']:<20} | {qtd:<12.2f} | R$ {custo:<9.2f} | R$ {venda:<9.2f} | R$ {lucro_item:,.2f}")

print("-" * 85)
print(f"🏆 LUCRO LÍQUIDO TOTAL ESPERADO: R$ {lucro_total_esperado:,.2f}")
print("\n👉 Vá na aba 'Auditoria Estoque' e verifique se a coluna 'LUCRO LÍQ.' bate com esses valores!")