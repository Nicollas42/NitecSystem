# gerar_release_notes.py
import os

# Conteúdo formatado em Markdown para o GitHub
conteudo_github = """
# 🏭 NitecSystem v4.0 - Atualização Industrial

**Título do Commit Sugerido:**
`feat(v4): Implementação de Custeio Industrial, Modularização de Abas e Correções Críticas`

---

## 📝 Descrição Detalhada

Este commit eleva o sistema para a versão **v4.0 (Industrial)**, introduzindo lógica avançada de precificação (Custeio por Absorção), refatoração completa da arquitetura de views e correções de estabilidade crítica.

### ✨ Novas Funcionalidades (Engenharia de Produto)
- **Custeio Industrial Avançado:** Implementação do cálculo de custo por absorção. O custo do produto agora é composto por:
  - 🧱 **Matéria Prima:** Soma dos insumos.
  - 👨‍🍳 **Mão de Obra Direta (MOD):** Baseada no tempo de preparo e tarifa horária.
  - ⚡ **Custos Indiretos (CIF):** Energia Elétrica e Gás baseados na potência das máquinas utilizadas.
- **Gestão de Máquinas e Tarifas:** Novo suporte no `EstoqueController` para cadastrar máquinas (Watts/Consumo Gás) e definir tarifas globais (kWh, kg Gás).
- **Água na Ficha Técnica:** Lógica para inclusão de água como insumo (Item 9000) para composição correta de peso/rendimento, com custo parametrizável.

### ♻️ Refatoração e Modularização
- **Aba Receitas (`aba_receitas.py`):** Código monolítico dividido em sub-módulos para facilitar manutenção:
  - `tab_ingredientes.py`: Gestão da lista de insumos.
  - `tab_maquinas.py`: Seleção de equipamentos e tempos.
  - `tab_financeiro.py`: Resumo de custos, markup e precificação.
- **Aba Cadastro (`aba_cadastro.py`):** Separação dos formulários em classes distintas (`FormRevenda`, `FormInsumo`, `FormInterno`) para interfaces mais limpas e dinâmicas.

### 🐛 Correções de Bugs (Fixes)
- **Produção Diária:** Corrigido `KeyError: 'nome'` ao carregar ingredientes na aba de produção. Implementado *fallback* robusto para buscar dados no cadastro caso não existam na receita salva.
- **Edição de Receitas:** Corrigido erro de tipagem de ID (`int` vs `str`) que impedia o carregamento dos dados ao clicar na árvore de produtos.
- **Histórico:** Corrigido `AttributeError` em ordenação/filtros quando campos (motivo/usuário) eram nulos no banco legado.
- **Busca de Insumos:** Corrigido bug onde produtos de revenda apareciam na busca de ingredientes (agora restrito apenas ao tipo `INSUMO`).

### 💅 Melhorias de Interface (UI/UX)
- **Tabelas:** Adicionada coluna **"Unidade"** na tabela de ingredientes da Ficha Técnica.
- **Usabilidade:** Implementada funcionalidade de **"Clicar para Editar"** na lista de ingredientes (antes era necessário remover e adicionar novamente).
- **Feedback:** Adicionado recálculo visual em tempo real na aba de precificação ao alterar parâmetros.

### ⚙️ Scripts e Configuração
- **Setup v4:** Adicionado script `setup_v4_industrial_final.py` para resetar o banco, criar dados iniciais (água, máquinas, tarifas) e simular um cenário de auditoria completo.
- **Documentação:** Adicionado script `gerar_manual.py` para criar documentação automática das regras de negócio em arquivo de texto.

---
*Gerado automaticamente via Script de Release.*
"""

try:
    with open("RELEASE_NOTES.md", "w", encoding="utf-8") as f:
        f.write(conteudo_github.strip())
    print("✅ Arquivo 'RELEASE_NOTES.md' gerado com sucesso!")
    print("👉 Abra o arquivo, copie o conteúdo e cole no GitHub (ele já está com a formatação de negritos e títulos).")
except Exception as e:
    print(f"❌ Erro ao gerar arquivo: {e}")