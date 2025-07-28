import streamlit as st
import pandas as pd
from src.database import get_session, table_exists, engine
from sqlalchemy import inspect
from io import StringIO

st.set_page_config(layout="wide", page_title="Upload de Tabelas")

st.header("Carga de Dados do Sistema via CSV")

st.info(
    "Faça o upload dos arquivos CSV. O sistema agora ignora automaticamente linhas duplicadas que já existem no banco de dados para evitar erros."
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
                    # Lê o CSV
                    df = pd.read_csv(uploader, sep=';', decimal=',')

                    # ----- Limpeza e Preparação dos Dados -----
                    if 'CONTRATO_LALOR' in df.columns:
                        df.rename(columns={'CONTRATO_LALOR': 'CONTRATO_VALOR'}, inplace=True)
                    for col in df.select_dtypes(include=['object']):
                        df[col] = df[col].astype(str).str.strip("'")

                    with get_session() as session:
                        if table_exists(session, table_name):
                            # Obtém as colunas da chave primária da tabela no BD
                            pk_constraint = inspector.get_pk_constraint(table_name)
                            pk_columns = pk_constraint['constrained_columns'] if pk_constraint else []

                            # ----- Lógica Anti-Duplicidade -----
                            # 1. Remove duplicatas dentro do próprio arquivo CSV
                            if pk_columns:
                                df.drop_duplicates(subset=pk_columns, inplace=True)
                            
                            # 2. Remove linhas do CSV que já existem no banco de dados
                            if pk_columns and not df.empty:
                                existing_pks_df = pd.read_sql_table(table_name, engine, columns=pk_columns)
                                if not existing_pks_df.empty:
                                    # Merge para identificar linhas que já existem
                                    merge_indicator = '_merge_indicator'
                                    df_merged = df.merge(existing_pks_df, on=pk_columns, how='left', indicator=merge_indicator)
                                    # Mantém apenas as linhas que não estão no BD
                                    df_to_insert = df_merged[df_merged[merge_indicator] == 'left_only'].drop(columns=[merge_indicator])
                                else:
                                    df_to_insert = df
                            else:
                                df_to_insert = df # Se não há PK, insere tudo

                            # ----- Inserção no Banco de Dados -----
                            if not df_to_insert.empty:
                                # Garante que apenas colunas existentes no BD sejam inseridas
                                db_columns = [c['name'] for c in inspector.get_columns(table_name)]
                                df_to_insert_filtered = df_to_insert[[col for col in df.columns if col in db_columns]]
                                
                                df_to_insert_filtered.to_sql(table_name, engine, if_exists='append', index=False)
                            
                            files_processed += 1
                        else:
                            st.warning(f"A tabela '{table_name}' não existe no banco de dados. Pulando...")

                except Exception as e:
                    st.error(f"Erro ao processar a tabela {table_name}: {e}")
                    files_with_errors += 1
    
    # Mensagens de feedback ao usuário
    if files_processed > 0 and files_with_errors == 0:
        st.success(f"{files_processed} arquivo(s) foram processados com sucesso! Os dados novos foram salvos.")
    elif files_processed > 0 and files_with_errors > 0:
        st.warning(f"{files_processed} arquivo(s) foram processados, mas ocorreram erros em {files_with_errors} deles. Verifique as mensagens de erro acima.")
    elif files_with_errors == 0:
        st.info("Nenhum arquivo novo foi selecionado ou os arquivos selecionados não continham dados novos para inserir.")

# Exibição do status final do banco de dados
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