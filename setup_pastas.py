# setup_pastas.py
import os
import shutil

# 1. Estrutura de Pastas
folders = [
    "dados",
    "src",
    "src/controllers",
    "src/models",
    "src/views"
]

for f in folders:
    if not os.path.exists(f):
        os.makedirs(f)
        print(f"📁 Criada: {f}")
        # Cria __init__.py para transformar em pacote Python
        if "src" in f:
            open(os.path.join(f, "__init__.py"), "a").close()

# 2. Mover Arquivos Existentes (Renomeando e Organizando)
moves = {
    "database.py": "src/models/database.py",
    "config_manager.py": "src/controllers/config_manager.py",
    "main.py": "src/views/main_view.py",
    "view_login.py": "src/views/view_login.py",
    "view_dashboard.py": "src/views/view_dashboard.py",
    "view_caixa.py": "src/views/view_caixa.py",
    "view_estoque.py": "src/views/view_estoque.py",
    "view_sobras.py": "src/views/view_sobras.py",
    "view_financeiro.py": "src/views/view_financeiro.py",
    "produtos.json": "dados/produtos.json",
    "vendas.json": "dados/vendas.json",
    "sobras.json": "dados/sobras.json",
    "config_pdv.json": "dados/config_pdv.json",
    "movimentos.json": "dados/movimentos.json" # Novo arquivo
}

for orig, dest in moves.items():
    if os.path.exists(orig):
        try:
            shutil.move(orig, dest)
            print(f"✅ Movido: {orig} -> {dest}")
        except:
            print(f"⚠️ Erro ao mover {orig} (arquivo pode estar aberto ou já movido)")

# 3. Criar o Executor (run.py)
run_code = """import sys
import os
from src.views.main_view import AppPrincipal

if __name__ == "__main__":
    app = AppPrincipal()
    app.mainloop()
"""
with open("run.py", "w") as f:
    f.write(run_code)

print("\n🚀 Estrutura MVC pronta! Agora atualize os códigos dos arquivos.")