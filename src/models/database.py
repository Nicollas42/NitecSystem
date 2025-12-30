# src/models/database.py
import json
import os
import sys
from datetime import datetime

# --- CONFIGURAÇÃO DE CAMINHOS (PORTABILIDADE EXE/PEN DRIVE) ---
def obter_caminho_base():
    """
    Retorna o diretório base correto:
    - Se for .exe: Retorna a pasta onde o executável está.
    - Se for .py: Retorna a pasta raiz do projeto.
    """
    if getattr(sys, 'frozen', False):
        # Se estiver rodando como executável (.exe)
        return os.path.dirname(sys.executable)
    else:
        # Se estiver rodando como script (.py) - sobe 3 níveis (src/models/database.py -> raiz)
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_DIR = obter_caminho_base()
DATA_DIR = os.path.join(BASE_DIR, "dados")

# Garante que a pasta dados existe para evitar erros de "directory not found"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Caminhos dos Arquivos
ARQ_PRODUTOS = os.path.join(DATA_DIR, "produtos.json")
ARQ_MOVIMENTOS = os.path.join(DATA_DIR, "movimentos.json")
ARQ_VENDAS = os.path.join(DATA_DIR, "vendas.json")
ARQ_SOBRAS = os.path.join(DATA_DIR, "sobras.json")
ARQ_RECEITAS = os.path.join(DATA_DIR, "receitas.json")
ARQ_MAQUINAS = os.path.join(DATA_DIR, "maquinas.json")
ARQ_TARIFAS = os.path.join(DATA_DIR, "tarifas.json")

# Usuários Hardcoded (Poderia ser um JSON também, mas mantive simples)
USUARIOS = {
    "admin": {"senha": "123", "nome": "Carlos Dono", "role": "admin"},
    "operador": {"senha": "123", "nome": "Ana Caixa", "role": "caixa"}
}

# --- FUNÇÕES DE LEITURA/ESCRITA ---

def carregar_json(caminho):
    """
    Carrega um arquivo JSON. Se não existir, retorna vazio (dict ou list).
    Isso permite que o sistema inicie 'limpo' sem dar erro.
    """
    if not os.path.exists(caminho):
        # Se for arquivos de Dicionário, retorna {}, senão []
        if any(x in caminho for x in ["produtos.json", "receitas.json", "maquinas.json", "tarifas.json"]):
            return {}
        return []
    
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao ler {caminho}: {e}")
        if any(x in caminho for x in ["produtos.json", "receitas.json", "maquinas.json", "tarifas.json"]):
            return {}
        return []

def salvar_json(caminho, dados):
    """Salva os dados no arquivo JSON com formatação bonita."""
    try:
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar em {caminho}: {e}")

# --- MÉTODOS DE ACESSO (PRODUTOS) ---

def carregar_produtos():
    return carregar_json(ARQ_PRODUTOS)

def salvar_produtos(dados):
    salvar_json(ARQ_PRODUTOS, dados)

# --- MOVIMENTAÇÕES (LIVRO RAZÃO) ---

def registrar_movimentacao(tipo, produto_id, nome, qtd, motivo, usuario, saldo_anterior, saldo_novo):
    log = {
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipo": tipo, # ENTRADA, SAIDA, AJUSTE, TRANSFERENCIA
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

# --- VENDAS E BAIXA DE ESTOQUE ---

def registrar_venda(total, itens, operador, pagamento):
    # 1. Registro Financeiro da Venda
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
        # Tenta achar o produto pelo nome (o item['produto'] vem da venda)
        for pid, dados in produtos.items():
            if dados['nome'] == item['produto']:
                
                # Só baixa se o produto estiver configurado para controlar estoque
                if dados.get('controla_estoque', True):
                    try:
                        qtd_venda = float(item['qtd'])
                    except:
                        qtd_venda = 0.0
                    
                    # Usa 'estoque_atual' que representa a FRENTE da loja
                    saldo_ant = dados.get('estoque_atual', 0.0)
                    saldo_novo = saldo_ant - qtd_venda
                    
                    dados['estoque_atual'] = round(saldo_novo, 4)
                    
                    # Registra a saída no histórico para auditoria
                    registrar_movimentacao(
                        "SAIDA_VENDA_FRENTE", 
                        pid, 
                        dados['nome'], 
                        -qtd_venda, 
                        f"Venda PDV {registro['id']}", 
                        operador, 
                        saldo_ant, 
                        saldo_novo
                    )
                break # Sai do loop de produtos e vai para o próximo item da venda
                
    salvar_produtos(produtos)

# --- UTILS / LOGIN ---

def verificar_login(u, s):
    return USUARIOS.get(u) if USUARIOS.get(u, {}).get("senha") == s else None

# Atalho global (opcional, usado em alguns scripts antigos)
PRODUTOS = carregar_produtos()