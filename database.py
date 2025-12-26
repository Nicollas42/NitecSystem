# database.py
import json
import os
from datetime import datetime

ARQUIVO_PRODUTOS = "produtos.json"
ARQUIVO_SOBRAS = "sobras.json"
ARQUIVO_VENDAS = "vendas.json"

USUARIOS = {
    "admin": {"senha": "123", "nome": "Carlos Dono", "role": "admin"},
    "operador": {"senha": "123", "nome": "Ana Caixa", "role": "caixa"}
}

# --- PRODUTOS & ESTOQUE ---
def carregar_produtos():
    padrao = {
        "101": {"nome": "Pão Francês (KG)", "preco": 14.90, "un": "KG", "estoque": 0},
        "102": {"nome": "Pão de Queijo", "preco": 3.50, "un": "UN", "estoque": 0},
        "7891": {"nome": "Coca-Cola 2L", "preco": 10.00, "un": "UN", "estoque": 0},
    }
    
    if not os.path.exists(ARQUIVO_PRODUTOS):
        salvar_produtos(padrao)
        return padrao
    
    try:
        with open(ARQUIVO_PRODUTOS, "r", encoding="utf-8") as f:
            produtos = json.load(f)
            # Migração: Garante que todos tenham o campo 'estoque'
            for cod in produtos:
                if "estoque" not in produtos[cod]:
                    produtos[cod]["estoque"] = 0
            return produtos
    except:
        return padrao

def salvar_produtos(produtos_dict):
    try:
        with open(ARQUIVO_PRODUTOS, "w", encoding="utf-8") as f:
            json.dump(produtos_dict, f, indent=4, ensure_ascii=False)
    except: pass

def atualizar_estoque(cod, delta):
    """
    Altera a quantidade do produto.
    delta > 0: Entrada (Compra)
    delta < 0: Saída (Venda ou Perda)
    """
    produtos = carregar_produtos()
    if cod in produtos:
        atual = produtos[cod].get("estoque", 0)
        novo_saldo = atual + delta
        produtos[cod]["estoque"] = novo_saldo
        salvar_produtos(produtos)

# --- SOBRAS ---
def registrar_sobra(cod, nome, qtd, motivo, operador):
    registro = {
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "cod": cod, "nome": nome, "qtd": qtd, "motivo": motivo, "operador": operador
    }
    historico = carregar_arquivo(ARQUIVO_SOBRAS)
    historico.append(registro)
    salvar_arquivo(historico, ARQUIVO_SOBRAS)
    
    # Baixa no estoque automaticamente
    atualizar_estoque(cod, -qtd)

def carregar_sobras():
    return carregar_arquivo(ARQUIVO_SOBRAS)

# --- VENDAS ---
def registrar_venda(total, itens, operador, pagamento="Dinheiro"):
    registro = {
        "id_venda": int(datetime.now().timestamp()),
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "total": total,
        "itens": itens,
        "operador": operador,
        "pagamento": pagamento
    }
    historico = carregar_arquivo(ARQUIVO_VENDAS)
    historico.append(registro)
    salvar_arquivo(historico, ARQUIVO_VENDAS)

    # Baixa no estoque para cada item vendido
    for item in itens:
        # Tenta pegar o código do produto pelo nome (ideal seria salvar o codigo na venda, mas vamos buscar)
        # Nota: Num sistema real, salve o CODIGO na lista de itens da venda para ser mais seguro.
        # Aqui vamos fazer uma busca rápida no DB atual
        produtos = carregar_produtos()
        for cod, dados in produtos.items():
            if dados['nome'] == item['produto']:
                atualizar_estoque(cod, -float(item['qtd']))
                break

def carregar_vendas():
    return carregar_arquivo(ARQUIVO_VENDAS)

# --- UTILITÁRIOS ---
def carregar_arquivo(caminho):
    if not os.path.exists(caminho): return []
    try:
        with open(caminho, "r", encoding="utf-8") as f: return json.load(f)
    except: return []

def salvar_arquivo(dados, caminho):
    try:
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
    except Exception as e: print(e)

# --- LOGIN ---
def verificar_login(usuario, senha):
    if usuario in USUARIOS and USUARIOS[usuario]["senha"] == senha: return USUARIOS[usuario]
    return None

PRODUTOS = carregar_produtos()