import os
import sys
import django
import customtkinter as ctk

# =============================================================================
# 1. INICIALIZAÇÃO DO DJANGO (O CÉREBRO)
# =============================================================================
# Define onde estão as configurações do projeto (settings.py)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nitec_core.settings')

# Inicializa o ORM e carrega os Apps
try:
    django.setup()
    print("✅ Django inicializado com sucesso! O ORM está pronto.")
except Exception as e:
    print(f"❌ Erro crítico ao iniciar Django: {e}")
    sys.exit(1)

# =============================================================================
# 2. INICIALIZAÇÃO DO TKINTER (A CARA)
# =============================================================================
# ATENÇÃO: Os imports do seu sistema DEVEM ficar abaixo do django.setup()
# Se você importar antes, o sistema quebra.

from src.views.view_login import LoginView 
# (Ou from src.views.main_view import MainApp, dependendo de como você iniciava)

def main():
    # Configuração do CustomTkinter
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    # TESTE RÁPIDO: Vamos ver se o Django consegue buscar produtos no banco
    try:
        # Importando aqui dentro para garantir que o Django já carregou
        from gestao.models import Produto
        qtd_produtos = Produto.objects.count()
        print(f"🚀 TESTE DE CONEXÃO: Você tem {qtd_produtos} produtos cadastrados no PostgreSQL via Django!")
    except Exception as e:
        print(f"⚠️ Aviso: Não foi possível testar o banco agora ({e})")

    # Inicia a Janela de Login (ou MainView)
    root = ctk.CTk()
    app = LoginView(root) # Ajuste aqui se sua classe principal tiver outro nome
    root.mainloop()

if __name__ == "__main__":
    main()