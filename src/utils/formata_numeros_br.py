# src/utils/formata_numeros_br.py

def formata_numeros_br(valor, moeda: bool = False) -> str:
    """
    Formata um valor numérico para o padrão brasileiro.
    
    Args:
        valor: Valor a ser formatado (int, float ou str).
        moeda: Se True, força 2 casas decimais (ex: 1.000,00).
               Se False, remove zeros decimais inúteis (ex: 1.000).
    """
    try:
        if valor is None or valor == "":
            return "0,00" if moeda else "0"

        # Garante que é float para formatar
        valor_float = float(str(valor).replace(",", "."))

        if moeda:
            # Padrão monetário: sempre 2 casas (1,234.50)
            texto = f"{valor_float:,.2f}"
        else:
            # Padrão quantidade: 3 casas de precisão inicial (1,234.500)
            texto = f"{valor_float:,.3f}"

        # Troca separadores US (,) e (.) para BR (.) e (,)
        # Ex: 1,234.50 -> 1.234,50
        texto_br = texto.replace(",", "X").replace(".", ",").replace("X", ".")

        if not moeda:
            # Remove zeros à direita e a vírgula se sobrar (ex: 10,500 -> 10,5 | 10,000 -> 10)
            if "," in texto_br:
                texto_br = texto_br.rstrip("0").rstrip(",")

        return texto_br

    except (ValueError, TypeError):
        return "0,00" if moeda else "0"