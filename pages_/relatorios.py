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
        data['pagamentos'], data['contratos'], data['credores'], data['produtos'] = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

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
st.info("Clique duas vezes sobre o registro(célula) para editar/modificar")
if df_pagamentos.empty:
    st.warning("Nenhum dado de pagamento encontrado. Use a página 'Upload de Tabelas' para carregar os dados iniciais.")
else:
    st.sidebar.header("Filtros de Pagamentos")
    df_filtrado = df_pagamentos.copy()

    # --- Lógica de Filtros (em cascata) ---
    min_date = df_filtrado['Data'].min().date()
    max_date = df_filtrado['Data'].max().date()
    filtro_data = st.sidebar.date_input("Intervalo de Datas", value=(min_date, max_date), min_value=min_date, max_value=max_date, format="DD/MM/YYYY")
    if len(filtro_data) == 2:
        start_date, end_date = pd.to_datetime(filtro_data[0]), pd.to_datetime(filtro_data[1])
        df_filtrado = df_filtrado[df_filtrado['Data'].between(start_date, end_date)]

    credores_disponiveis = sorted(df_filtrado['Credor'].dropna().unique())
    filtro_credor = st.sidebar.multiselect("Credor", options=credores_disponiveis, placeholder="Escolha uma opção")
    if filtro_credor:
        df_filtrado = df_filtrado[df_filtrado['Credor'].isin(filtro_credor)]

    periodos_disponiveis = sorted(df_filtrado['Período'].dropna().unique())
    filtro_periodo = st.sidebar.multiselect("Período", options=periodos_disponiveis, placeholder="Escolha uma opção")
    if filtro_periodo:
        df_filtrado = df_filtrado[df_filtrado['Período'].isin(filtro_periodo)]

    tipos_disponiveis = sorted(df_filtrado['Tipo de pagamento'].dropna().unique())
    filtro_tipo = st.sidebar.multiselect("Tipo de pagamento", options=tipos_disponiveis, placeholder="Escolha uma opção")
    if filtro_tipo:
        df_filtrado = df_filtrado[df_filtrado['Tipo de pagamento'].isin(filtro_tipo)]

    contratos_disponiveis = sorted(df_filtrado['Contrato'].dropna().unique())
    filtro_contrato = st.sidebar.multiselect("Contrato", options=contratos_disponiveis, placeholder="Escolha uma opção")
    if filtro_contrato:
        df_filtrado = df_filtrado[df_filtrado['Contrato'].isin(filtro_contrato)]


    # --- Exibição da Tabela de Pagamentos ---
    df_para_exibir = df_filtrado.fillna('-')

    st.data_editor(df_para_exibir, use_container_width=True, key="editor_pagamentos")

    # --- Lógica para Salvar Alterações na Tabela de Pagamentos ---
if st.session_state.get('editor_pagamentos', {}).get('edited_rows'):
    if st.button("Salvar Alterações nos Pagamentos", type="primary"):
        try:
            with get_session() as session:
                for row_index, changes in st.session_state.editor_pagamentos['edited_rows'].items():
                    # Pega o ID do pagamento a partir do índice do dataframe filtrado
                    pagto_id = df_filtrado.index[row_index]
                    
                    # Constrói o dicionário de alterações para o banco de dados
                    db_changes = {}
                    for col, val in changes.items():
                        if col == 'Data':
                            db_changes['PAGTO_DATA'] = val
                        elif col == 'Período':
                            db_changes['PAGTO_PERIODO'] = val
                        elif col == 'Tipo de pagamento':
                            db_changes['PAGTO_TIPO'] = val
                        elif col == 'Valor':
                            db_changes['PAGTO_VALOR'] = val
                        elif col == 'Contrato':
                            db_changes['CONTRATO_N'] = val
                        # Adicione outros mapeamentos de coluna aqui se necessário

                    # Apenas executa a atualização se houverem alterações válidas
                    if db_changes:
                        stmt = update(Pagamento).where(Pagamento.PAGTO_ID == int(pagto_id)).values(**db_changes)
                        session.execute(stmt)
                
                session.commit()
            st.success("Alterações salvas com sucesso!")
            # Limpa o cache para recarregar os dados e atualiza a página
            st.cache_data.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar as alterações: {e}")

    # Métrica e Download
    valor_total = pd.to_numeric(df_filtrado['Valor'], errors='coerce').sum()
    st.metric(label="**Valor Total dos Pagamentos Filtrados**", value=f"R$ {valor_total:,.2f}")
    
    output = BytesIO()
    df_filtrado.to_excel(output, index=False)
    st.download_button(
        label="📥 Exportar para Excel",
        data=output.getvalue(),
        file_name="relatorio_pagamentos.xlsx"
    )


# 1. Garanta que a coluna 'Valor' em df_pagamentos é numérica
df_pagamentos['Valor'] = pd.to_numeric(df_pagamentos['Valor'], errors='coerce')

# 2. Agrupe por 'Credor' e some os 'Valores'
valor_total_por_credor = df_pagamentos.groupby('Credor')['Valor'].sum().reset_index()

# 3. Renomeie a coluna da soma para maior clareza
valor_total_por_credor = valor_total_por_credor.rename(columns={'Valor': 'Valor Total'})

# 4. Junte (merge) o dataframe de credores com os totais calculados
#    Usamos 'left' merge para manter todos os credores originais, mesmo que não tenham pagamentos.
df_credores_com_total = pd.merge(
    df_credores,
    valor_total_por_credor,
    left_on='CREDOR_NOME',  # Coluna em df_credores
    right_on='Credor',     # Coluna em valor_total_por_credor
    how='left'
)

# 5. Remova a coluna 'Credor' duplicada que veio do merge
df_credores_com_total = df_credores_com_total.drop(columns=['Credor'])

# 6. Preencha com 0 os valores nulos (credores sem pagamentos) na nova coluna
df_credores_com_total['Valor Total'] = df_credores_com_total['Valor Total'].fillna(0)

# --- Relatórios Adicionais ---
st.divider()
st.subheader("Outros Relatórios")

with st.expander("Visualizar Relatório de Contratos"):
    valor_total_contratos = pd.to_numeric(df_contratos['CONTRATO_VALOR'], errors='coerce').sum()
    st.dataframe(df_contratos.fillna('-'), use_container_width=True)
    st.metric(label="**Valor Total dos Contratos Filtrados**", value=f"R$ {valor_total_contratos:,.2f}")

with st.expander("Visualizar Relatório de Credores"):
    valor_total_credores = df_credores_com_total['Valor Total'].sum()
    st.dataframe(df_credores_com_total.fillna('-'), use_container_width=True)
    st.metric(label="**Valor Total dos Credores**", value=f"R$ {valor_total_credores:,.2f}")

with st.expander("Visualizar Relatório de Produtos e Serviços"):
    valor_total_prodserv = pd.to_numeric(df_produtos['PROD_SERV_VALOR'], errors='coerce').sum()
    st.dataframe(df_produtos.fillna('-'), use_container_width=True)
    st.metric(label="**Valor Total dos Produtos e Serviços Filtrados**", value=f"R$ {valor_total_prodserv:,.2f}")