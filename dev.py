import sys
import time
import subprocess
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuração
ARQUIVO_PRINCIPAL = "run.py"  # Seu arquivo principal
PASTA_OBSERVADA = "."         # Pasta atual (e subpastas)

class OrganizadorDeReinicio(FileSystemEventHandler):
    def __init__(self):
        self.processo = None
        self.iniciar_app()

    def iniciar_app(self):
        if self.processo:
            print("🔄 Reiniciando aplicação...")
            self.processo.terminate() # Mata o processo antigo
            self.processo.wait()      # Espera fechar
        else:
            print("🚀 Iniciando aplicação...")

        # Inicia o run.py como um sub-processo
        self.processo = subprocess.Popen([sys.executable, ARQUIVO_PRINCIPAL])

    def on_modified(self, event):
        # Se o arquivo modificado for .py, reinicia
        if event.src_path.endswith(".py"):
            # Pequeno delay para garantir que o arquivo foi salvo completamente
            time.sleep(0.5) 
            self.iniciar_app()

if __name__ == "__main__":
    path = PASTA_OBSERVADA
    event_handler = OrganizadorDeReinicio()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    print(f"👀 Observando alterações em arquivos .py na pasta: {os.path.abspath(path)}")
    print("✍️  Salve qualquer arquivo para recarSSregar.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.processo:
            event_handler.processo.terminate()
    observer.join()