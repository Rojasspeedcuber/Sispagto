import streamlit as st
import pandas as pd
from src.database import get_session, table_exists, engine
from sqlalchemy import inspect, text
from io import StringIO

st.set_page_config(layout="wide", page_title="Upload de Tabelas")

st.header("Carga de Dados do Sistema via CSV")

st.info(
    "Faça o upload dos arquivos CSV correspondentes a cada tabela do sistema. "
    "O sistema agora ignora automaticamente linhas duplicadas que já existem no banco de dados."
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
        files_with_errors = 0
        inspector = inspect(engine)

        for table_name, uploader in st.session_state.uploaders.items():
            if uploader is not None:
                try:
                    df = pd.read_csv(uploader, sep=';', decimal=',')

                    # Limpeza de dados
                    if 'CONTRATO_LALOR' in df.columns:
                        df.rename(columns={'CONTRATO_LALOR': 'CONTRATO_VALOR'}, inplace=True)
                    for col in df.select_dtypes(include=['object']):
                        df[col] = df[col].str.strip("'")

                    with get_session() as session:
                        if table_exists(session, table_name):
                            pk_columns = [key.name for key in inspector.get_primary_keys(table_name)]
                            
                            # 1. Remove duplicatas do próprio arquivo CSV
                            if pk_columns:
                                df.drop_duplicates(subset=pk_columns, inplace=True)
                            else:
                                df.drop_duplicates(inplace=True)

                            # 2. Remove duplicatas que já existem no banco de dados
                            if pk_columns:
                                existing_pks_df = pd.read_sql_table(table_name, engine, columns=pk_columns)
                                
                                # Prepara para o merge anti-join
                                df_to_insert = df.merge(existing_pks_df, on=pk_columns, how='left', indicator=True)
                                df_to_insert = df_to_insert[df_to_insert['_merge'] == 'left_only'].drop(columns=['_merge'])
                            else:
                                # Se não há chave primária, não é possível verificar duplicatas existentes
                                df_to_insert = df

                            # Garante que apenas colunas existentes no BD sejam inseridas
                            db_columns = [c['name'] for c in inspector.get_columns(table_name)]
                            df_to_insert = df_to_insert[[col for col in df.columns if col in db_columns]]

                            # Salva apenas os dados novos
                            if not df_to_insert.empty:
                                df_to_insert.to_sql(table_name, engine, if_exists='append', index=False)
                            
                            files_processed += 1
                        else:
                            st.warning(f"A tabela '{table_name}' não existe no banco de dados. Pulando...")

                except Exception as e:
                    st.error(f"Erro ao processar a tabela {table_name}: {e}")
                    files_with_errors += 1
    
    if files_processed > 0:
        st.success(f"{files_processed} arquivo(s) processado(s) e salvo(s) no banco de dados com sucesso!")
    elif files_with_errors == 0:
        st.warning("Nenhum arquivo novo foi selecionado para processamento.")

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