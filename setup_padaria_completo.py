import json
import os

# --- CONFIGURAÇÃO DE CAMINHOS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DADOS_DIR = os.path.join(BASE_DIR, "dados")

# Garante que a pasta dados existe
if not os.path.exists(DADOS_DIR):
    os.makedirs(DADOS_DIR)

def salvar_json(nome_arquivo, dados):
    caminho = os.path.join(DADOS_DIR, nome_arquivo)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
    print(f"✅ Arquivo atualizado: {nome_arquivo}")

def setup_total():
    print("🚀 INICIANDO RESET E CONFIGURAÇÃO DA PADARIA PROFISSIONAL...")
    print("-" * 50)

    # 1. ZERA OS ARQUIVOS DE MOVIMENTAÇÃO
    salvar_json("vendas.json", [])
    salvar_json("movimentos.json", [])
    salvar_json("sobras.json", [])
    
    # Se quiser já criar o arquivo de receitas vazio para o futuro
    if not os.path.exists(os.path.join(DADOS_DIR, "receitas.json")):
        salvar_json("receitas.json", {})

    # 2. DEFINE O CADASTRO DE INSUMOS E PRODUTOS
    # Estrutura nova com 'tipo' e 'custo'
    db_produtos = {
        # --- INSUMOS (MATÉRIA-PRIMA) ---
        "1001": {
            "id": "1001", "nome": "FARINHA DE TRIGO ESPECIAL", "tipo": "INSUMO",
            "unidade": "KG", "categoria": "Insumos",
            "custo": 4.50, "preco": 0.00, # Custa 4.50, não vende
            "estoque_minimo": 50.0, "estoque_atual": 0.0, "estoque_fundo": 100.0, # Começa com 100kg no estoque
            "controla_estoque": True, "ativo": True
        },
        "1002": {
            "id": "1002", "nome": "FERMENTO BIOLÓGICO SECO", "tipo": "INSUMO",
            "unidade": "G", "categoria": "Insumos",
            "custo": 0.08, "preco": 0.00, # 8 centavos a grama
            "estoque_minimo": 500.0, "estoque_atual": 0.0, "estoque_fundo": 2000.0,
            "controla_estoque": True, "ativo": True
        },
        "1003": {
            "id": "1003", "nome": "SAL REFINADO", "tipo": "INSUMO",
            "unidade": "G", "categoria": "Insumos",
            "custo": 0.005, "preco": 0.00,
            "estoque_minimo": 1000.0, "estoque_atual": 0.0, "estoque_fundo": 5000.0,
            "controla_estoque": True, "ativo": True
        },
        "1004": {
            "id": "1004", "nome": "AÇÚCAR CRISTAL", "tipo": "INSUMO",
            "unidade": "KG", "categoria": "Insumos",
            "custo": 3.80, "preco": 0.00,
            "estoque_minimo": 20.0, "estoque_atual": 0.0, "estoque_fundo": 50.0,
            "controla_estoque": True, "ativo": True
        },
        "1005": {
            "id": "1005", "nome": "LEITE INTEGRAL (CX)", "tipo": "INSUMO",
            "unidade": "L", "categoria": "Insumos",
            "custo": 4.20, "preco": 0.00,
            "estoque_minimo": 12.0, "estoque_atual": 0.0, "estoque_fundo": 48.0,
            "controla_estoque": True, "ativo": True
        },
        "1006": {
            "id": "1006", "nome": "OVOS VERMELHOS", "tipo": "INSUMO",
            "unidade": "UN", "categoria": "Insumos",
            "custo": 0.50, "preco": 0.00,
            "estoque_minimo": 30.0, "estoque_atual": 0.0, "estoque_fundo": 180.0,
            "controla_estoque": True, "ativo": True
        },
        "1007": {
            "id": "1007", "nome": "MANTEIGA SEM SAL", "tipo": "INSUMO",
            "unidade": "G", "categoria": "Insumos",
            "custo": 0.04, "preco": 0.00,
            "estoque_minimo": 500.0, "estoque_atual": 0.0, "estoque_fundo": 2000.0,
            "controla_estoque": True, "ativo": True
        },

        # --- PRODUTOS FINAIS (VENDA) ---
        "2001": {
            "id": "2001", "nome": "PÃO FRANCÊS", "tipo": "PRODUTO",
            "unidade": "KG", "categoria": "Panificação",
            "custo": 0.00, "preco": 14.90, # Custo será calculado pela receita depois
            "estoque_minimo": 5.0, "estoque_atual": 10.0, "estoque_fundo": 0.0,
            "controla_estoque": False, "ativo": True
        },
        "2002": {
            "id": "2002", "nome": "PÃO DE QUEIJO", "tipo": "PRODUTO",
            "unidade": "KG", "categoria": "Panificação",
            "custo": 0.00, "preco": 29.90,
            "estoque_minimo": 2.0, "estoque_atual": 3.5, "estoque_fundo": 0.0,
            "controla_estoque": True, "ativo": True
        },
        "2003": {
            "id": "2003", "nome": "BOLO DE CENOURA", "tipo": "PRODUTO",
            "unidade": "UN", "categoria": "Confeitaria",
            "custo": 0.00, "preco": 18.00,
            "estoque_minimo": 2.0, "estoque_atual": 4.0, "estoque_fundo": 0.0,
            "controla_estoque": True, "ativo": True
        },
        "2004": {
            "id": "2004", "nome": "SONHO DE CREME", "tipo": "PRODUTO",
            "unidade": "UN", "categoria": "Confeitaria",
            "custo": 0.00, "preco": 4.50,
            "estoque_minimo": 5.0, "estoque_atual": 12.0, "estoque_fundo": 0.0,
            "controla_estoque": True, "ativo": True
        },
        "2005": {
            "id": "2005", "nome": "COCA COLA 2L", "tipo": "PRODUTO",
            "unidade": "UN", "categoria": "Bebidas",
            "custo": 7.50, "preco": 14.00, # Revenda (tem custo fixo e preço venda)
            "estoque_minimo": 12.0, "estoque_atual": 6.0, "estoque_fundo": 24.0,
            "controla_estoque": True, "ativo": True
        },
        "2006": {
            "id": "2006", "nome": "CAFÉ EXPRESSO", "tipo": "PRODUTO",
            "unidade": "UN", "categoria": "Bebidas",
            "custo": 0.00, "preco": 5.00,
            "estoque_minimo": 0.0, "estoque_atual": 999.0, "estoque_fundo": 0.0,
            "controla_estoque": False, "ativo": True
        }
    }

    salvar_json("produtos.json", db_produtos)
    
    print("-" * 50)
    print("✅ BANCO DE DADOS RECONSTRUÍDO COM SUCESSO!")
    print("   - Histórico limpo.")
    print("   - Insumos cadastrados (Farinha, Fermento, etc).")
    print("   - Produtos cadastrados (Pão, Bolo, etc).")
    print("👉 Agora abra o sistema e confira a aba Cadastro!")

if __name__ == "__main__":
    setup_total()