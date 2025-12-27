import json
import os

# --- CONFIGURAÇÃO ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DADOS_DIR = os.path.join(BASE_DIR, "dados")

# Garante a pasta
if not os.path.exists(DADOS_DIR): os.makedirs(DADOS_DIR)

def salvar(nome, dados):
    with open(os.path.join(DADOS_DIR, nome), "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def resetar_sistema():
    print("🧹 Limpando banco de dados...")
    
    # 1. Zera Vendas e Movimentos
    salvar("vendas.json", [])
    salvar("movimentos.json", [])
    salvar("sobras.json", [])

    # 2. Cadastra Produtos Iniciais (Com Estoque ZERADO para simularmos a entrada depois)
    produtos = {
        "101": {
            "id": "101", "nome": "PÃO FRANCÊS", "unidade": "KG", "categoria": "Panificação",
            "preco": 14.90, "estoque_minimo": 5.0, 
            "estoque_atual": 0.0, "estoque_fundo": 0.0, "controla_estoque": False, "ativo": True
        },
        "102": {
            "id": "102", "nome": "LEITE INTEGRAL 1L", "unidade": "UN", "categoria": "Bebidas",
            "preco": 6.50, "estoque_minimo": 6.0, 
            "estoque_atual": 0.0, "estoque_fundo": 0.0, "controla_estoque": True, "ativo": True
        },
        "103": {
            "id": "103", "nome": "COCA COLA 2L", "unidade": "UN", "categoria": "Bebidas",
            "preco": 14.00, "estoque_minimo": 10.0, 
            "estoque_atual": 0.0, "estoque_fundo": 0.0, "controla_estoque": True, "ativo": True
        },
        "104": {
            "id": "104", "nome": "QUEIJO MUSSARELA", "unidade": "KG", "categoria": "Frios",
            "preco": 59.90, "estoque_minimo": 2.0, 
            "estoque_atual": 0.0, "estoque_fundo": 0.0, "controla_estoque": True, "ativo": True
        },
        "105": {
            "id": "105", "nome": "SONHO DE CREME", "unidade": "UN", "categoria": "Confeitaria",
            "preco": 4.50, "estoque_minimo": 0.0, 
            "estoque_atual": 0.0, "estoque_fundo": 0.0, "controla_estoque": False, "ativo": True
        }
    }
    
    salvar("produtos.json", produtos)
    print("✅ Sistema resetado! Produtos cadastrados com estoque ZERO.")

if __name__ == "__main__":
    resetar_sistema()