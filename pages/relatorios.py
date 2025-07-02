import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

st.set_page_config(layout="wide", page_title="Relatório de Pagamentos")

st.header("Relatório de Pagamentos")

# --- FUNÇÃO PARA CONSTRUIR O RELATÓRIO ---
def build_report_dataframe():
    """
    Verifica se os DataFrames necessários estão na sessão, os une (merge)
    e retorna o DataFrame final para o relatório.
    """
    required_keys = ['pagamentos_df', 'credores_df', 'produtos_servicos_df']
    for key in required_keys:
        if key not in st.session_state or st.session_state[key].empty:
            return None, f"A tabela '{key.replace('_df', '').upper()}' ainda não foi carregada."

    # Inicia com a tabela principal de pagamentos
    df_report = st.session_state['pagamentos_df'].copy()

    # Converte colunas de data
    df_report['PAGTO_DATA'] = pd.to_datetime(df_report['PAGTO_DATA'], dayfirst=True, errors='coerce')
    
    # ===== INÍCIO DA CORREÇÃO =====
    # Limpa e converte a coluna de valor para numérico antes de qualquer merge.
    # Isso resolve o erro de formatação se o CSV tiver valores como "1.250,50".
    if 'PAGTO_VALOR' in df_report.columns:
        df_report['PAGTO_VALOR'] = (
            df_report['PAGTO_VALOR'].astype(str)
            .str.replace('.', '', regex=False)      # Remove o separador de milhar
            .str.replace(',', '.', regex=False)      # Substitui a vírgula do decimal por ponto
            .astype(float)                           # Converte a string limpa para float
        )
    # ===== FIM DA CORREÇÃO =====

    # Junta com a tabela de credores
    credores_df = st.session_state['credores_df']
    df_report = pd.merge(df_report, credores_df, on='CREDOR_DOC', how='left')

    # Junta com a tabela de produtos/serviços
    produtos_df = st.session_state['produtos_servicos_df']
    df_report = pd.merge(df_report, produtos_df, on='PROD_SERV_N', how='left')
    
    # Junta com a tabela de contratos (se existir)
    if 'contratos_df' in st.session_state and not st.session_state['contratos_df'].empty:
        contratos_df = st.session_state['contratos_df']
        # Converte a chave em ambos os dataframes para string para garantir o merge
        df_report['CONTRATO_N'] = df_report['CONTRATO_N'].astype(str)
        contratos_df['CONTRATO_N'] = contratos_df['CONTRATO_N'].astype(str)
        df_report = pd.merge(df_report, contratos_df, on='CONTRATO_N', how='left', suffixes=('', '_contrato'))

    # Renomeia e seleciona as colunas conforme especificação do PDF
    df_report.rename(columns={
        'PAGTO_DATA': 'Data',
        'PAGTO_PERIODO': 'Período',
        'CREDOR_NOME': 'Credor',
        'CONTRATO_N': 'Contrato',
        'PAGTO_GRUPO': 'Grupo',
        'PROD_SERV_DESCRICAO': 'Produto/Serviço',
        'PROD_SERV_QTD': 'Quantidade',
        'PAGTO_VALOR': 'Valor'
    }, inplace=True)
    
    # Cria a coluna "Tipo de pagamento"
    def get_tipo_pagamento(row):
        if pd.notna(row.get('NF_N')): return 'NF'
        if pd.notna(row.get('RECIBO_N')): return 'Recibo'
        if pd.notna(row.get('FATURA_N')): return 'Fatura'
        if pd.notna(row.get('BOLETO_N')): return 'Boleto'
        return 'N/A'
    df_report['Tipo de pagamento'] = df_report.apply(get_tipo_pagamento, axis=1)

    # Define a ordem final das colunas
    final_columns = [
        'Data', 'Período', 'Credor', 'Contrato', 'Grupo',
        'Tipo de pagamento', 'Produto/Serviço', 'Quantidade', 'Valor'
    ]
    
    # Filtra para manter apenas as colunas existentes no DataFrame
    final_columns_exist = [col for col in final_columns if col in df_report.columns]
    
    return df_report[final_columns_exist], None


# --- LÓGICA PRINCIPAL DA PÁGINA ---
df_relatorio_base, error_message = build_report_dataframe()

if error_message:
    st.error(f"**Erro ao gerar relatório:** {error_message}")
    st.info("Por favor, vá para a aba '⬆️ Upload de Tabelas' para carregar os dados necessários.")
else:
    # --- BARRA LATERAL DE FILTROS ---
    st.sidebar.header("Filtros")

    # Opções de filtros são carregadas dinamicamente a partir dos dados
    lista_credores = sorted(df_relatorio_base['Credor'].dropna().unique())
    
    filtro_credor = st.sidebar.multiselect("Credor", options=lista_credores)
    filtro_contrato = st.sidebar.text_input("Contrato (busca por parte do número)")
    filtro_tipo = st.sidebar.selectbox("Tipo de pagamento", ["Todos"] + sorted(df_relatorio_base['Tipo de pagamento'].unique()))
    
    # Remove NaT (Not a Time) para evitar erros nos seletores de data
    df_relatorio_base.dropna(subset=['Data'], inplace=True)
    
    min_date = df_relatorio_base['Data'].min().date()
    max_date = df_relatorio_base['Data'].max().date()

    filtro_data = st.sidebar.date_input(
        "Intervalo de dias",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # --- APLICAÇÃO DOS FILTROS ---
    df_filtrado = df_relatorio_base.copy()

    if filtro_data and len(filtro_data) == 2:
        start_date, end_date = pd.to_datetime(filtro_data[0]), pd.to_datetime(filtro_data[1])
        df_filtrado = df_filtrado[(df_filtrado['Data'] >= start_date) & (df_filtrado['Data'] <= end_date)]
    if filtro_credor:
        df_filtrado = df_filtrado[df_filtrado['Credor'].isin(filtro_credor)]
    if filtro_contrato:
        df_filtrado = df_filtrado[df_filtrado['Contrato'].astype(str).str.contains(filtro_contrato, case=False, na=False)]
    if filtro_tipo != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Tipo de pagamento'] == filtro_tipo]

    # --- EXIBIÇÃO DO RELATÓRIO ---
    st.subheader("Planilha de Pagamentos")

    if df_filtrado.empty:
        st.warning("Nenhum pagamento encontrado para os filtros selecionados.")
    else:
        # A formatação agora funcionará, pois a coluna 'Valor' é numérica.
        st.dataframe(df_filtrado.style.format({"Valor": "R$ {:,.2f}"}), use_container_width=True)

        valor_total = df_filtrado['Valor'].sum()
        st.metric(label="**Valor Total dos Pagamentos Filtrados**", value=f"R$ {valor_total:,.2f}")
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_filtrado.to_excel(writer, index=False, sheet_name='Pagamentos')
        
        st.download_button(
            label="📥 Exportar para Excel (XLS)",
            data=output.getvalue(),
            file_name=f"relatorio_pagamentos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
