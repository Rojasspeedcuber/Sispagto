import streamlit as st
import pandas as pd
from datetime import date
from src.database import get_session, engine, Credor, Contrato, ProdutoServico, Pagamento
from sqlalchemy import update

# Configuração da página
st.set_page_config(layout="wide", page_title="Cadastros")

# Título e informações
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
        # Carrega credores, usando CREDOR_DOC como índice
        data['credores'] = pd.read_sql("SELECT * FROM CREDOR ORDER BY CREDOR_NOME", engine, index_col='CREDOR_DOC')
        # Carrega contratos, usando CONTRATO_N como índice
        data['contratos'] = pd.read_sql("SELECT * FROM CONTRATO", engine, index_col='CONTRATO_N')
        # Carrega produtos, usando PROD_SERV_N como índice
        data['produtos_servicos'] = pd.read_sql("SELECT * FROM PRODUTOS_SERVICOS ORDER BY PROD_SERV_DESCRICAO", engine, index_col='PROD_SERV_N')
    return data

# Carregamento inicial dos dados
try:
    db_data = carregar_dados_bd()
    credores_df = db_data['credores']
    contratos_df = db_data['contratos']
    produtos_servicos_df = db_data['produtos_servicos']
except Exception as e:
    st.error(f"Falha ao carregar dados do banco de dados: {e}")
    st.warning("Verifique se o banco de dados foi inicializado e se a página de Upload foi utilizada.")
    # Cria dataframes vazios para evitar mais erros
    credores_df = pd.DataFrame()
    contratos_df = pd.DataFrame()
    produtos_servicos_df = pd.DataFrame()


# Definição das abas de navegação
tab_pagto, tab_contrato, tab_credor, tab_produto = st.tabs([
    "➕ Pagamentos", "📄 Contratos", "👥 Credores", "📦 Produtos/Serviços"
])


# --- Aba de Pagamentos ---
with tab_pagto:
    st.subheader("Cadastro de Novos Pagamentos")
    with st.form("form_pagamento", clear_on_submit=True):
        data_pag = st.date_input("Data do pagamento (obrigatório)", format="DD/MM/AAAA", value=None)
        periodo = st.text_input("Período do pagamento (ex: jul/2025)", placeholder="jul/2025")
        valor = st.number_input("Valor do pagamento (obrigatório)", min_value=0.01, format="%.2f")
        
        # Corrige o erro ao criar o mapa de credores
        if not credores_df.empty:
            map_credor_nome_doc = pd.Series(credores_df.index, index=credores_df['CREDOR_NOME']).to_dict()
            credor_nome_selecionado = st.selectbox("Credor (obrigatório)", options=list(map_credor_nome_doc.keys()), index=None, placeholder="Selecione o credor")
        else:
            credor_nome_selecionado = None
            st.warning("Nenhum credor cadastrado. Cadastre um credor na aba 'Credores' primeiro.")

        tipo_pagamento = st.selectbox("Tipo de pagamento", ["Nota Fiscal", "Recibo", "Fatura", "Boleto", "Outro"], index=None, placeholder="Selecione o tipo")
        
        # Adiciona o botão de submit que estava faltando
        submitted = st.form_submit_button("Cadastrar Pagamento")
        if submitted:
            if not all([data_pag, valor, credor_nome_selecionado]):
                st.error("Preencha todos os campos obrigatórios!")
            else:
                try:
                    novo_pagamento = Pagamento(
                        PAGTO_DATA=data_pag, PAGTO_PERIODO=periodo, PAGTO_VALOR=valor,
                        CREDOR_DOC=map_credor_nome_doc[credor_nome_selecionado], PAGTO_TIPO=tipo_pagamento
                    )
                    with get_session() as session:
                        session.add(novo_pagamento)
                        session.commit()
                    st.success(f"Pagamento para {credor_nome_selecionado} registrado com sucesso!")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao cadastrar pagamento: {e}")

# --- Aba de Contratos ---
with tab_contrato:
    st.subheader("Adicionar Novo Contrato")
    with st.form("form_contrato", clear_on_submit=True):
        numero_contrato = st.text_input("Número do Contrato (obrigatório)")
        
        if not credores_df.empty:
            map_credor_nome_doc = pd.Series(credores_df.index, index=credores_df['CREDOR_NOME']).to_dict()
            credor_nome_selecionado_contrato = st.selectbox("Credor (obrigatório)", options=list(map_credor_nome_doc.keys()), index=None, key="credor_contrato", placeholder="Escolha o Credor")
        else:
            credor_nome_selecionado_contrato = None

        col1, col2 = st.columns(2)
        data_inicio = col1.date_input("Data de Início", value=None)
        data_fim = col2.date_input("Data de Fim", value=None)
        valor_global = st.number_input("Valor Global do Contrato", min_value=0.0, format="%.2f")

        if st.form_submit_button("Cadastrar Contrato"):
            if not all([numero_contrato, credor_nome_selecionado_contrato, data_inicio, data_fim, valor_global > 0]):
                st.error("Por favor, preencha todos os campos obrigatórios.")
            else:
                try:
                    novo_contrato = Contrato(
                        CONTRATO_N=numero_contrato, CREDOR_DOC=map_credor_nome_doc[credor_nome_selecionado_contrato],
                        CONTRATO_DATA_INI=data_inicio, CONTRATO_DATA_FIM=data_fim, CONTRATO_VALOR=valor_global
                    )
                    with get_session() as session:
                        session.add(novo_contrato)
                        session.commit()
                    st.success(f"Contrato {numero_contrato} cadastrado com sucesso!")
                    st.cache_data.clear(); st.rerun()
                except Exception as e:
                    st.error(f"Erro ao cadastrar contrato: {e}")
    
    st.divider()
    st.subheader("Editar Contratos Existentes")
    st.data_editor(contratos_df.fillna('-'), use_container_width=True, key="editor_contratos")
    # ... (lógica de salvamento para edição de contratos)

# --- Aba de Credores ---
with tab_credor:
    st.subheader("Adicionar Novo Credor")
    with st.form("form_credor", clear_on_submit=True):
        credor_doc = st.text_input("CPF ou CNPJ do Credor (obrigatório)")
        credor_nome = st.text_input("Nome do Credor (obrigatório)")

        if st.form_submit_button("Cadastrar Credor"):
            if not all([credor_doc, credor_nome]):
                st.error("Ambos os campos são obrigatórios.")
            else:
                try:
                    novo_credor = Credor(CREDOR_DOC=credor_doc.strip(), CREDOR_NOME=credor_nome.strip())
                    with get_session() as session:
                        session.add(novo_credor)
                        session.commit()
                    st.success(f"Credor '{credor_nome}' cadastrado com sucesso!")
                    st.cache_data.clear(); st.rerun()
                except Exception as e:
                    st.error(f"Erro ao cadastrar credor: {e}")
    
    st.divider()
    st.subheader("Editar Credores Existentes")
    st.data_editor(credores_df.fillna('-'), use_container_width=True, key="editor_credores")
    if st.session_state.get('editor_credores', {}).get('edited_rows'):
        if st.button("Salvar Alterações nos Credores", type="primary"):
            try:
                with get_session() as session:
                    for doc_index, changes in st.session_state.editor_credores['edited_rows'].items():
                        credor_doc_real = credores_df.index[doc_index]
                        stmt = update(Credor).where(Credor.CREDOR_DOC == credor_doc_real).values(**changes)
                        session.execute(stmt)
                    session.commit()
                st.success("Alterações nos credores salvas com sucesso!")
                st.cache_data.clear(); st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar alterações nos credores: {e}")

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
    if st.session_state.get('editor_produtos', {}).get('edited_rows'):
        if st.button("Salvar Alterações nos Produtos", type="primary"):
            try:
                with get_session() as session:
                    for prod_index, changes in st.session_state.editor_produtos['edited_rows'].items():
                        prod_serv_n_real = produtos_servicos_df.index[prod_index]
                        stmt = update(ProdutoServico).where(ProdutoServico.PROD_SERV_N == prod_serv_n_real).values(**changes)
                        session.execute(stmt)
                    session.commit()
                st.success("Alterações nos produtos salvas com sucesso!")
                st.cache_data.clear(); st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar alterações nos produtos: {e}")