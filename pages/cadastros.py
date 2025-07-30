import streamlit as st
import pandas as pd
from datetime import datetime
from src.database import get_session, engine, Credor, Contrato, ProdutoServico, Pagamento
from sqlalchemy import update

st.set_page_config(layout="wide", page_title="Cadastros")

st.header("Módulo de Cadastros e Edições")
st.info("As tabelas abaixo são editáveis. Clique em uma célula para alterar seu valor e depois use o botão 'Salvar Alterações' para gravar no banco de dados.")

# Função para carregar dados do BD, com cache para otimizar
@st.cache_data(ttl=30)
def carregar_dados_bd():
    data = {}
    with get_session() as session:
        data['credores'] = pd.read_sql("SELECT * FROM CREDOR ORDER BY CREDOR_NOME", engine, index_col='CREDOR_DOC')
        data['contratos'] = pd.read_sql("SELECT * FROM CONTRATO", engine, index_col='CONTRATO_N')
        data['produtos_servicos'] = pd.read_sql("SELECT * FROM PRODUTOS_SERVICOS ORDER BY PROD_SERV_DESCRICAO", engine, index_col='PROD_SERV_N')
    return data

# Carrega e prepara os dados
db_data = carregar_dados_bd()
credores_df = db_data['credores']
contratos_df = db_data['contratos']
produtos_servicos_df = db_data['produtos_servicos']

tab_pagto, tab_contrato, tab_credor, tab_produto = st.tabs([
    "➕ Novo Pagamento", "📄 Contratos", "👥 Credores", "📦 Produtos/Serviços"
])

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

with tab_contrato:
    st.subheader("Editar Contratos Cadastrados")
    edited_contratos = st.data_editor(contratos_df.fillna('-'), use_container_width=True, key="editor_contratos")
    if not edited_contratos.equals(contratos_df):
        if st.button("Salvar Alterações nos Contratos", type="primary"):
            # Lógica para salvar alterações (simplificada)
            # Uma implementação completa compararia as diferenças e faria updates específicos.
            st.success("Lógica de salvamento para contratos aqui!")


with tab_credor:
    st.subheader("Editar Credores Cadastrados")
    edited_credores = st.data_editor(credores_df.fillna('-'), use_container_width=True, key="editor_credores")
    if not edited_credores.equals(credores_df):
        if st.button("Salvar Alterações nos Credores", type="primary"):
            try:
                # Compara o dataframe original com o editado
                diff = edited_credores.compare(credores_df)
                with get_session() as session:
                    for credor_doc, row in diff.iterrows():
                        # Obtém os valores atualizados
                        update_values = row['self'].dropna().to_dict()
                        if update_values:
                            # Constrói e executa a query de update
                            stmt = update(Credor).where(Credor.CREDOR_DOC == credor_doc).values(**update_values)
                            session.execute(stmt)
                    session.commit()
                st.success("Alterações nos credores salvas com sucesso!")
                st.cache_data.clear() # Limpa o cache para recarregar
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar alterações: {e}")


with tab_produto:
    st.subheader("Editar Produtos e Serviços Cadastrados")
    edited_produtos = st.data_editor(produtos_servicos_df.fillna('-'), use_container_width=True, key="editor_produtos")
    if not edited_produtos.equals(produtos_servicos_df):
        if st.button("Salvar Alterações nos Produtos", type="primary"):
            st.success("Lógica de salvamento para produtos aqui!")