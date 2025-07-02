import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Upload de Tabelas")

st.header("Carga de Dados via CSV")

st.write(
    "Nesta seção, você pode carregar os dados do sistema a partir de arquivos CSV. "
    "Selecione o tipo de tabela que deseja carregar e escolha o arquivo correspondente."
)
st.info(
    "Os dados carregados ficarão disponíveis na aba 'Relatórios' para visualização e análise."
)

# Dicionário para mapear o nome amigável da tabela para a chave no session_state
TABLE_MAP = {
    "Pagamentos": "pagamentos_df",
    "Credores": "credores_df",
    "Contratos": "contratos_df",
    "Produtos/Serviços": "produtos_servicos_df",
    # Adicione outras tabelas conforme necessário (NF, Recibo, etc.)
}

# --- Formulário de Upload ---
tipo_tabela = st.selectbox(
    "Selecione o tipo de tabela para carregar:",
    options=list(TABLE_MAP.keys())
)

uploaded_file = st.file_uploader(f"Escolha o arquivo CSV de **{tipo_tabela}**", type="csv")

if uploaded_file is not None:
    try:
        # Lê o arquivo CSV para um DataFrame
        df = pd.read_csv(uploaded_file)
        
        st.write("**Pré-visualização dos Dados Carregados:**")
        st.dataframe(df.head(), use_container_width=True)
        
        if st.button(f"✔️ Carregar Dados de {tipo_tabela}", use_container_width=True):
            # Obtém a chave correspondente do dicionário
            session_key = TABLE_MAP[tipo_tabela]
            
            # Armazena o DataFrame no estado da sessão
            st.session_state[session_key] = df
            
            st.success(f"Tabela de **{tipo_tabela}** carregada com sucesso! "
                       "Os dados já estão disponíveis na aba de Relatórios.")

    except Exception as e:
        st.error(f"Ocorreu um erro ao processar o arquivo: {e}")

# --- Status dos Dados Carregados ---
st.markdown("---")
st.subheader("Status dos Dados na Sessão Atual")

for nome_amigavel, chave_sessao in TABLE_MAP.items():
    if chave_sessao in st.session_state:
        st.success(f"**{nome_amigavel}:** {st.session_state[chave_sessao].shape[0]} linhas carregadas.")
    else:
        st.warning(f"**{nome_amigavel}:** Nenhum dado carregado ainda.")
