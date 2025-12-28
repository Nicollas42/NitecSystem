# src/dev_state.py
import json
import os

ARQUIVO_ESTADO = "dev_state.json"

def salvar_estado(dados):
    """Salva um dicionário com o estado atual (tela, aba, etc)"""
    try:
        # Se o arquivo já existe, lê para não perder dados de outras chaves
        conteudo_atual = {}
        if os.path.exists(ARQUIVO_ESTADO):
            with open(ARQUIVO_ESTADO, 'r') as f:
                try: conteudo_atual = json.load(f)
                except: pass
        
        # Atualiza com os novos dadoss
        conteudo_atual.update(dados)
        
        with open(ARQUIVO_ESTADO, 'w') as f:
            json.dump(conteudo_atual, f)
    except Exception as e:
        print(f"Erro ao salvar estado dev: {e}")

def carregar_estado():
    """Lê o estado salvo"""
    if not os.path.exists(ARQUIVO_ESTADO):
        return {}
    try:
        with open(ARQUIVO_ESTADO, 'r') as f:
            return json.load(f)
    except:
        return {}