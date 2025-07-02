import streamlit as st
from src.database import inicializar_banco

# Inicializa o banco de dados na primeira execução
inicializar_banco()

st.set_page_config(
    page_title="SisPagto - Início",
    page_icon="🏠",
    layout="wide"
)

st.title("SISTEMA DE CONTROLE DE PAGAMENTOS")
st.markdown("---")

st.header("Bem-vindo!")
st.write(
    """
    Este é o Sistema para controle de pagamentos efetuados pelo Departamento Administrativo Financeiro. [cite: 2]
    
    **Utilize o menu na barra lateral para navegar entre as funcionalidades:**

    - **✔️ Cadastros:** Para inserir novos pagamentos, contratos, credores e produtos.
    - **📊 Relatórios:** Para visualizar, filtrar e exportar a planilha de pagamentos.
    - **⬆️ Upload de Tabelas:** Para carregar dados de pagamentos em lote a partir de um arquivo CSV.
    """
)

st.info("O sistema foi desenvolvido com base na documentação técnica fornecida, implementando todas as tabelas, relacionamentos e regras de negócio especificadas.")

st.image("https://raw.githubusercontent.com/pmarcosf/sispagto/main/img/modelo_dados.png", caption="Modelo de Dados do Sistema [cite: 25]")