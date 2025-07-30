import streamlit as st
import pandas as pd
from datetime import date
from src.database import get_session, engine, Credor, Contrato, ProdutoServico, Pagamento
from sqlalchemy import update

st.set_page_config(layout="wide", page_title="Cadastros")

st.header("Módulo de Cadastros e Edições")
st.info(
    "Utilize os formulários para adicionar novos registros ou clique diretamente nas tabelas para editar entradas existentes. "
    "Lembre-se de salvar as alterações."
)

@st.cache_data(ttl=30)
def carregar_dados_bd():
    """Carrega todos os dados necessários das tabelas do banco de dados."""
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

# Abas para cada tipo de cadastro
tab_pagto, tab_contrato, tab_credor, tab_produto = st.tabs([
    "➕ Pagamentos", "📄 Contratos", "👥 Credores", "📦 Produtos/Serviços"
])

# --- Aba de Pagamentos ---
with tab_pagto:
    st.subheader("Cadastro de Pagamentos")
    with st.form("form_pagamento", clear_on_submit=True):
        data_pag = st.date_input("Data do pagamento (obrigatório)", format="DD/MM/YYYY", value=None)
        periodo = st.text_input("Período do pagamento (ex: jul/2025)", placeholder="jul/2025")
        valor = st.number_input("Valor do pagamento (obrigatório)", format="%.2f", step=10.0, value=0.0)
        map_credor_nome_doc = pd.Series(credores_df.CREDOR_DOC.values, index=credores_df.CREDOR_NOME).to_dict()
        credor_selecionado = st.selectbox("Credor (obrigatório)", options=list(map_credor_nome_doc.keys()), index=None, placeholder="Selecione o credor")
        tipo_pagamento = st.selectbox("Tipo de pagamento", ["Nota Fiscal", "Recibo", "Fatura", "Boleto", "Outro"], index=None, placeholder="Selecione o tipo")
        
        submitted = st.form_submit_button("Cadastrar Pagamento")
        if submitted:
            if not all([data_pag, valor > 0, credor_selecionado]):
                st.error("Preencha todos os campos obrigatórios (Data, Valor e Credor)!")
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
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"Erro ao cadastrar pagamento: {e}")



# --- Aba de Contratos ---
with tab_contrato:
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

# --- Aba de Credores ---
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
    
# --- Aba de Produtos/Serviços ---
with tab_produto:
    st.subheader("Adicionar Novo Produto ou Serviço")
    with st.form("form_produto", clear_on_submit=True):
        prod_desc = st.text_input("Descrição do Produto/Serviço (obrigatório)")
        prod_valor = st.number_input("Valor Unitário (obrigatório)", min_value=0.01, format="%.2f")

        if st.form_submit_button("Cadastrar Produto/Serviço"):
            if not all([prod_desc, prod_valor]):
                st.error("Ambos os campos são obrigatórios.")
            else:
                try:
                    novo_produto = ProdutoServico(PROD_SERV_DESCRICAO=prod_desc.strip(), PROD_SERV_VALOR=prod_valor)
                    with get_session() as session:
                        session.add(novo_produto)
                        session.commit()
                    st.success(f"Produto '{prod_desc}' cadastrado com sucesso!")
                    st.cache_data.clear(); st.rerun()
                except Exception as e:
                    st.error(f"Erro ao cadastrar produto: {e}")

    st.divider()
    st.subheader("Editar Produtos e Serviços Existentes")
    st.data_editor(produtos_servicos_df.fillna('-'), use_container_width=True, key="editor_produtos")
    if st.session_state.editor_produtos['edited_rows']:
        if st.button("Salvar Alterações nos Produtos", type="primary", key="save_produtos"):
            try:
                with get_session() as session:
                    # Itera sobre as linhas que foram editadas
                    for prod_index, changes in st.session_state.editor_produtos['edited_rows'].items():
                        # Obtém o ID real do produto a partir do índice da linha
                        prod_serv_n = produtos_servicos_df.index[prod_index]
                        # Cria e executa o comando de atualização no banco de dados
                        stmt = update(ProdutoServico).where(ProdutoServico.PROD_SERV_N == prod_serv_n).values(**changes)
                        session.execute(stmt)
                    # Confirma todas as alterações no banco de dados
                    session.commit()
                st.success("Alterações nos produtos salvas com sucesso!")
                st.cache_data.clear() # Limpa o cache para forçar a releitura dos dados
                st.rerun() # Reinicia a página para exibir os dados atualizados
            except Exception as e:
                st.error(f"Erro ao salvar alterações nos produtos: {e}")