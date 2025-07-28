import streamlit as st
import pandas as pd
from src.database import get_session, table_exists, engine
from sqlalchemy import inspect
from io import StringIO

st.set_page_config(layout="wide", page_title="Upload de Tabelas")

st.header("Carga de Dados do Sistema via CSV")

st.info(
    "Faça o upload dos arquivos CSV correspondentes a cada tabela do sistema. "
    "Os dados carregados serão salvos no banco de dados e ficarão disponíveis permanentemente."
)

TABLE_MAP = {
    "CREDOR": "credores_df",
    "PRODUTOS_SERVICOS": "produtos_servicos_df",
    "CONTRATO": "contratos_df",
    "PAGTO": "pagamentos_df",
    "NF": "nf_df",
    "RECIBO": "recibo_df",
    "FATURA": "fatura_df",
    "BOLETO": "boleto_df",
    "ADITIVOS": "aditivos_df",
    "LISTA_ITENS": "lista_itens_df",
}

if 'uploaders' not in st.session_state:
    st.session_state.uploaders = {key: None for key in TABLE_MAP.keys()}

col1, col2, col3 = st.columns(3)
columns = [col1, col2, col3]

for i, table_name in enumerate(TABLE_MAP.keys()):
    with columns[i % 3]:
        st.session_state.uploaders[table_name] = st.file_uploader(
            f"Tabela {table_name}",
            type="csv",
            key=f"upload_{table_name}"
        )

if st.button("✔️ Processar e Salvar no Banco de Dados", use_container_width=True, type="primary"):
    with st.spinner("Lendo, processando e salvando arquivos..."):
        files_processed = 0
        inspector = inspect(engine)

        for table_name, uploader in st.session_state.uploaders.items():
            if uploader is not None:
                try:
                    df = pd.read_csv(uploader, sep=';')

                    # Correção para o erro de digitação em CONTRATO
                    if 'CONTRATO_LALOR' in df.columns:
                        df.rename(columns={'CONTRATO_LALOR': 'CONTRATO_VALOR'}, inplace=True)
                    
                    # Remove aspas simples dos dados
                    for col in df.select_dtypes(include=['object']):
                        df[col] = df[col].str.strip("'")

                    # Garante que apenas colunas existentes no BD sejam inseridas
                    if table_exists(get_session(), table_name):
                        db_columns = [c['name'] for c in inspector.get_columns(table_name)]
                        df_filtered = df[[col for col in df.columns if col in db_columns]]
                        
                        df_filtered.to_sql(table_name, engine, if_exists='append', index=False)
                        files_processed += 1
                        st.session_state[TABLE_MAP[table_name]] = df_filtered
                    else:
                        st.warning(f"A tabela '{table_name}' não existe no banco de dados. Pulando...")

                except Exception as e:
                    st.error(f"Erro ao processar a tabela {table_name}: {e}")
    
    if files_processed > 0:
        st.success(f"{files_processed} arquivo(s) processado(s) e salvo(s) no banco de dados com sucesso!")
    else:
        st.warning("Nenhum arquivo foi selecionado para processamento.")

st.markdown("---")
st.subheader("Status dos Dados no Banco de Dados")

status_data = []
with get_session() as session:
    for table_name in TABLE_MAP.keys():
        if table_exists(session, table_name):
            try:
                count = pd.read_sql(f"SELECT COUNT(*) FROM {table_name}", engine).iloc[0,0]
                status = "✅ Carregado"
                info = f"{count} linhas"
            except Exception as e:
                status = "❌ Erro"
                info = str(e)
        else:
            status = "⚠️ Pendente"
            info = "Tabela não encontrada no BD"
        status_data.append({"Tabela": table_name, "Status": status, "Info": info})

st.dataframe(pd.DataFrame(status_data), use_container_width=True)