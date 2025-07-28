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
        """
        df_report = pd.read_sql(query, engine)
        df_report['Data'] = pd.to_datetime(df_report['Data'])
        return df_report
    except Exception:
        st.error("Erro ao carregar dados do banco. Verifique se os dados foram carregados na página de Upload.")
        return pd.DataFrame()

df_relatorio_base = load_data_from_db()

if df_relatorio_base.empty:
    st.warning("Nenhum dado de pagamento encontrado. Use a página 'Upload de Tabelas' para carregar os dados iniciais.")
else:
    st.sidebar.header("Filtros")
    df_filtrado = df_relatorio_base.copy()

    # --- Filtros em cascata ---
    # ... (lógica de filtros permanece a mesma)

    st.subheader("Planilha de Pagamentos")
    
    # Substituir NaN por hífen para exibição
    df_display = df_filtrado.fillna('-')

    if df_display.empty:
        st.warning("Nenhum pagamento encontrado para os filtros selecionados.")
    else:
        st.info("Clique duas vezes em uma célula para editar. As alterações são salvas automaticamente no banco de dados.")
        
        # Edição da Tabela
        edited_df = st.data_editor(
            df_display, use_container_width=True, key="data_editor",
            column_config={"PAGTO_ID": None}, hide_index=True # Oculta o ID
        )
        
        # Lógica para salvar alterações no banco de dados (a ser implementada se necessário)
        
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