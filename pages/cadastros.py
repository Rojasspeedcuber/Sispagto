import streamlit as st
import pandas as pd
from datetime import datetime
from src.database import get_session, engine, Credor, Contrato, ProdutoServico, Pagamento

st.set_page_config(layout="wide", page_title="Cadastros")

st.header("Módulo de Cadastros e Edições")
st.info("Os dados cadastrados aqui são salvos diretamente no banco de dados permanente.")

# Função para carregar dados do BD, com cache para otimizar
@st.cache_data(ttl=60)
def carregar_dados_bd():
    data = {}
    with get_session() as session:
        data['credores'] = pd.read_sql("SELECT CREDOR_NOME, CREDOR_DOC FROM CREDOR ORDER BY CREDOR_NOME", engine)
        data['contratos'] = pd.read_sql("SELECT * FROM CONTRATO", engine)
        data['produtos_servicos'] = pd.read_sql("SELECT * FROM PRODUTOS_SERVICOS", engine)
    return data

db_data = carregar_dados_bd()
credores_df = db_data['credores']
contratos_df = db_data['contratos']
produtos_servicos_df = db_data['produtos_servicos']

tab_pagto, tab_contrato, tab_credor, tab_produto = st.tabs([
    "Pagamentos", "Contratos", "Credores", "Produtos/Serviços"
])

with tab_pagto:
    st.subheader("Cadastro de Pagamentos")
    with st.form("form_pagamento", clear_on_submit=True):
        data_pag = st.date_input("Data do pagamento (obrigatório)", format="DD/MM/YYYY")
        periodo = st.text_input("Período do pagamento (ex: jul/2025)", placeholder="jul/2025")
        valor = st.number_input("Valor do pagamento (obrigatório)", format="%.2f", step=10.0)
        
        map_credor_nome_doc = pd.Series(credores_df.CREDOR_DOC.values, index=credores_df.CREDOR_NOME).to_dict()
        credor_selecionado = st.selectbox("Credor (obrigatório)", options=list(map_credor_nome_doc.keys()), index=None)
        
        tipo_pagamento = st.selectbox("Tipo de pagamento", ["Nota Fiscal", "Recibo", "Fatura", "Boleto", "Outro"], index=None)
        
        submitted = st.form_submit_button("Cadastrar Pagamento")
        if submitted:
            if not all([data_pag, valor, credor_selecionado]):
                st.error("Preencha todos os campos obrigatórios!")
            else:
                try:
                    novo_pagamento = Pagamento(
                        PAGTO_DATA=data_pag, PAGTO_PERIODO=periodo, PAGTO_VALOR=valor,
                        CREDOR_DOC=map_credor_nome_doc[credor_selecionado], PAGTO_TIPO=tipo_pagamento
                    )
                    with get_session() as session:
                        session.add(novo_pagamento)
                        session.commit()
                    st.success(f"Pagamento para {credor_selecionado} registrado com sucesso!")
                    st.cache_data.clear() # Limpa o cache para recarregar os dados
                except Exception as e:
                    st.error(f"Erro ao cadastrar pagamento: {e}")

with tab_contrato:
    st.subheader("Cadastro de Contratos")
    # ... (formulário de contrato similar, lendo e salvando no BD)
    st.dataframe(contratos_df.fillna('-'), use_container_width=True)


with tab_credor:
    st.subheader("Cadastro de Credores")
    # ... (formulário de credor similar, lendo e salvando no BD)
    st.dataframe(credores_df.fillna('-'), use_container_width=True)

with tab_produto:
    st.subheader("Cadastro de Produtos/Serviços")
    # ... (formulário de produto similar, lendo e salvando no BD)
    st.dataframe(produtos_servicos_df.fillna('-'), use_container_width=True)