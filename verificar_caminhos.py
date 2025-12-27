import os

def listar_estrutura(pasta_inicial="."):
    print(f"📂 Mapeando estrutura a partir de: {os.path.abspath(pasta_inicial)}\n")
    
    # Pastas para ignorar na busca
    ignorar = {'.git', '__pycache__', '.idea', 'venv', '.vscode'}

    for raiz, pastas, arquivos in os.walk(pasta_inicial):
        # Remove pastas indesejadas da lista de busca
        pastas[:] = [d for d in pastas if d not in ignorar]
        
        # Calcula o nível de indentação para o "desenho" da árvore
        nivel = raiz.replace(pasta_inicial, '').count(os.sep)
        indentacao = ' ' * 4 * (nivel)
        
        # Mostra a pasta atual
        pasta_atual = os.path.basename(raiz)
        if pasta_atual == '.':
            pasta_atual = "RAIZ DO PROJETO"
        print(f"{indentacao}📁 {pasta_atual}/")
        
        # Mostra os arquivos dentro dela
        sub_indentacao = ' ' * 4 * (nivel + 1)
        for f in arquivos:
            print(f"{sub_indentacao}📄 {f}")

if __name__ == "__main__":
    # Pega o diretório onde este script está salvo
    caminho_atual = os.path.dirname(os.path.abspath(__file__))
    listar_estrutura(caminho_atual)
    
    input("\n✅ Pressione ENTER para sair...")