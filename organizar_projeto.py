import os
import shutil

# Estrutura desejada
pastas = [
    "dados",
    "src",
    "src/controllers",
    "src/models",
    "src/views",
    "src/assets"
]

# Cria as pastas
for p in pastas:
    if not os.path.exists(p):
        os.makedirs(p)
        print(f"📁 Pasta criada: {p}")

# Cria __init__.py em cada subpasta do src para o Python reconhecer como pacote
init_files = ["src", "src/controllers", "src/models", "src/views"]
for p in init_files:
    open(os.path.join(p, "__init__.py"), "a").close()

# Mapa de migração (Origem -> Destino)
movimentos = {
    "produtos.json": "dados/produtos.json",
    "vendas.json": "dados/vendas.json",
    "sobras.json": "dados/sobras.json",
    "config_pdv.json": "dados/config_pdv.json",
    
    "database.py": "src/models/database.py",
    "config_manager.py": "src/controllers/config_manager.py", # Promovido a controller
    
    "view_login.py": "src/views/view_login.py",
    "view_dashboard.py": "src/views/view_dashboard.py",
    "view_caixa.py": "src/views/view_caixa.py",
    "view_estoque.py": "src/views/view_estoque.py",
    "view_sobras.py": "src/views/view_sobras.py",
    "view_financeiro.py": "src/views/view_financeiro.py",
    
    "main.py": "src/views/main_view.py" # O main antigo vira a view principal
}

for origem, destino in movimentos.items():
    if os.path.exists(origem):
        shutil.move(origem, destino)
        print(f"✅ Movido: {origem} -> {destino}")
    else:
        print(f"⚠️ Não encontrado: {origem} (Pode já ter sido movido)")

# Cria o novo lançador RUN.PY na raiz
run_content = """
import sys
import os

# Adiciona a pasta raiz ao caminho do Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.views.main_view import AppPrincipal

if __name__ == "__main__":
    app = AppPrincipal()
    app.mainloop()
"""

with open("run.py", "w", encoding="utf-8") as f:
    f.write(run_content)

print("\n🚀 Reorganização completa! Execute o sistema agora pelo arquivo 'run.py'.")
print("ATENÇÃO: Você precisará corrigir os 'imports' dentro dos arquivos movidos.")