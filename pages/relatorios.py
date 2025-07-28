import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
from src.database import engine

st.set_page_config(layout="wide", page_title="Relatório de Pagamentos")

st.header("Relatório de Pagamentos")

@st.cache_data(ttl=60)
def load_data_from_db():
    try:
        query = """
        SELECT 
            p.PAGTO_ID,
            p.PAGTO_DATA AS "Data",
            p.PAGTO_PERIODO AS "Período",
            c.CREDOR_NOME AS "Credor",
            p.CONTRATO_N AS "Contrato",
            p.PAGTO_TIPO AS "Tipo de pagamento",
            p.PAGTO_VALOR AS "Valor"
        FROM PAGTO p
        LEFT JOIN CREDOR c ON p.CREDOR_DOC = c.CREDOR_DOC
        ORDER BY p.PAGTO_DATA DESC
        """
        df_report = pd.read_sql(query, engine, parse_dates=['Data'])
        return df_report
    except Exception as e:
        st.error(f"Erro ao carregar dados do banco: {e}. Verifique se os dados foram carregados na página de Upload.")
        return pd.DataFrame()

df_relatorio_base = load_data_from_db()

if df_relatorio_base.empty:
    st.warning("Nenhum dado de pagamento encontrado. Use a página 'Upload de Tabelas' para carregar os dados iniciais.")
else:
    st.sidebar.header("Filtros")
    df_filtrado = df_relatorio_base.copy()

    # --- Filtros em cascata ---
    credores_disponiveis = sorted(df_filtrado['Credor'].dropna().unique())
    filtro_credor = st.sidebar.multiselect("Credor", options=credores_disponiveis)
    if filtro_credor:
        df_filtrado = df_filtrado[df_filtrado['Credor'].isin(filtro_credor)]
    
    # ... outros filtros ...

    st.subheader("Planilha de Pagamentos")
    
    # Substituir NaN por hífen para exibição
    df_display = df_filtrado.fillna('-')

    if df_display.empty:
        st.warning("Nenhum pagamento encontrado para os filtros selecionados.")
    else:
        st.info("Clique duas vezes em uma célula para editar. As alterações são salvas automaticamente no banco de dados.")
        
        # Oculta o ID e o índice da tabela de edição
        edited_df = st.data_editor(
            df_display, 
            use_container_width=True, 
            key="data_editor",
            column_config={"PAGTO_ID": None}, # Oculta a coluna de ID
            hide_index=True
        )
        
        valor_total = pd.to_numeric(df_filtrado['Valor'], errors='coerce').sum()
        st.metric(label="**Valor Total dos Pagamentos Filtrados**", value=f"R$ {valor_total:,.2f}")
        
        # --- Lógica de Download ---
        output = BytesIO()
        # Salva o dataframe filtrado (com NaNs, não hífens) para o Excel
        df_filtrado.to_excel(output, index=False, sheet_name='Pagamentos')
        output.seek(0)
        
        st.download_button(
            label="📥 Exportar para Excel (XLSX)",
            data=output,
            file_name=f"relatorio_pagamentos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )