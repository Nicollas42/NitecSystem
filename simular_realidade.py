import json
import random
import os
from datetime import datetime, timedelta

# --- CONFIGURAÇÃO ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DADOS_DIR = os.path.join(BASE_DIR, "dados")
ARQ_PRODUTOS = os.path.join(DADOS_DIR, "produtos.json")
ARQ_VENDAS = os.path.join(DADOS_DIR, "vendas.json")
ARQ_MOVIMENTOS = os.path.join(DADOS_DIR, "movimentos.json")

def carregar(nome):
    with open(os.path.join(DADOS_DIR, nome), "r", encoding="utf-8") as f: return json.load(f)

def salvar(nome, dados):
    with open(os.path.join(DADOS_DIR, nome), "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def log_movimento(movs, data, tipo, cod, nome, qtd, ant, novo, motivo, usuario):
    movs.append({
        "data": data.strftime("%Y-%m-%d %H:%M:%S"),
        "tipo": tipo, "cod": cod, "nome": nome, 
        "qtd": round(qtd, 3), # <--- ARREDONDAMENTO NA GRAVAÇÃO
        "anterior": round(ant, 3), 
        "novo": round(novo, 3), 
        "motivo": motivo, "usuario": usuario
    })

def simular_rotina():
    print("🚀 Iniciando simulação de 7 dias de padaria (Com Correção de Casas Decimais)...")
    produtos = carregar("produtos.json")
    vendas = []
    movimentos = []
    
    operadores = ["Ana Caixa", "Carlos Dono"]
    data_base = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=7)

    for dia in range(8):
        data_atual = data_base + timedelta(days=dia)
        print(f"📅 Simulando dia: {data_atual.strftime('%d/%m/%Y')}...")

        # 1. MANHÃ: PRODUÇÃO E COMPRAS
        hora_entrada = data_atual.replace(hour=6, minute=random.randint(0, 30))
        for pid, p in produtos.items():
            qtd_entrada = 0
            motivo = ""
            
            if p['nome'] == "PÃO FRANCÊS":
                qtd_entrada = 50.0 
                motivo = "Produção da Manhã"
            elif p['nome'] == "LEITE INTEGRAL 1L":
                if p['estoque_fundo'] < 20: 
                    qtd_entrada = 24.0
                    motivo = "Entrega Laticínios"
            elif p['nome'] == "COCA COLA 2L":
                if p['estoque_fundo'] < 10:
                    qtd_entrada = 30.0
                    motivo = "Fornecedor Coca"
            
            if qtd_entrada > 0:
                ant = p['estoque_fundo']
                p['estoque_fundo'] = round(p['estoque_fundo'] + qtd_entrada, 3) # Arredonda
                log_movimento(movimentos, hora_entrada, "ENTRADA_FUNDO", pid, p['nome'], qtd_entrada, ant, p['estoque_fundo'], motivo, "Gerente")

        # 2. ABERTURA: ABASTECER PRATELEIRA
        hora_abastecer = data_atual.replace(hour=6, minute=45)
        for pid, p in produtos.items():
            meta_frente = 10.0
            if p['estoque_atual'] < meta_frente and p['estoque_fundo'] > 0:
                falta = round(meta_frente - p['estoque_atual'], 3) # <--- CORREÇÃO PRINCIPAL
                qtd_mover = min(falta, p['estoque_fundo'])
                qtd_mover = round(qtd_mover, 3) # Garante 3 casas
                
                if qtd_mover > 0:
                    ant_frente = p['estoque_atual']
                    p['estoque_fundo'] = round(p['estoque_fundo'] - qtd_mover, 3)
                    p['estoque_atual'] = round(p['estoque_atual'] + qtd_mover, 3)
                    log_movimento(movimentos, hora_abastecer, "TRANSFERENCIA", pid, p['nome'], qtd_mover, ant_frente, p['estoque_atual'], "Abastecimento Matinal", "Gerente")

        # 3. VENDAS DO DIA
        num_vendas = random.randint(10, 20)
        for _ in range(num_vendas):
            hora_venda = data_atual.replace(hour=random.randint(7, 20), minute=random.randint(0, 59))
            itens_venda = []
            total_venda = 0.0
            qtd_itens = random.randint(1, 3)

            for _ in range(qtd_itens):
                pid = random.choice(list(produtos.keys()))
                prod = produtos[pid]
                
                if prod['unidade'] == 'KG': qtd_quer = round(random.uniform(0.2, 0.8), 3)
                else: qtd_quer = random.randint(1, 3)

                # Reposição de Emergência
                if prod['controla_estoque'] and prod['estoque_atual'] < qtd_quer:
                    falta = round(qtd_quer - prod['estoque_atual'], 3)
                    if prod['estoque_fundo'] >= falta:
                        hora_repo = hora_venda - timedelta(minutes=1)
                        ant_frente = prod['estoque_atual']
                        
                        prod['estoque_fundo'] = round(prod['estoque_fundo'] - falta, 3)
                        prod['estoque_atual'] = round(prod['estoque_atual'] + falta, 3)
                        
                        log_movimento(movimentos, hora_repo, "TRANSFERENCIA", pid, prod['nome'], falta, ant_frente, prod['estoque_atual'], "🚨 REPOSIÇÃO CAIXA", "Ana Caixa")
                    else:
                        continue 

                preco = prod['preco']
                total_item = round(qtd_quer * preco, 2)
                
                ant_frente = prod['estoque_atual']
                prod['estoque_atual'] = round(prod['estoque_atual'] - qtd_quer, 3)

                log_movimento(movimentos, hora_venda, "SAIDA_VENDA", pid, prod['nome'], -qtd_quer, ant_frente, prod['estoque_atual'], "Venda Balcão", "Ana Caixa")
                
                itens_venda.append({"produto": prod['nome'], "qtd": qtd_quer, "total": total_item})
                total_venda += total_item

            if itens_venda:
                vendas.append({
                    "id": int(hora_venda.timestamp()),
                    "data": hora_venda.strftime("%d/%m/%Y %H:%M"),
                    "total": round(total_venda, 2),
                    "itens": itens_venda,
                    "operador": random.choice(operadores),
                    "pagamento": random.choice(["Dinheiro", "Pix", "Débito"])
                })

    salvar("produtos.json", produtos)
    salvar("vendas.json", vendas)
    salvar("movimentos.json", movimentos)
    print("✅ Simulação concluída!")

if __name__ == "__main__":
    simular_rotina()