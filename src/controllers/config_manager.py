# src/controllers/config_manager.py
import json
import os
import customtkinter as ctk

# Caminho ajustado para a nova estrutura de pastas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ARQUIVO_CONFIG = os.path.join(BASE_DIR, "dados", "config_pdv.json")

def carregar_config():
    padrao = {"modo": "Dark", "cor_destaque": "#2CC985"}
    if not os.path.exists(ARQUIVO_CONFIG):
        return padrao
    try:
        with open(ARQUIVO_CONFIG, "r") as f:
            return json.load(f)
    except:
        return padrao

def aplicar_tema_inicial():
    cfg = carregar_config()
    ctk.set_appearance_mode(cfg["modo"])
    ctk.set_default_color_theme("blue")
    return cfg