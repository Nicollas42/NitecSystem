# config_manager.py
import json
import os
import customtkinter as ctk

ARQUIVO_CONFIG = "config_pdv.json"

def carregar_config():
    padrao = {"modo": "Dark", "cor_destaque": "#2CC985"}
    if not os.path.exists(ARQUIVO_CONFIG):
        return padrao
    try:
        with open(ARQUIVO_CONFIG, "r") as f:
            return json.load(f)
    except:
        return padrao

def salvar_config(nova_config):
    try:
        with open(ARQUIVO_CONFIG, "w") as f:
            json.dump(nova_config, f)
    except:
        pass

def aplicar_tema_inicial():
    cfg = carregar_config()
    ctk.set_appearance_mode(cfg["modo"])
    ctk.set_default_color_theme("blue")
    return cfg