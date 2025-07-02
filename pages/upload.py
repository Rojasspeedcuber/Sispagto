# pages/3_⬆️_Upload_de_Tabelas.py
import streamlit as st
import pandas as pd
from io import StringIO

st.set_page_config(layout="wide", page_title="Upload de Tabelas")

st.header("Carga de Dados do Sistema via CSV")

st.info(
    "Faça o upload dos arquivos CSV correspondentes a cada tabela do sistema. "
    "Os dados carregados serão utilizados para gerar os relatórios na aba ao lado."
)

# Dicionário para mapear o nome da tabela para a chave no session_state
# e para o objeto do file_uploader
TABLE_MAP = {
    "PAGTO": "pagamentos_df",
    "CREDOR": "credores_df",
    "PRODUTOS_SERVICOS": "produtos_servicos_df",
    "CONTRATO": "contratos_df",
    "NF": "nf_df",
    "RECIBO": "recibo_df",
    "FATURA": "fatura_df",
    "BOLETO": "boleto_df",
    "ADITIVOS": "aditivos_df",
    "LISTA_ITENS": "lista_itens_df",
}

# Inicializa o dicionário de uploaders no session state se não existir
if 'uploaders' not in st.session_state:
    st.session_state.uploaders = {key: None for key in TABLE_MAP.keys()}

# --- Layout dos Uploaders em Colunas ---
col1, col2, col3 = st.columns(3)
columns = [col1, col2, col3]

# Distribui os uploaders pelas colunas
for i, table_name in enumerate(TABLE_MAP.keys()):
    with columns[i % 3]:
        st.session_state.uploaders[table_name] = st.file_uploader(
            f"Tabela {table_name}",
            type="csv",
            key=f"upload_{table_name}"
        )

# --- Botão para Processar os Arquivos ---
if st.button("✔️ Processar Arquivos Carregados", use_container_width=True, type="primary"):
    with st.spinner("Lendo e processando arquivos..."):
        files_processed = 0
        for table_name, uploader in st.session_state.uploaders.items():
            if uploader is not None:
                try:
                    # Lê o arquivo CSV. O delimitador ';' é crucial.
                    df = pd.read_csv(uploader, sep=';')
                    
                    # Armazena o DataFrame no estado da sessão com a chave correta
                    session_key = TABLE_MAP[table_name]
                    st.session_state[session_key] = df
                    files_processed += 1
                except Exception as e:
                    st.error(f"Erro ao ler o arquivo para a tabela {table_name}: {e}")
    
    if files_processed > 0:
        st.success(f"{files_processed} arquivo(s) processado(s) com sucesso!")
    else:
        st.warning("Nenhum arquivo foi selecionado para processamento.")

# --- Status dos Dados Carregados ---
st.markdown("---")
st.subheader("Status dos Dados na Sessão Atual")

status_data = []
for table_name, session_key in TABLE_MAP.items():
    if session_key in st.session_state:
        status = "✅ Carregado"
        rows = st.session_state[session_key].shape[0]
        cols = st.session_state[session_key].shape[1]
        info = f"{rows} linhas, {cols} colunas"
    else:
        status = "⚠️ Pendente"
        info = "Nenhum arquivo carregado"
    status_data.append({"Tabela": table_name, "Status": status, "Info": info})

st.dataframe(pd.DataFrame(status_data), use_container_width=True)

