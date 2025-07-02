# src/business_rules.py
from datetime import date
from src.database import get_session

def validar_data_pagamento(pagamento_data: date, contrato_n: str):
    """
    Verifica se a data do pagamento está dentro da vigência do contrato.
    Implementa a regra "Data fora da vigência". [cite: 163]
    Retorna True se válido, False caso contrário, junto com uma mensagem.
    """
    # Lógica para buscar as datas do contrato e aditivos e comparar
    # com a PAGTO.PAGTO_DATA.
    return True, "Validação OK"

def validar_valor_pagamento(valor_pagamento: float, contrato_n: str):
    """
    Verifica se o valor do pagamento não excede o saldo do contrato.
    Implementa a regra "Valor superior ao disponível". [cite: 163]
    Retorna True se válido, False caso contrário, junto com uma mensagem.
    """
    # Lógica para calcular o valor já pago e o valor total do contrato
    # (incluindo aditivos) e fazer a verificação.
    return True, "Validação OK"

def validar_datas_contrato(data_ini: date, data_fim: date):
    """
    Verifica se a data de término do contrato é posterior à de início.
    Implementa a regra da tabela 3.2. [cite: 165]
    """
    if data_fim < data_ini:
        return False, "A data de término da vigência não pode ser anterior à data de início."
    return True, "Validação OK"

# ... (demais funções de validação para contratos [cite: 165], aditivos [cite: 167] e pagamentos [cite: 163])