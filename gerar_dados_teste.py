import json
import random
import os
from datetime import datetime, timedelta

# --- CORREÇÃO DE CAMINHO ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Removemos o "src" do caminho para alinhar com o database.py
DATA_DIR = os.path.join(BASE_DIR, "dados") 

ARQ_PRODUTOS = os.path.join(DATA_DIR, "produtos.json")
ARQ_VENDAS = os.path.join(DATA_DIR, "vendas.json")
ARQ_MOVIMENTOS = os.path.join(DATA_DIR, "movimentos.json")

def carregar_json(caminho):
    if not os.path.exists(caminho): return [] if "produtos" not in caminho else {}
    with open(caminho, "r", encoding="utf-8") as f: return json.load(f)

def salvar_json(caminho, dados):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def gerar_dados():
    print(f"🔄 Buscando dados em: {DATA_DIR}")
    produtos = carregar_json(ARQ_PRODUTOS)
    vendas = carregar_json(ARQ_VENDAS) # Carrega vendas existentes se houver
    if isinstance(vendas, dict): vendas = [] # Garante lista
    
    movimentos = carregar_json(ARQ_MOVIMENTOS)
    if isinstance(movimentos, dict): movimentos = [] # Garante lista
    
    if not produtos:
        print("❌ Erro: Nenhum produto encontrado! Rode o 'popular_produtos.py' primeiro.")
        return

    lista_ids = list(produtos.keys())
    operadores = ["Ana Caixa", "Carlos Dono", "Roberto Gerente"]
    pagamentos = ["Dinheiro", "Pix", "Débito", "Crédito"]
    
    print("🚀 Gerando 100 vendas...")

    for i in range(100):
        dias_atras = random.randint(0, 6)
        hora_aleatoria = random.randint(6, 20)
        minuto_aleatorio = random.randint(0, 59)
        
        data_venda = datetime.now() - timedelta(days=dias_atras)
        data_venda = data_venda.replace(hour=hora_aleatoria, minute=minuto_aleatorio)
        data_str = data_venda.strftime("%d/%m/%Y %H:%M")
        data_iso = data_venda.strftime("%Y-%m-%d %H:%M:%S")

        qtd_itens_cesta = random.randint(1, 5)
        itens_venda = []
        total_venda = 0.0

        for _ in range(qtd_itens_cesta):
            pid = random.choice(lista_ids)
            prod = produtos[pid]
            
            if prod.get('unidade') in ['KG', 'L']:
                qtd = round(random.uniform(0.1, 2.0), 3)
            else:
                qtd = random.randint(1, 6)
            
            preco = prod.get('preco', 0.0)
            total_item = round(qtd * preco, 2)
            
            itens_venda.append({
                "produto": prod['nome'],
                "qtd": qtd,
                "total": total_item
            })
            total_venda += total_item

            # Baixa de Estoque Simulada
            saldo_ant = prod.get('estoque_atual', 0.0)
            saldo_novo = round(saldo_ant - qtd, 4)
            prod['estoque_atual'] = saldo_novo

            movimentos.append({
                "data": data_iso,
                "tipo": "SAIDA_VENDA",
                "cod": pid,
                "nome": prod['nome'],
                "qtd": -qtd,
                "anterior": saldo_ant,
                "novo": saldo_novo,
                "motivo": "Simulação",
                "usuario": "Bot"
            })

        vendas.append({
            "id": int(data_venda.timestamp()) + i,
            "data": data_str,
            "total": round(total_venda, 2),
            "itens": itens_venda,
            "operador": random.choice(operadores),
            "pagamento": random.choice(pagamentos)
        })

    salvar_json(ARQ_PRODUTOS, produtos)
    salvar_json(ARQ_VENDAS, vendas)
    salvar_json(ARQ_MOVIMENTOS, movimentos)

    print(f"✅ Sucesso! Vendas salvas em {ARQ_VENDAS}")

if __name__ == "__main__":
    gerar_dados()