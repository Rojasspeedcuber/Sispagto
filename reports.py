# reports.py

import pandas as pd
from sqlalchemy.orm import Session
from models import Pagto, Credor, Contrato, ProdutosServicos

def generate_report(db: Session, data_inicio: str = None, data_fim: str = None, periodo: str = None,
                    credor_doc: str = None, contrato_n: str = None, tipo_pagamento: str = None):
    """
    Generates a payment report based on filters and exports it to an Excel file.
    """
    query = db.query(
        Pagto.pagto_data,
        Pagto.pagto_periodo,
        Credor.credor_nome,
        Pagto.contrato_n,
        Pagto.pagto_grupo,
        Pagto.nf_n,
        Pagto.recibo_n,
        Pagto.fatura_n,
        Pagto.boleto_n,
        ProdutosServicos.prod_serv_descricao,
        Pagto.prod_serv_qtd,
        Pagto.pagto_valor
    ).join(Credor, Pagto.credor_doc == Credor.credor_doc)\
     .join(ProdutosServicos, Pagto.prod_serv_n == ProdutosServicos.prod_serv_n)\
     .outerjoin(Contrato, Pagto.contrato_n == Contrato.contrato_n)

    # Apply filters
    if data_inicio:
        query = query.filter(Pagto.pagto_data >= data_inicio)
    if data_fim:
        query = query.filter(Pagto.pagto_data <= data_fim)
    if periodo:
        query = query.filter(Pagto.pagto_periodo == periodo)
    if credor_doc:
        query = query.filter(Pagto.credor_doc == credor_doc)
    if contrato_n:
        query = query.filter(Pagto.contrato_n == contrato_n)

    results = query.all()

    # Formatting data into a list of dictionaries for pandas
    data_for_df = []
    for row in results:
        # Determine Tipo de Pagamento
        tipo = ""
        if row.nf_n: tipo = "NF"
        elif row.recibo_n: tipo = "Recibo"
        elif row.fatura_n: tipo = "Fatura"
        elif row.boleto_n: tipo = "Boleto"

        data_for_df.append({
            "Data": row.pagto_data,
            "Período": row.pagto_periodo,
            "Credor": row.credor_nome,
            "Contrato": row.contrato_n,
            "Grupo": row.pagto_grupo,
            "Tipo de pagamento": tipo,
            "Produto/Serviço": row.prod_serv_descricao,
            "Quantidade": row.prod_serv_qtd,
            # ALTERAÇÃO: Converte o valor de centavos para Reais (float)
            "Valor": row.pagto_valor / 100.0
        })

    df = pd.DataFrame(data_for_df)

    # Add total row at the bottom
    if not df.empty:
        total_valor = df['Valor'].sum()
        # Create a total row with appropriate data types and columns
        total_row_data = {col: '' for col in df.columns}
        total_row_data['Valor'] = total_valor
        total_row_data['Quantidade'] = 'Total:'
        total_row = pd.DataFrame([total_row_data])
        df = pd.concat([df, total_row], ignore_index=True)


    # Export to Excel
    file_path = "relatorio_pagamentos.xlsx"
    # ALTERAÇÃO: Formata a coluna Valor como moeda no Excel
    if not df.empty:
        writer = pd.ExcelWriter(file_path, engine='openpyxl')
        df.to_excel(writer, index=False, sheet_name='Relatório')
        workbook = writer.book
        worksheet = writer.sheets['Relatório']
        # Define o formato de moeda
        money_format = '_-R$* #,##0.00_-;-R$* #,##0.00_-;_-"-"??_-;_-@_-'
        # Encontra a coluna "Valor" (letra)
        for col in worksheet.columns:
            if col[0].value == 'Valor':
                col_letter = col[0].column_letter
                for cell in worksheet[col_letter]:
                    if cell.row > 1: # Pula o cabeçalho
                        cell.number_format = money_format
                break
        writer.close()
    else:
         df.to_excel(file_path, index=False, engine='openpyxl')


    return file_path