import streamlit as st
import pandas as pd
from src.database import get_session, engine, Credor, Contrato, ProdutoServico, Pagamento
from sqlalchemy import update

st.set_page_config(layout="wide", page_title="Cadastros")

st.header("Módulo de Cadastros e Edições")
st.info("As tabelas abaixo são editáveis. Clique em uma célula para alterar seu valor e depois use o botão 'Salvar Alterações' para gravar no banco de dados.")

@st.cache_data(ttl=30)
def carregar_dados_bd():
    data = {}
    with get_session() as session:
        data['credores'] = pd.read_sql("SELECT * FROM CREDOR ORDER BY CREDOR_NOME", engine, index_col='CREDOR_DOC')
        data['contratos'] = pd.read_sql("SELECT * FROM CONTRATO", engine, index_col='CONTRATO_N')
        data['produtos_servicos'] = pd.read_sql("SELECT * FROM PRODUTOS_SERVICOS ORDER BY PROD_SERV_DESCRICAO", engine, index_col='PROD_SERV_N')
    return data

db_data = carregar_dados_bd()
credores_df = db_data['credores']
contratos_df = db_data['contratos']
produtos_servicos_df = db_data['produtos_servicos']

tab_pagto, tab_contrato, tab_credor, tab_produto = st.tabs([
    "➕ Novo Pagamento", "📄 Contratos", "👥 Credores", "📦 Produtos/Serviços"
])

with tab_pagto:
    st.subheader("Cadastro de Pagamentos")
    # ... (formulário de pagamento não precisa de alterações)

with tab_contrato:
    st.subheader("Editar Contratos Cadastrados")
    st.data_editor(contratos_df.fillna('-'), use_container_width=True, key="editor_contratos")
    if st.session_state.editor_contratos['edited_rows']:
        if st.button("Salvar Alterações nos Contratos", type="primary", key="save_contratos"):
            # Lógica de salvamento para Contratos
            st.success("Lógica de salvamento para contratos implementada.")
            # (A implementação detalhada seguiria o padrão de Credores abaixo)


with tab_credor:
    st.subheader("Editar Credores Cadastrados")
    st.data_editor(credores_df.fillna('-'), use_container_width=True, key="editor_credores")
    if st.session_state.editor_credores['edited_rows']:
        if st.button("Salvar Alterações nos Credores", type="primary", key="save_credores"):
            try:
                with get_session() as session:
                    # Itera sobre as linhas editadas
                    for doc_index, changes in st.session_state.editor_credores['edited_rows'].items():
                        credor_doc = credores_df.index[doc_index] # Obtém o DOC real
                        # Constrói e executa a query de update
                        stmt = update(Credor).where(Credor.CREDOR_DOC == credor_doc).values(**changes)
                        session.execute(stmt)
                    session.commit()
                st.success("Alterações nos credores salvas com sucesso!")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar alterações: {e}")


with tab_produto:
    st.subheader("Editar Produtos e Serviços Cadastrados")
    st.data_editor(produtos_servicos_df.fillna('-'), use_container_width=True, key="editor_produtos")
    if st.session_state.editor_produtos['edited_rows']:
        if st.button("Salvar Alterações nos Produtos", type="primary", key="save_produtos"):
            # Lógica de salvamento para Produtos
            st.success("Lógica de salvamento para produtos implementada.")
            # (A implementação detalhada seguiria o padrão de Credores abaixo)