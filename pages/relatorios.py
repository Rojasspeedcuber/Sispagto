import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
from src.database import engine, get_session, Pagamento
from sqlalchemy import update

# Configuração da página
st.set_page_config(layout="wide", page_title="Relatórios")

# Título
st.header("Relatórios Gerais do Sistema")

# --- Funções de Carregamento de Dados ---
@st.cache_data(ttl=30)
def load_all_data():
    """Carrega todos os dados necessários para os relatórios."""
    data = {}
    try:
        # Relatório principal de Pagamentos
        query_pagamentos = """
        SELECT 
            p.PAGTO_ID, p.PAGTO_DATA AS "Data", p.PAGTO_PERIODO AS "Período",
            c.CREDOR_NOME AS "Credor", p.CONTRATO_N AS "Contrato",
            p.PAGTO_TIPO AS "Tipo de pagamento", p.PAGTO_VALOR AS "Valor"
        FROM PAGTO p
        LEFT JOIN CREDOR c ON p.CREDOR_DOC = c.CREDOR_DOC
        ORDER BY p.PAGTO_DATA DESC
        """
        data['pagamentos'] = pd.read_sql(query_pagamentos, engine, index_col="PAGTO_ID", parse_dates=['Data'])
        
        # Dados adicionais para relatórios secundários
        data['contratos'] = pd.read_sql("SELECT * FROM CONTRATO", engine, index_col='CONTRATO_N')
        data['credores'] = pd.read_sql("SELECT * FROM CREDOR", engine, index_col='CREDOR_DOC')
        data['produtos'] = pd.read_sql("SELECT * FROM PRODUTOS_SERVICOS", engine, index_col='PROD_SERV_N')

    except Exception as e:
        st.error(f"Erro ao carregar dados do banco: {e}.")
        # Retorna dataframes vazios em caso de erro
        data['pagamentos'] = pd.DataFrame()
        data['contratos'] = pd.DataFrame()
        data['credores'] = pd.DataFrame()
        data['produtos'] = pd.DataFrame()
        
    return data

# Carrega os dados
all_data = load_all_data()
df_pagamentos = all_data['pagamentos']
df_contratos = all_data['contratos']
df_credores = all_data['credores']
df_produtos = all_data['produtos']

# --- Relatório Principal de Pagamentos ---
st.subheader("Relatório de Pagamentos")
st.info("Utilize os filtros na barra lateral para refinar os resultados da tabela de pagamentos. A tabela é editável e as alterações podem ser salvas.")

if df_pagamentos.empty:
    st.warning("Nenhum dado de pagamento encontrado. Use a página 'Upload de Tabelas' para carregar os dados iniciais.")
else:
    st.sidebar.header("Filtros de Pagamentos")
    df_filtrado = df_pagamentos.copy()
    
    # --- Lógica de Filtros (em cascata) ---
    min_date = df_filtrado['Data'].min().date()
    max_date = df_filtrado['Data'].max().date()
    filtro_data = st.sidebar.date_input("Intervalo de Datas", value=(min_date, max_date), min_value=min_date, max_date=max_date, format="DD/MM/YYYY")
    if len(filtro_data) == 2:
        start_date, end_date = pd.to_datetime(filtro_data[0]), pd.to_datetime(filtro_data[1])
        df_filtrado = df_filtrado[df_filtrado['Data'].between(start_date, end_date)]

    credores_disponiveis = sorted(df_filtrado['Credor'].dropna().unique())
    filtro_credor = st.sidebar.multiselect("Credor", options=credores_disponiveis)
    if filtro_credor:
        df_filtrado = df_filtrado[df_filtrado['Credor'].isin(filtro_credor)]
    # ... (outros filtros podem ser adicionados aqui da mesma forma)

    # --- Exibição da Tabela de Pagamentos ---
    # APLICAÇÃO DO fillna() CONFORME SOLICITADO
    df_para_exibir = df_filtrado.fillna('-')
    
    st.data_editor(df_para_exibir, use_container_width=True, key="editor_pagamentos")

    # --- Lógica para Salvar Alterações na Tabela de Pagamentos ---
    if st.session_state.get('editor_pagamentos', {}).get('edited_rows'):
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

    # Métrica e Download
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
# --- Relatórios Adicionais ---
st.divider()
st.subheader("Outros Relatórios")

with st.expander("Visualizar Relatório de Contratos"):
    st.dataframe(df_contratos.fillna('-'), use_container_width=True)

with st.expander("Visualizar Relatório de Credores"):
    st.dataframe(df_credores.fillna('-'), use_container_width=True)

with st.expander("Visualizar Relatório de Produtos e Serviços"):
    st.dataframe(df_produtos.fillna('-'), use_container_width=True)