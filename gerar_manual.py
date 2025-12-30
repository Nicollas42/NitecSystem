# gerar_manual.py
import os

conteudo = """
==============================================================================
📘 NITEC SYSTEM V4 - MANUAL DE REGRAS DE NEGÓCIO E CÁLCULOS
==============================================================================
Versão: 4.0 (Industrial / Padaria)
Data: 2025

------------------------------------------------------------------------------
1. CLASSIFICAÇÃO DE ITENS
------------------------------------------------------------------------------
O sistema divide os cadastros em 3 categorias para definir a origem do custo
e do estoque:

[A] INSUMO
    - O que é: Matéria-prima (Farinha, Ovo, Água Filtrada).
    - Origem do Custo: Definido manualmente no cadastro (preço de compra).
    - Estoque: Entra via Nota Fiscal/Compra no Estoque FUNDO.
    - Exemplo: Farinha de Trigo, Gás (se controlado), Água (Item 9000).

[B] PRODUTO (REVENDA)
    - O que é: Item comprado pronto para revender.
    - Origem do Custo: Preço de Compra.
    - Estoque: Entra via Compra no Estoque FUNDO.
    - Exemplo: Coca-Cola, Manteiga, Chiclete.

[C] INTERNO (FABRICAÇÃO PRÓPRIA)
    - O que é: Produto feito na casa.
    - Origem do Custo: CALCULADO pela Ficha Técnica (Ingredientes + Máquinas + MO).
    - Estoque: Entra via ORDEM DE PRODUÇÃO no Estoque FUNDO.
    - Exemplo: Pão Francês, Coxinha, Bolo.

------------------------------------------------------------------------------
2. ENGENHARIA DE CUSTOS (CÁLCULOS)
------------------------------------------------------------------------------
Utilizamos o Custeio por Absorção Simplificado.
O custo de um produto fabricado é a soma de 3 pilares:

FÓRMULA GERAL:
Custo Total = (Custo Matéria Prima) + (Custo Mão de Obra) + (Custo Máquinas)

--- DETALHAMENTO ---

1. Matéria Prima (MP)
   Soma do custo de todos os ingredientes usados na receita.
   * A Água (Item 9000) entra aqui para compor o peso físico correto.

2. Mão de Obra Direta (MOD)
   Custo do tempo do funcionário dedicado à receita.
   Fórmula: (Tempo em Minutos / 60) * Tarifa Hora do Funcionário

3. Custos Indiretos (Máquinas - Energia e Gás)
   Calculado por máquina usada.

   A) Energia Elétrica:
      Custo = (Potência em Watts / 1000) * (Tempo Uso / 60) * Tarifa kWh

   B) Gás:
      Custo = (Consumo kg/h) * (Tempo Uso / 60) * Tarifa kg Gás

------------------------------------------------------------------------------
3. PRECIFICAÇÃO (MARKUP)
------------------------------------------------------------------------------
Após achar o Custo Total do lote, dividimos pelo rendimento.

1. Custo Unitário = Custo Total do Lote / Quantidade Rendimento
2. Preço Sugerido = Custo Unitário * (1 + (Margem de Lucro % / 100))

Exemplo:
Custo Unitário = R$ 1,00
Margem Desejada = 200%
Preço Venda = 1,00 * (1 + 2) = R$ 3,00

------------------------------------------------------------------------------
4. DINÂMICA DE ESTOQUE (FUNDO vs FRENTE)
------------------------------------------------------------------------------
O sistema possui dois locais de estoque para controle de perdas e reposição.

[1] ESTOQUE FUNDO (Depósito/Fábrica)
    - Onde chegam as Compras.
    - Onde a Produção deposita os itens prontos.
    - O CAIXA NÃO VENDE DAQUI.

[2] ESTOQUE FRENTE (Loja/Vitrine)
    - Onde o cliente pega o produto.
    - O CAIXA SÓ VENDE DAQUI.

Fluxo:
Compra -> Fundo -> (Produção) -> Fundo -> Transferência -> Frente -> Venda

------------------------------------------------------------------------------
5. AUDITORIA E RESULTADO
------------------------------------------------------------------------------
O relatório de auditoria cruza o valor vendido com o custo exato do item.

Lucro Líquido = Receita Total - (Custo Mercadoria Vendida + Valor das Perdas)

* Se o lucro estiver negativo, significa que o Custo de Produção (Ingredientes + 
  Energia + Mão de Obra) está maior que o Preço de Venda.

------------------------------------------------------------------------------
6. CONFIGURAÇÕES GLOBAIS (TARIFAS ATUAIS)
------------------------------------------------------------------------------
Valores configurados no sistema (podem ser alterados na aba Máquinas):

- Energia: R$ 0,95 / kWh
- Gás: R$ 9,50 / kg
- Mão de Obra: R$ 18,00 / hora
- Água (Insumo 9000): R$ 0,02 / Litro

==============================================================================
Fim do Manual
==============================================================================
"""

try:
    with open("Manual_Regras.txt", "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("✅ Arquivo 'Manual_Regras.txt' gerado com sucesso na pasta do projeto!")
except Exception as e:
    print(f"❌ Erro ao gerar arquivo: {e}")