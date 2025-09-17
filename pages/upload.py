import streamlit as st
import pandas as pd
import numpy as np
from src.database import get_session, table_exists, engine
from sqlalchemy import inspect
from io import StringIO

st.set_page_config(layout="wide", page_title="Upload de Tabelas")

st.header("Carga de Dados do Sistema via CSV")

st.info(
    "Faça o upload dos arquivos CSV para popular o banco de dados. "
    "O sistema identificará e inserirá **apenas os registros novos**, ignorando duplicatas que já existam no banco."
)

TABLE_MAP = {
    "CREDOR": "credores_df", "PRODUTOS_SERVICOS": "produtos_servicos_df",
    "LISTA_ITENS": "lista_itens_df", "CONTRATO": "contratos_df",
    "ADITIVOS": "aditivos_df", "NF": "nf_df", "RECIBO": "recibo_df",
    "FATURA": "fatura_df", "BOLETO": "boleto_df", "PAGTO": "pagamentos_df",
}

if 'uploaders' not in st.session_state:
    st.session_state.uploaders = {key: None for key in TABLE_MAP.keys()}

col1, col2, col3 = st.columns(3)
columns = [col1, col2, col3]

for i, table_name in enumerate(TABLE_MAP.keys()):
    with columns[i % 3]:
        st.session_state.uploaders[table_name] = st.file_uploader(
            f"Tabela {table_name}", type="csv", key=f"upload_{table_name}"
        )

if st.button("✔️ Processar e Salvar no Banco de Dados", use_container_width=True, type="primary"):
    with st.spinner("Analisando e salvando dados... Por favor, aguarde."):
        files_processed, files_with_errors = 0, 0
        inspector = inspect(engine)

        for table_name, uploader in st.session_state.uploaders.items():
            if uploader is not None:
                try:
                    df = pd.read_csv(uploader, sep=';', decimal=',')
                    
                    # --- Lógica para determinar o PAGTO_TIPO automaticamente ---
                    if table_name == 'PAGTO':
                        doc_cols = ['NF_N', 'RECIBO_N', 'FATURA_N', 'BOLETO_N']
                        # Garante que as colunas de documento sejam tratadas como texto
                        for col in doc_cols:
                            if col in df.columns:
                                df[col] = df[col].astype(str).str.strip().str.lower().replace('nan', '')

                        # Define as condições e os tipos de pagamento correspondentes
                        conditions = [
                            (df['NF_N'].notna() & (df['NF_N'] != '')),
                            (df['RECIBO_N'].notna() & (df['RECIBO_N'] != '')),
                            (df['FATURA_N'].notna() & (df['FATURA_N'] != '')),
                            (df['BOLETO_N'].notna() & (df['BOLETO_N'] != ''))
                        ]
                        choices = ['Nota Fiscal', 'Recibo', 'Fatura', 'Boleto']
                        
                        # Cria a coluna PAGTO_TIPO com base nas condições
                        df['PAGTO_TIPO'] = np.select(conditions, choices, default='Outro')


                    # --- Limpeza e Preparação ---
                    if 'CONTRATO_LALOR' in df.columns:
                        df.rename(columns={'CONTRATO_LALOR': 'CONTRATO_VALOR'}, inplace=True)
                    for col in df.select_dtypes(include=['object']):
                        df[col] = df[col].astype(str).str.strip("'")

                    with get_session() as session:
                        if table_exists(session, table_name):
                            pk_constraint = inspector.get_pk_constraint(table_name)
                            pk_columns = pk_constraint['constrained_columns'] if pk_constraint else []
                            pk_cols_in_df = [col for col in pk_columns if col in df.columns]

                            # --- Lógica Anti-Duplicidade ---
                            df_to_insert = df
                            if pk_cols_in_df:
                                df.drop_duplicates(subset=pk_cols_in_df, inplace=True)
                                try:
                                    existing_pks_df = pd.read_sql_table(table_name, engine, columns=pk_cols_in_df)
                                    if not existing_pks_df.empty:
                                        merge_indicator = '_merge'
                                        df_merged = df.merge(existing_pks_df, on=pk_cols_in_df, how='left', indicator=merge_indicator)
                                        df_to_insert = df_merged[df_merged[merge_indicator] == 'left_only'].drop(columns=[merge_indicator])
                                except Exception: # Tabela vazia
                                    pass
                            
                            # --- Inserção Final ---
                            if not df_to_insert.empty:
                                db_columns = [c['name'] for c in inspector.get_columns(table_name)]
                                df_final = df_to_insert[[col for col in df_to_insert.columns if col in db_columns]]
                                df_final.to_sql(table_name, engine, if_exists='append', index=False)
                            
                            files_processed += 1
                        else:
                            st.warning(f"Tabela '{table_name}' não encontrada. Pulando...")
                except Exception as e:
                    st.error(f"Erro ao processar '{table_name}': {e}")
                    files_with_errors += 1
    
    if files_processed > 0 and files_with_errors == 0:
        st.success(f"Operação concluída! {files_processed} arquivo(s) foram checados e os dados novos foram salvos no banco de dados.")
    elif files_processed > 0:
        st.warning(f"{files_processed} arquivo(s) processados, mas ocorreram erros em {files_with_errors}. Verifique as mensagens.")
    elif files_with_errors == 0:
        st.info("Nenhum arquivo foi selecionado ou os arquivos não continham dados novos para inserir.")

st.markdown("---")
st.subheader("Status do Banco de Dados")
status_data = []
with get_session() as session:
    for table_name in TABLE_MAP.keys():
        status, info = ("⚠️ Pendente", "Tabela não encontrada")
        if table_exists(session, table_name):
            try:
                count = pd.read_sql(f"SELECT COUNT(*) FROM {table_name}", engine).iloc[0,0]
                status, info = ("✅ Carregado", f"{count} linhas")
            except Exception as e:
                status, info = ("❌ Erro", str(e))
        status_data.append({"Tabela": table_name, "Status": status, "Info": info})
st.dataframe(pd.DataFrame(status_data), use_container_width=True)