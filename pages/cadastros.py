import streamlit as st
import pandas as pd
from datetime import datetime
from src.database import get_session, engine, Credor, Contrato, ProdutoServico, Pagamento

st.set_page_config(layout="wide", page_title="Cadastros")

st.header("Módulo de Cadastros e Edições")

def carregar_dados_bd():
    try:
        st.session_state['credores_df'] = pd.read_sql("SELECT * FROM CREDOR", engine)
    except:
        st.session_state['credores_df'] = pd.DataFrame(columns=['CREDOR_DOC', 'CREDOR_NOME'])
        
    try:
        st.session_state['produtos_servicos_df'] = pd.read_sql("SELECT * FROM PRODUTOS_SERVICOS", engine)
    except:
        st.session_state['produtos_servicos_df'] = pd.DataFrame(columns=['PROD_SERV_N', 'PROD_SERV_DESCRICAO', 'PROD_SERV_VALOR'])

    try:
        st.session_state['contratos_df'] = pd.read_sql("SELECT * FROM CONTRATO", engine)
    except:
        st.session_state['contratos_df'] = pd.DataFrame(columns=['CONTRATO_N', 'CREDOR_DOC', 'CONTRATO_DATA_INI', 'CONTRATO_DATA_FIM', 'CONTRATO_VALOR'])

# Carrega os dados no início
carregar_dados_bd()

tab_pagto, tab_contrato, tab_credor, tab_produto = st.tabs([
    "Pagamentos", "Contratos", "Credores", "Produtos/Serviços"
])

with tab_pagto:
    st.subheader("Cadastro de Pagamentos")
    with st.form("form_pagamento", clear_on_submit=True):
        data_pag = st.date_input("Data do pagamento (obrigatório)", format="DD/MM/YYYY")
        periodo = st.text_input("Período do pagamento (obrigatório) (ex: jul/2025)")
        valor = st.number_input("Valor do pagamento (obrigatório)", format="%.2f", step=0.01)
        
        credores_df = st.session_state['credores_df']
        map_credor_nome_doc = pd.Series(credores_df.CREDOR_DOC.values,index=credores_df.CREDOR_NOME).to_dict()
        credor_selecionado = st.selectbox("Credor (obrigatório)", options=list(map_credor_nome_doc.keys()))
        
        tipo_pagamento = st.selectbox("Tipo de pagamento", ["Nota Fiscal", "Recibo", "Fatura", "Boleto"])
        
        submitted = st.form_submit_button("Cadastrar Pagamento")
        
        if submitted:
            try:
                credor_doc_selecionado = map_credor_nome_doc[credor_selecionado]
                novo_pagamento = Pagamento(
                    PAGTO_DATA=data_pag,
                    PAGTO_PERIODO=periodo,
                    PAGTO_VALOR=valor,
                    CREDOR_DOC=credor_doc_selecionado,
                    PAGTO_TIPO=tipo_pagamento 
                )
                with get_session() as session:
                    session.add(novo_pagamento)
                    session.commit()
                st.success(f"Pagamento para {credor_selecionado} registrado com sucesso no banco de dados!")
            except Exception as e:
                st.error(f"Erro ao cadastrar pagamento: {e}")


with tab_contrato:
    st.subheader("Cadastro de Contratos")
    with st.form("form_contrato", clear_on_submit=True):
        numero_contrato = st.text_input("Número do contrato (obrigatório)")
        
        map_credor_nome_doc = pd.Series(credores_df.CREDOR_DOC.values, index=credores_df.CREDOR_NOME).to_dict()
        credor_nome_selecionado = st.selectbox("Credor associado (obrigatório)", options=list(map_credor_nome_doc.keys()))
        
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input("Data de início da vigência (obrigatório)")
        with col2:
            data_fim = st.date_input("Data de término da vigência (obrigatório)")

        valor_global = st.number_input("Valor global do contrato (obrigatório)", min_value=0.0, format="%.2f")

        submitted = st.form_submit_button("Cadastrar Contrato")

        if submitted:
            if not all([numero_contrato, credor_nome_selecionado, data_inicio, data_fim]):
                st.error("Por favor, preencha todos os campos obrigatórios.")
            elif data_fim < data_inicio:
                st.error("A data de término da vigência não pode ser anterior à data de início.")
            else:
                try:
                    credor_doc_selecionado = map_credor_nome_doc[credor_nome_selecionado]
                    novo_contrato = Contrato(
                        CONTRATO_N=numero_contrato,
                        CREDOR_DOC=credor_doc_selecionado,
                        CONTRATO_DATA_INI=data_inicio,
                        CONTRATO_DATA_FIM=data_fim,
                        CONTRATO_VALOR=valor_global
                    )
                    with get_session() as session:
                        session.add(novo_contrato)
                        session.commit()
                    st.success(f"Contrato {numero_contrato} cadastrado com sucesso!")
                    carregar_dados_bd() # Recarrega para exibir
                except Exception as e:
                    st.error(f"Erro ao cadastrar contrato: {e}")

    st.write("Contratos Cadastrados")
    st.dataframe(st.session_state.get('contratos_df', pd.DataFrame()).fillna('-'), use_container_width=True)

with tab_credor:
    st.subheader("Cadastro de Credores")
    with st.form("form_credor", clear_on_submit=True):
        credor_doc = st.text_input("CPF ou CNPJ do credor (obrigatório)")
        credor_nome = st.text_input("Nome do credor (obrigatório)")
        
        submitted = st.form_submit_button("Cadastrar Credor")

        if submitted:
            if not credor_doc or not credor_nome:
                st.error("Ambos os campos são obrigatórios.")
            else:
                try:
                    novo_credor = Credor(CREDOR_DOC=credor_doc.strip("'"), CREDOR_NOME=credor_nome.strip("'"))
                    with get_session() as session:
                        session.add(novo_credor)
                        session.commit()
                    st.success(f"Credor '{credor_nome}' cadastrado com sucesso!")
                    carregar_dados_bd() # Recarrega para exibir
                except Exception as e:
                    st.error(f"Erro ao cadastrar credor: {e}")
    
    st.write("Credores Cadastrados")
    df_credores_display = st.session_state.get('credores_df', pd.DataFrame())
    for col in df_credores_display.select_dtypes(include=['object']):
        df_credores_display[col] = df_credores_display[col].str.strip("'")
    st.dataframe(df_credores_display.fillna('-'), use_container_width=True)

with tab_produto:
    st.subheader("Cadastro de Produtos/Serviços")
    with st.form("form_produto", clear_on_submit=True):
        prod_desc = st.text_input("Descrição do produto/serviço (obrigatório)")
        prod_valor = st.number_input("Valor unitário (obrigatório)", min_value=0.0, format="%.2f")

        submitted = st.form_submit_button("Cadastrar Produto/Serviço")

        if submitted:
            if not prod_desc or prod_valor <= 0:
                st.error("Descrição e valor (maior que zero) são obrigatórios.")
            else:
                try:
                    novo_produto = ProdutoServico(PROD_SERV_DESCRICAO=prod_desc, PROD_SERV_VALOR=prod_valor)
                    with get_session() as session:
                        session.add(novo_produto)
                        session.commit()
                    st.success(f"Produto '{prod_desc}' cadastrado com sucesso!")
                    carregar_dados_bd() # Recarrega para exibir
                except Exception as e:
                    st.error(f"Erro ao cadastrar produto: {e}")
    
    st.write("Produtos/Serviços Cadastrados")
    st.dataframe(st.session_state.get('produtos_servicos_df', pd.DataFrame()).fillna('-'), use_container_width=True)