# src/models/database.py
import json
import os
from datetime import datetime

# --- CONFIGURAÇÃO DE CAMINHOS ABSOLUTOS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "dados")

ARQ_PRODUTOS = os.path.join(DATA_DIR, "produtos.json")
ARQ_MOVIMENTOS = os.path.join(DATA_DIR, "movimentos.json")
ARQ_VENDAS = os.path.join(DATA_DIR, "vendas.json")
ARQ_SOBRAS = os.path.join(DATA_DIR, "sobras.json")

USUARIOS = {
    "admin": {"senha": "123", "nome": "Carlos Dono", "role": "admin"},
    "operador": {"senha": "123", "nome": "Ana Caixa", "role": "caixa"}
}

def carregar_json(caminho):
    if not os.path.exists(caminho): return {} if "produtos" in caminho else []
    try:
        with open(caminho, "r", encoding="utf-8") as f: return json.load(f)
    except: return {} if "produtos" in caminho else []

def salvar_json(caminho, dados):
    try:
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
    except Exception as e: print(f"Erro ao salvar: {e}")

# --- PRODUTOS ---
def carregar_produtos():
    return carregar_json(ARQ_PRODUTOS)

def salvar_produtos(dados):
    salvar_json(ARQ_PRODUTOS, dados)

# --- MOVIMENTAÇÕES ---
def registrar_movimentacao(tipo, produto_id, nome, qtd, motivo, usuario, saldo_anterior, saldo_novo):
    """O Livro Razão do Estoque"""
    log = {
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipo": tipo, # ENTRADA, SAIDA, AJUSTE
        "cod": produto_id,
        "nome": nome,
        "qtd": qtd,
        "anterior": saldo_anterior,
        "novo": saldo_novo,
        "motivo": motivo,
        "usuario": usuario
    }
    movs = carregar_json(ARQ_MOVIMENTOS)
    movs.append(log)
    salvar_json(ARQ_MOVIMENTOS, movs)

# --- VENDAS ---
def registrar_venda(total, itens, operador, pagamento):
    # 1. Registro Financeiro
    vendas = carregar_json(ARQ_VENDAS)
    registro = {
        "id": int(datetime.now().timestamp()),
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "total": total,
        "itens": itens,
        "operador": operador,
        "pagamento": pagamento
    }
    vendas.append(registro)
    salvar_json(ARQ_VENDAS, vendas)
    
    # 2. Baixa de Estoque (FRENTE) - APENAS UMA VEZ
    produtos = carregar_produtos()
    for item in itens:
        for pid, dados in produtos.items():
            if dados['nome'] == item['produto']:
                # Só baixa se o produto estiver configurado para controlar estoque
                # (Ex: Pão Francês pode estar como False, Água como True)
                if dados.get('controla_estoque', True):
                    qtd_venda = float(item['qtd'])
                    
                    # Usa 'estoque_atual' que representa a FRENTE da loja
                    saldo_ant = dados.get('estoque_atual', 0.0)
                    saldo_novo = saldo_ant - qtd_venda
                    
                    dados['estoque_atual'] = round(saldo_novo, 4)
                    
                    # Registra a saída no histórico para auditoria
                    registrar_movimentacao(
                        "SAIDA_VENDA", 
                        pid, 
                        dados['nome'], 
                        -qtd_venda, 
                        "Venda PDV", 
                        operador, 
                        saldo_ant, 
                        saldo_novo
                    )
                break
    salvar_produtos(produtos)

# --- UTILS ---
def verificar_login(u, s):
    return USUARIOS.get(u) if USUARIOS.get(u, {}).get("senha") == s else None

# Atalhos globais
PRODUTOS = carregar_produtos()