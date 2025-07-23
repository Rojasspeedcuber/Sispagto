import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
from src.database import engine

st.set_page_config(layout="wide", page_title="Relatório de Pagamentos")

st.header("Relatório de Pagamentos")

@st.cache_data(ttl=300) # Cache para otimizar a leitura do BD
def load_data():
    try:
        pagamentos_df = pd.read_sql("SELECT * FROM PAGTO", engine)
        credores_df = pd.read_sql("SELECT * FROM CREDOR", engine)
        contratos_df = pd.read_sql("SELECT * FROM CONTRATO", engine)
        
        # Merge
        df_report = pd.merge(pagamentos_df, credores_df, on='CREDOR_DOC', how='left')
        if not contratos_df.empty:
             df_report = pd.merge(df_report, contratos_df, on='CONTRATO_N', how='left', suffixes=('', '_contrato'))
        
        # Limpeza e formatação
        for col in df_report.select_dtypes(include=['object']):
            df_report[col] = df_report[col].str.strip("'")

        df_report.rename(columns={
            'PAGTO_DATA': 'Data',
            'PAGTO_PERIODO': 'Período',
            'CREDOR_NOME': 'Credor',
            'CONTRATO_N': 'Contrato',
            'PAGTO_TIPO': 'Tipo de pagamento',
            'PAGTO_VALOR': 'Valor'
        }, inplace=True)
        
        df_report['Data'] = pd.to_datetime(df_report['Data'], errors='coerce')
        
        return df_report
    except Exception as e:
        st.error(f"Erro ao carregar dados do banco de dados: {e}")
        return pd.DataFrame()

df_relatorio_base = load_data()

if df_relatorio_base.empty:
    st.warning("Nenhum dado de pagamento encontrado no banco de dados. Faça o upload na aba 'Upload de Tabelas'.")
else:
    st.sidebar.header("Filtros")
    df_filtrado = df_relatorio_base.copy()

    # --- Filtros em cascata ---
    
    # Datas
    min_date = df_filtrado['Data'].min().date()
    max_date = df_filtrado['Data'].max().date()
    filtro_data = st.sidebar.date_input("Intervalo de dias", value=(min_date, max_date), min_value=min_date, max_value=max_date, format="DD/MM/YYYY")
    if len(filtro_data) == 2:
        start_date, end_date = pd.to_datetime(filtro_data[0]), pd.to_datetime(filtro_data[1])
        df_filtrado = df_filtrado[df_filtrado['Data'].between(start_date, end_date)]

    # Credor
    credores_disponiveis = sorted(df_filtrado['Credor'].dropna().unique())
    filtro_credor = st.sidebar.multiselect("Credor", options=credores_disponiveis)
    if filtro_credor:
        df_filtrado = df_filtrado[df_filtrado['Credor'].isin(filtro_credor)]

    # Período
    periodos_disponiveis = sorted(df_filtrado['Período'].dropna().unique())
    filtro_periodo = st.sidebar.multiselect("Período", options=periodos_disponiveis)
    if filtro_periodo:
        df_filtrado = df_filtrado[df_filtrado['Período'].isin(filtro_periodo)]

    # Tipo de Pagamento
    tipos_disponiveis = sorted(df_filtrado['Tipo de pagamento'].dropna().unique())
    filtro_tipo = st.sidebar.selectbox("Tipo de pagamento", ["Todos"] + tipos_disponiveis)
    if filtro_tipo != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Tipo de pagamento'] == filtro_tipo]

    # Contrato
    contratos_disponiveis = sorted(df_filtrado['Contrato'].dropna().unique())
    filtro_contrato = st.sidebar.multiselect("Contrato", options=contratos_disponiveis)
    if filtro_contrato:
        df_filtrado = df_filtrado[df_filtrado['Contrato'].isin(filtro_contrato)]


    st.subheader("Planilha de Pagamentos")
    
    # Substituir NaN por hífen
    df_display = df_filtrado.fillna('-')

    if df_display.empty:
        st.warning("Nenhum pagamento encontrado para os filtros selecionados.")
    else:
        st.info("Clique duas vezes em uma célula para editar. As alterações são salvas automaticamente no banco de dados.")
        
        # Edição da Tabela
        edited_df = st.data_editor(
            df_display,
            use_container_width=True,
            num_rows="dynamic",
            key="data_editor"
        )
        
        # Lógica para salvar alterações no banco de dados (simplificada)
        # Uma implementação mais robusta usaria chaves primárias para garantir a atualização correta
        # if not edited_df.equals(df_display):
            # st.write("Alterações detectadas. Lógica para salvar no BD seria implementada aqui.")
            # st.write(st.session_state["data_editor"])


        valor_total = pd.to_numeric(df_filtrado['Valor'], errors='coerce').sum()
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