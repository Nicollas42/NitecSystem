# migrar_para_sql.py
import json
import os
from src.models.database_sql import DatabaseSQL
from psycopg2.extras import Json

# Ajuste o caminho se sua pasta de dados for diferente
DIR_DADOS = "dados"  # ou "src/dados" dependendo da sua estrutura atual

def carregar_json(arquivo):
    caminho = os.path.join(DIR_DADOS, arquivo)
    if not os.path.exists(caminho):
        return {} if "produtos" in arquivo or "maquinas" in arquivo else []
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def migrar():
    db = DatabaseSQL()
    db.criar_tabelas() # Garante que existem
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        print("\n🚀 INICIANDO MIGRAÇÃO JSON -> POSTGRESQL\n")

        # 1. PRODUTOS
        produtos = carregar_json("produtos.json")
        print(f"📦 Migrando {len(produtos)} produtos...")
        for pid, p in produtos.items():
            cursor.execute("""
                INSERT INTO produtos (id, nome, tipo, grupo, unidade, preco, custo, 
                                      estoque_atual, estoque_fundo, estoque_minimo, 
                                      controla_estoque, codigos_barras, categoria, data_cadastro)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TO_DATE(%s, 'DD/MM/YYYY'))
                ON CONFLICT (id) DO NOTHING;
            """, (
                p.get('id'), p.get('nome'), p.get('tipo'), p.get('grupo'), p.get('unidade'),
                p.get('preco', 0), p.get('custo', 0), p.get('estoque_atual', 0),
                p.get('estoque_fundo', 0), p.get('estoque_minimo', 0),
                p.get('controla_estoque', True), Json(p.get('codigos_barras', [])),
                p.get('categoria'), p.get('data_cadastro')
            ))

        # 2. MÁQUINAS
        maquinas = carregar_json("maquinas.json")
        print(f"⚙️ Migrando {len(maquinas)} máquinas...")
        for mid, m in maquinas.items():
            cursor.execute("""
                INSERT INTO maquinas (id, nome, potencia_w, gas_kg_h)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
            """, (m.get('id'), m.get('nome'), m.get('potencia_w'), m.get('gas_kg_h')))

        # 3. TARIFAS
        tarifas = carregar_json("tarifas.json")
        print(f"⚡ Migrando tarifas...")
        for k, v in tarifas.items():
            cursor.execute("""
                INSERT INTO tarifas (chave, valor) VALUES (%s, %s)
                ON CONFLICT (chave) DO UPDATE SET valor = EXCLUDED.valor;
            """, (k, v))

        # 4. RECEITAS
        receitas = carregar_json("receitas.json")
        print(f"👩‍🍳 Migrando {len(receitas)} fichas técnicas...")
        for rid, r in receitas.items():
            custos = r.get('custos', {})
            cursor.execute("""
                INSERT INTO receitas (id_produto, nome, rendimento, tempo_preparo, margem_lucro, imposto_perc,
                                      custo_insumos, custo_maquinas, custo_mao_obra, custo_total_lote, custo_unitario,
                                      ingredientes, maquinas_uso)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id_produto) DO NOTHING;
            """, (
                r.get('id_produto'), r.get('nome'), r.get('rendimento'), r.get('tempo_preparo'), 
                r.get('margem_lucro'), r.get('imposto_perc', 0),
                custos.get('insumos', 0), custos.get('maquinas', 0), custos.get('mao_obra', 0),
                custos.get('total_lote', 0), custos.get('unitario', 0),
                Json(r.get('ingredientes', [])), Json(r.get('maquinas_uso', []))
            ))

        # 5. MOVIMENTAÇÕES (Cuidado com datas)
        movimentos = carregar_json("movimentos.json") # Lista
        print(f"🔄 Migrando {len(movimentos)} movimentações (pode demorar)...")
        for m in movimentos:
            # Tratamento de data simples
            data_str = m.get('data') # Ex: "2023-12-30 10:00:00"
            cursor.execute("""
                INSERT INTO movimentacoes (data, cod_produto, nome_produto, qtd, tipo, motivo, usuario, saldo_anterior, saldo_novo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (
                data_str, str(m.get('cod')), m.get('nome'), m.get('qtd'), m.get('tipo'),
                m.get('motivo'), m.get('usuario'), m.get('saldo_anterior', 0), m.get('novo_saldo', 0)
            ))

        # 6. VENDAS
        vendas = carregar_json("vendas.json") # Lista
        print(f"💰 Migrando {len(vendas)} vendas...")
        for v in vendas:
            cursor.execute("""
                INSERT INTO vendas (data, total, pagamento, operador, itens)
                VALUES (%s, %s, %s, %s, %s);
            """, (
                v.get('data'), v.get('total'), v.get('pagamento'), v.get('operador'), Json(v.get('itens', []))
            ))

        conn.commit()
        print("\n✅ SUCESSO! DADOS MIGRADOS PARA O POSTGRESQL.")
        print("Agora podemos atualizar o 'estoque_controller.py' para usar o banco novo.")

    except Exception as e:
        print(f"\n❌ ERRO FATAL NA MIGRAÇÃO: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrar()
    