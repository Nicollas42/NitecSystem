import json
import os

# --- CORREÇÃO DE CAMINHO ---
# Pega a pasta onde o script está rodando (Raiz do Projeto)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Aponta para a pasta 'dados' na raiz, e não dentro de 'src'
DADOS_DIR = os.path.join(BASE_DIR, "dados") 
ARQ_PRODUTOS = os.path.join(DADOS_DIR, "produtos.json")

# Garante que a pasta dados existe
if not os.path.exists(DADOS_DIR):
    os.makedirs(DADOS_DIR)

def salvar_json(caminho, dados):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def criar_produtos_fakes():
    produtos = {
        "101": {
            "id": "101",
            "nome": "PÃO FRANCÊS",
            "unidade": "KG",
            "categoria": "Panificação",
            "preco": 12.90,
            "estoque_minimo": 5.0,
            "estoque_atual": 10.0,  # Frente
            "estoque_fundo": 0.0,   # Produção diária
            "controla_estoque": False, # Pão não bloqueia
            "ativo": True
        },
        "102": {
            "id": "102",
            "nome": "LEITE INTEGRAL 1L",
            "unidade": "UN",
            "categoria": "Bebidas",
            "preco": 6.50,
            "estoque_minimo": 12.0,
            "estoque_atual": 20.0,
            "estoque_fundo": 48.0,
            "controla_estoque": True,
            "ativo": True
        },
        "103": {
            "id": "103",
            "nome": "CAFÉ EXPRESSO",
            "unidade": "UN",
            "categoria": "Bebidas",
            "preco": 4.00,
            "estoque_minimo": 0.0,
            "estoque_atual": 100.0, # Insumo
            "estoque_fundo": 0.0,
            "controla_estoque": False,
            "ativo": True
        },
        "104": {
            "id": "104",
            "nome": "QUEIJO MUSSARELA",
            "unidade": "KG",
            "categoria": "Frios",
            "preco": 49.90,
            "estoque_minimo": 2.0,
            "estoque_atual": 3.500,
            "estoque_fundo": 10.000,
            "controla_estoque": True,
            "ativo": True
        },
        "105": {
            "id": "105",
            "nome": "COCA COLA 2L",
            "unidade": "UN",
            "categoria": "Bebidas",
            "preco": 14.00,
            "estoque_minimo": 10.0,
            "estoque_atual": 15.0,
            "estoque_fundo": 60.0,
            "controla_estoque": True,
            "ativo": True
        }
    }

    print(f"💾 Cadastrando produtos em: {ARQ_PRODUTOS}")
    salvar_json(ARQ_PRODUTOS, produtos)
    print("✅ Sucesso! 5 produtos criados.")

if __name__ == "__main__":
    criar_produtos_fakes()