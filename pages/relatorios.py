import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
from src.database import engine, get_session, Pagamento
from sqlalchemy import update

st.set_page_config(layout="wide", page_title="Relatório de Pagamentos")

st.header("Relatório de Pagamentos")
st.info("A tabela abaixo é editável. Clique em uma célula para alterar seu valor e use o botão 'Salvar Alterações' para gravar as mudanças.")

@st.cache_data(ttl=30)
def load_data_from_db():
    try:
        query = """
        SELECT 
            p.PAGTO_ID, p.PAGTO_DATA AS "Data", p.PAGTO_PERIODO AS "Período",
            c.CREDOR_NOME AS "Credor", p.CONTRATO_N AS "Contrato",
            p.PAGTO_TIPO AS "Tipo de pagamento", p.PAGTO_VALOR AS "Valor"
        FROM PAGTO p
        LEFT JOIN CREDOR c ON p.CREDOR_DOC = c.CREDOR_DOC
        ORDER BY p.PAGTO_DATA DESC
        """
        df_report = pd.read_sql(query, engine, index_col="PAGTO_ID", parse_dates=['Data'])
        return df_report
    except Exception as e:
        st.error(f"Erro ao carregar dados do banco: {e}.")
        return pd.DataFrame()

df_relatorio_original = load_data_from_db()

if df_relatorio_original.empty:
    st.warning("Nenhum dado de pagamento encontrado.")
else:
    st.sidebar.header("Filtros")
    df_filtrado = df_relatorio_original.copy()
    
    # 1. Filtro de Data
    min_date = df_filtrado['Data'].min().date()
    max_date = df_filtrado['Data'].max().date()
    filtro_data = st.sidebar.date_input(
        "Intervalo de Datas",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        format="DD/MM/YYYY"
    )
    if len(filtro_data) == 2:
        start_date, end_date = pd.to_datetime(filtro_data[0]), pd.to_datetime(filtro_data[1])
        df_filtrado = df_filtrado[df_filtrado['Data'].between(start_date, end_date)]

    # 2. Filtro de Credor (opções baseadas no filtro de data)
    credores_disponiveis = sorted(df_filtrado['Credor'].dropna().unique())
    filtro_credor = st.sidebar.multiselect("Credor", options=credores_disponiveis)
    if filtro_credor:
        df_filtrado = df_filtrado[df_filtrado['Credor'].isin(filtro_credor)]

    # 3. Filtro de Período (opções baseadas nos filtros anteriores)
    periodos_disponiveis = sorted(df_filtrado['Período'].dropna().unique())
    filtro_periodo = st.sidebar.multiselect("Período", options=periodos_disponiveis)
    if filtro_periodo:
        df_filtrado = df_filtrado[df_filtrado['Período'].isin(filtro_periodo)]

    # 4. Filtro de Tipo de Pagamento (opções baseadas nos filtros anteriores)
    tipos_disponiveis = sorted(df_filtrado['Tipo de pagamento'].dropna().unique())
    filtro_tipo = st.sidebar.multiselect("Tipo de pagamento", options=tipos_disponiveis)
    if filtro_tipo:
        df_filtrado = df_filtrado[df_filtrado['Tipo de pagamento'].isin(filtro_tipo)]
        
    # 5. Filtro de Contrato (opções baseadas nos filtros anteriores)
    contratos_disponiveis = sorted(df_filtrado['Contrato'].dropna().unique())
    filtro_contrato = st.sidebar.multiselect("Contrato", options=contratos_disponiveis)
    if filtro_contrato:
        df_filtrado = df_filtrado[df_filtrado['Contrato'].isin(filtro_contrato)]
    st.subheader("Planilha de Pagamentos")
    
    df_para_editar = df_filtrado.copy()
    st.subheader("Planilha de Pagamentos")
    
    # Tabela de dados editável
    st.data_editor(
        df_filtrado.fillna('-'),
        use_container_width=True,
        key="editor_pagamentos"
    )

    # Lógica para salvar alterações
    if st.session_state.editor_pagamentos['edited_rows']:
        st.warning("Você fez alterações na tabela. Clique no botão abaixo para salvá-las.")
        if st.button("Salvar Alterações nos Pagamentos", type="primary"):
            try:
                with get_session() as session:
                    # Itera sobre as linhas editadas no dicionário do Streamlit
                    for row_index, changes in st.session_state.editor_pagamentos['edited_rows'].items():
                        pagto_id = df_filtrado.index[row_index] # Obtém o PAGTO_ID real
                        
                        # Renomeia as chaves do dicionário para corresponder às colunas do BD
                        db_changes = {}
                        for col_name, value in changes.items():
                            if col_name == 'Data': db_changes['PAGTO_DATA'] = value
                            elif col_name == 'Período': db_changes['PAGTO_PERIODO'] = value
                            elif col_name == 'Contrato': db_changes['CONTRATO_N'] = value
                            elif col_name == 'Tipo de pagamento': db_changes['PAGTO_TIPO'] = value
                            elif col_name == 'Valor': db_changes['PAGTO_VALOR'] = value
                        
                        if db_changes:
                            stmt = update(Pagamento).where(Pagamento.PAGTO_ID == int(pagto_id)).values(**db_changes)
                            session.execute(stmt)
                            
                    session.commit()
                st.success("Alterações nos pagamentos salvas com sucesso!")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar alterações: {e}")

    # --- Métrica e Download ---
    valor_total = pd.to_numeric(df_filtrado['Valor'], errors='coerce').sum()
    st.metric(label="**Valor Total dos Pagamentos Filtrados**", value=f"R$ {valor_total:,.2f}")
    
    output = BytesIO()
    df_filtrado.to_excel(output, index=False, sheet_name='Pagamentos')
    output.seek(0)
        
    st.download_button(
        label="📥 Exportar para Excel (XLSX)",
        data=output,
        file_name=f"relatorio_pagamentos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )