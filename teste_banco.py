import psycopg2

def testar_conexao():
    try:
        # 1. Conectar ao banco
        conn = psycopg2.connect(
            host="localhost",
            database="nitec_db",
            user="postgres",
            password="zacU1322685617!"  # <--- Coloque a senha da instalação
        )
        
        # O cursor é quem "executa" os comandos
        cursor = conn.cursor()
        
        print("✅ Conexão com PostgreSQL realizada com sucesso!")

        # 2. Criar uma tabela de teste (se não existir)
        # Note que precisamos definir o TIPO de cada dado (INTEGER, TEXT, DECIMAL)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos_teste (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                preco DECIMAL(10, 2)
            );
        """)
        
        # 3. Inserir um produto (INSERT)
        cursor.execute("INSERT INTO produtos_teste (nome, preco) VALUES (%s, %s)", ("Coxinha", 5.50))
        conn.commit() # <--- OBRIGATÓRIO: Confirmar a gravação
        print("✅ Produto inserido!")

        # 4. Ler os produtos (SELECT)
        cursor.execute("SELECT * FROM produtos_teste;")
        resultado = cursor.fetchall()
        
        print("\n📦 Produtos no Banco:")
        for linha in resultado:
            print(linha) # Vai sair algo como: (1, 'Coxinha', 5.50)

        # 5. Fechar
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")

if __name__ == "__main__":
    testar_conexao()