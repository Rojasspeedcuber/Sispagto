import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide", page_title="Cadastros")

st.header("Módulo de Cadastros e Edições")

# Define as abas
tab_pagto, tab_contrato, tab_credor, tab_produto = st.tabs([
    "Pagamentos", "Contratos e Aditivos", "Credores", "Produtos/Serviços"
])

# --- ABA DE PAGAMENTOS (Estrutura base) ---
with tab_pagto:
    st.subheader("Cadastro de Pagamentos")
    st.info("Esta seção depende dos cadastros de Credores, Contratos e Produtos.")
    
    # Verifica se os dados necessários existem na sessão
    if 'credores_df' in st.session_state:
        with st.form("form_pagamento", clear_on_submit=True):
            data_pag = st.date_input("Data do pagamento (obrigatório)", format="DD/MM/YYYY")
            periodo = st.text_input("Período do pagamento (obrigatório)")
            valor = st.number_input("Valor do pagamento (obrigatório)", format="%.2f", step=0.01)
            
            # Popula o selectbox com os credores carregados
            credores_df = st.session_state['credores_df']
            lista_credores = credores_df['CREDOR_NOME'].tolist()
            credor_selecionado = st.selectbox("Credor (obrigatório)", options=lista_credores)
            
            tipo_pagamento = st.selectbox("Tipo de pagamento", ["Nota Fiscal", "Recibo", "Fatura", "Boleto"])
            
            submitted = st.form_submit_button("Cadastrar Pagamento")
            
            if submitted:
                # Aqui entraria a lógica de validação e inserção de dados
                st.success(f"Pagamento para {credor_selecionado} registrado com sucesso!")
    else:
        st.warning("Por favor, carregue a tabela de Credores na aba 'Upload de Tabelas' primeiro.")

# --- ABA DE CONTRATOS ---
with tab_contrato:
    st.subheader("Cadastro de Contratos")
    
    if 'credores_df' in st.session_state and 'produtos_servicos_df' in st.session_state:
        credores_df = st.session_state['credores_df']
        produtos_df = st.session_state['produtos_servicos_df']

        with st.form("form_contrato", clear_on_submit=True):
            st.write("Informações do Contrato")
            numero_contrato = st.text_input("Número do contrato (obrigatório)")
            
            # Mapeia nome do credor para o seu documento (CPF/CNPJ)
            map_credor_nome_doc = pd.Series(credores_df.CREDOR_DOC.values, index=credores_df.CREDOR_NOME).to_dict()
            credor_nome_selecionado = st.selectbox("Credor associado (obrigatório)", options=list(map_credor_nome_doc.keys()))
            
            col1, col2 = st.columns(2)
            with col1:
                data_inicio = st.date_input("Data de início da vigência (obrigatório)")
            with col2:
                data_fim = st.date_input("Data de término da vigência (obrigatório)")

            valor_global = st.number_input("Valor global do contrato (obrigatório)", min_value=0.0, format="%.2f", step=0.01)

            st.write("Itens do Contrato")
            # Mapeia descrição do produto para o seu número
            map_prod_desc_n = pd.Series(produtos_df.PROD_SERV_N.values, index=produtos_df.PROD_SERV_DESCRICAO).to_dict()
            produtos_selecionados = st.multiselect(
                "Selecione os produtos/serviços do contrato (obrigatório)",
                options=list(map_prod_desc_n.keys())
            )
            
            submitted = st.form_submit_button("Cadastrar Contrato")

            if submitted:
                if not all([numero_contrato, credor_nome_selecionado, data_inicio, data_fim, produtos_selecionados]):
                    st.error("Por favor, preencha todos os campos obrigatórios.")
                elif data_fim < data_inicio:
                    st.error("A data de término da vigência não pode ser anterior à data de início.")
                else:
                    # Lógica para adicionar o novo contrato ao DataFrame na sessão
                    credor_doc_selecionado = map_credor_nome_doc[credor_nome_selecionado]
                    novo_contrato = pd.DataFrame([{
                        "CONTRATO_N": numero_contrato,
                        "CREDOR_DOC": credor_doc_selecionado,
                        "CONTRATO_DATA_INI": data_inicio,
                        "CONTRATO_DATA_FIM": data_fim,
                        "CONTRATO_VALOR": valor_global,
                        "LISTA_ITENS_N": "N/A" # Simplificado
                    }])
                    
                    if 'contratos_df' not in st.session_state:
                         st.session_state['contratos_df'] = pd.DataFrame(columns=novo_contrato.columns)
                    
                    st.session_state['contratos_df'] = pd.concat([st.session_state['contratos_df'], novo_contrato], ignore_index=True)
                    st.success(f"Contrato {numero_contrato} cadastrado com sucesso!")

        if 'contratos_df' in st.session_state:
            st.write("Contratos Cadastrados")
            st.dataframe(st.session_state['contratos_df'], use_container_width=True)

    else:
        st.warning("Para cadastrar contratos, carregue as tabelas de Credores e Produtos/Serviços primeiro.")


# --- ABA DE CREDORES ---
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
                # Cria um DataFrame para o novo credor
                novo_credor = pd.DataFrame([{"CREDOR_DOC": credor_doc, "CREDOR_NOME": credor_nome}])
                
                # Se o df de credores não existir na sessão, cria um vazio
                if 'credores_df' not in st.session_state:
                    st.session_state['credores_df'] = pd.DataFrame(columns=novo_credor.columns)
                
                # Adiciona o novo credor ao DataFrame na sessão
                st.session_state['credores_df'] = pd.concat([st.session_state['credores_df'], novo_credor], ignore_index=True)
                st.success(f"Credor '{credor_nome}' cadastrado com sucesso!")
    
    # Exibe a lista atual de credores
    if 'credores_df' in st.session_state:
        st.write("Credores Cadastrados")
        st.dataframe(st.session_state['credores_df'], use_container_width=True)


# --- ABA DE PRODUTOS/SERVIÇOS ---
with tab_produto:
    st.subheader("Cadastro de Produtos/Serviços")
    with st.form("form_produto", clear_on_submit=True):
        prod_desc = st.text_input("Descrição do produto/serviço (obrigatório)")
        prod_valor = st.number_input("Valor unitário (obrigatório)", min_value=0.0, format="%.2f", step=0.01)

        submitted = st.form_submit_button("Cadastrar Produto/Serviço")

        if submitted:
            if not prod_desc or prod_valor <= 0:
                st.error("Descrição e valor (maior que zero) são obrigatórios.")
            else:
                # Se o df de produtos não existir, cria um vazio
                if 'produtos_servicos_df' not in st.session_state:
                    st.session_state['produtos_servicos_df'] = pd.DataFrame(columns=["PROD_SERV_N", "PROD_SERV_DESCRICAO", "PROD_SERV_VALOR"])
                
                # Gera uma nova PK para o produto (simulação)
                if st.session_state['produtos_servicos_df'].empty:
                    nova_pk = 1
                else:
                    nova_pk = st.session_state['produtos_servicos_df']['PROD_SERV_N'].max() + 1

                novo_produto = pd.DataFrame([{
                    "PROD_SERV_N": nova_pk,
                    "PROD_SERV_DESCRICAO": prod_desc,
                    "PROD_SERV_VALOR": prod_valor
                }])

                st.session_state['produtos_servicos_df'] = pd.concat([st.session_state['produtos_servicos_df'], novo_produto], ignore_index=True)
                st.success(f"Produto '{prod_desc}' cadastrado com sucesso!")

    if 'produtos_servicos_df' in st.session_state:
        st.write("Produtos/Serviços Cadastrados")
        st.dataframe(st.session_state['produtos_servicos_df'], use_container_width=True)
