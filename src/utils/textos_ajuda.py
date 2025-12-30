# src/utils/textos_ajuda.py
import customtkinter as ctk

# Controle global da instância da janela de ajuda
_janela_ajuda_instancia = None

AJUDAS = {
    "cadastro": {
        "titulo": "📖 MANUAL DE CADASTRO",
        "texto": """
🎯 PARA QUE SERVE ESTA TELA?
Registre aqui tudo o que entra ou sai da sua padaria.

🛠️ REGRAS DO JOGO:
1. TIPO DO ITEM
• 📦 INSUMO: Matéria-prima que você COMPRA.
• 🍞 PRODUTO: O que você VENDE.

2. CAMPOS DE VALOR
• Custo (R$): Preço de compra.
• Venda (R$): Preço no caixa.
"""
    },
    "receitas": {
        "titulo": "👩‍🍳 FICHA TÉCNICA (RECEITAS)",
        "texto": """
🎯 PASSO A PASSO:
1️⃣ Selecione o PRODUTO FINAL.
2️⃣ Defina o RENDIMENTO.
3️⃣ Adicione os INSUMOS usados.
4️⃣ Clique em SALVAR para atualizar custos.
"""
    },
    "producao": {
        "titulo": "🏭 REGISTRO DE PRODUÇÃO",
        "texto": """
🎯 COMO FUNCIONA:
1️⃣ Escolha o item fabricado.
2️⃣ Informe a quantidade produzida.
3️⃣ O sistema baixa os Insumos e adiciona o Produto Pronto.
"""
    },
    "movimentacao": {
        "titulo": "🔄 MOVIMENTAÇÃO DE ESTOQUE",
        "texto": """
🔼 ENTRADA: Compras ou ajustes.
🗑️ PERDA: Itens estragados.
📦 REPOSIÇÃO: Move do Depósito para a Loja.
"""
    },
    "historico": {
        "titulo": "📜 HISTÓRICO DE MOVIMENTAÇÕES",
        "texto": """
🎯 PARA QUE SERVE ESTA TELA?
Consulte todas as entradas, saídas e produções realizadas no sistema.

🔍 FILTROS DISPONÍVEIS:
• Produto: Busca por um item específico.
• Usuário: Quem realizou a operação.
• Tipo: Filtra por Venda, Perda, Produção, etc.
• Datas: Clique nos campos de data para abrir o calendário.

💡 DICA:
Clique nos títulos das colunas da tabela para ordenar os dados!
"""
    }
}

def abrir_ajuda(master, topico):
    """
    Exibe uma janela de ajuda centralizada com base no tópico fornecido.

    @param master: Janela ou Frame pai.
    @param topico: Chave correspondente ao conteúdo no dicionário AJUDAS.
    @return: None
    """
    global _janela_ajuda_instancia

    # Se a janela já existe, apenas traz para frente
    if _janela_ajuda_instancia is not None and _janela_ajuda_instancia.winfo_exists():
        _janela_ajuda_instancia.deiconify()
        _janela_ajuda_instancia.lift()
        _janela_ajuda_instancia.focus_force()
        return

    if topico not in AJUDAS:
        return
        
    conteudo = AJUDAS[topico]
    
    # Criação da janela independente
    _janela_ajuda_instancia = ctk.CTkToplevel(master)
    _janela_ajuda_instancia.title("NitecSystem - Manual")
    _janela_ajuda_instancia.geometry("550x550")
    
    # Força a janela a aparecer no topo na criação
    _janela_ajuda_instancia.attributes("-topmost", True)
    _janela_ajuda_instancia.after(500, lambda: _janela_ajuda_instancia.attributes("-topmost", False))

    # Conteúdo (Label e Scroll)
    ctk.CTkLabel(_janela_ajuda_instancia, text=conteudo["titulo"], 
                 font=("Arial", 20, "bold"), text_color="#2CC985").pack(pady=20)
    
    scroll = ctk.CTkScrollableFrame(_janela_ajuda_instancia, fg_color="transparent")
    scroll.pack(fill="both", expand=True, padx=10, pady=10)

    lbl = ctk.CTkLabel(scroll, text=conteudo["texto"], justify="left", 
                       anchor="nw", padx=20, font=("Consolas", 13))
    lbl.pack(fill="both", expand=True)

    _janela_ajuda_instancia.lift()
    _janela_ajuda_instancia.focus_force()