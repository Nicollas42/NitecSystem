# src/models/database_sql.py
import psycopg2
import json
from psycopg2.extras import RealDictCursor, Json

class DatabaseSQL:
    def __init__(self):
        # CONFIGURAÇÕES DO BANCO (Ajuste a senha aqui)
        self.host = "localhost"
        self.database = "nitec_db"
        self.user = "postgres"
        self.password = "zacU1322685617!"  # <--- COLOQUE SUA SENHA AQUI
        self.port = "5432"

    def get_connection(self):
        """Abre uma conexão com o banco e retorna."""
        conn = psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password,
            port=self.port
        )
        return conn

    def criar_tabelas(self):
        """Cria a estrutura do banco se não existir."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            print("🔨 Criando/Verificando tabelas no PostgreSQL...")

            # 1. TABELA DE PRODUTOS
            # Substitui produtos.json
            # Usamos JSONB para 'codigos_barras' para aceitar múltiplos códigos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS produtos (
                    id VARCHAR(50) PRIMARY KEY,
                    nome TEXT NOT NULL,
                    tipo VARCHAR(20),
                    grupo VARCHAR(50),
                    unidade VARCHAR(10),
                    preco DECIMAL(10, 2) DEFAULT 0.00,
                    custo DECIMAL(10, 4) DEFAULT 0.00,
                    estoque_atual DECIMAL(10, 4) DEFAULT 0.00,
                    estoque_fundo DECIMAL(10, 4) DEFAULT 0.00,
                    estoque_minimo DECIMAL(10, 4) DEFAULT 0.00,
                    controla_estoque BOOLEAN DEFAULT TRUE,
                    codigos_barras JSONB DEFAULT '[]'::jsonb,
                    categoria TEXT,
                    data_cadastro DATE,
                    ativo BOOLEAN DEFAULT TRUE
                );
            """)

            # 2. TABELA DE MOVIMENTAÇÕES
            # Substitui movimentos.json
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS movimentacoes (
                    id SERIAL PRIMARY KEY,
                    data TIMESTAMP,
                    cod_produto VARCHAR(50) REFERENCES produtos(id),
                    nome_produto TEXT,
                    qtd DECIMAL(10, 4),
                    tipo VARCHAR(50),
                    motivo TEXT,
                    usuario VARCHAR(50),
                    saldo_anterior DECIMAL(10, 4),
                    saldo_novo DECIMAL(10, 4)
                );
            """)

            # 3. TABELA DE VENDAS
            # Substitui vendas.json
            # 'itens' guarda o carrinho inteiro em formato JSON para facilitar
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vendas (
                    id SERIAL PRIMARY KEY,
                    data TIMESTAMP,
                    total DECIMAL(10, 2),
                    pagamento VARCHAR(50),
                    operador VARCHAR(50),
                    itens JSONB NOT NULL
                );
            """)

            # 4. TABELA DE MÁQUINAS
            # Substitui maquinas.json
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS maquinas (
                    id VARCHAR(50) PRIMARY KEY,
                    nome TEXT,
                    potencia_w DECIMAL(10, 2),
                    gas_kg_h DECIMAL(10, 4)
                );
            """)

            # 5. TABELA DE RECEITAS (Ficha Técnica)
            # Substitui receitas.json
            # Guarda ingredientes e máquinas usadas como JSONB para flexibilidade
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS receitas (
                    id_produto VARCHAR(50) PRIMARY KEY REFERENCES produtos(id),
                    nome TEXT,
                    rendimento DECIMAL(10, 4),
                    tempo_preparo DECIMAL(10, 2),
                    margem_lucro DECIMAL(10, 2),
                    imposto_perc DECIMAL(10, 2) DEFAULT 0.00,
                    custo_insumos DECIMAL(10, 4),
                    custo_maquinas DECIMAL(10, 4),
                    custo_mao_obra DECIMAL(10, 4),
                    custo_total_lote DECIMAL(10, 4),
                    custo_unitario DECIMAL(10, 4),
                    ingredientes JSONB,
                    maquinas_uso JSONB
                );
            """)

            # 6. TABELA DE TARIFAS
            # Substitui tarifas.json (Armazena chave-valor)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tarifas (
                    chave VARCHAR(50) PRIMARY KEY,
                    valor DECIMAL(10, 4)
                );
            """)

            conn.commit()
            print("✅ Todas as tabelas foram criadas com sucesso!")

        except Exception as e:
            print(f"❌ Erro ao criar tabelas: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    db = DatabaseSQL()
    db.criar_tabelas()