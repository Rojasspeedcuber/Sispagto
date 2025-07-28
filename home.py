import streamlit as st
import os
from src.database import inicializar_banco

# Garante que o diretório de dados exista
if not os.path.exists('data'):
    os.makedirs('data')

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
    Este é o Sistema para controle de pagamentos efetuados pelo Departamento Administrativo Financeiro.
    
    Os dados agora são armazenados de forma **permanente**. Utilize o menu na barra lateral para navegar entre as funcionalidades:

    - **⬆️ Upload de Tabelas:** Se for o primeiro uso, comece por aqui para carregar os dados iniciais dos arquivos CSV. Os dados serão salvos e não será necessário carregar os arquivos novamente.
    - **✔️ Cadastros:** Insira novos pagamentos, contratos, credores e produtos diretamente no banco de dados.
    - **📊 Relatórios:** Visualize, filtre e edite a planilha de pagamentos com os dados sempre atualizados do banco de dados.
    """
)

st.info(
    "**Como funciona a persistência de dados?**\n"
    "Ao usar a funcionalidade de 'Upload de Tabelas', os dados dos seus arquivos CSV são salvos em um banco de dados local (SQLite). "
    "A partir desse momento, todo o sistema passa a ler, cadastrar e alterar informações diretamente nesse banco de dados, "
    "garantindo que seus dados não sejam perdidos ao atualizar a página ou fechar o sistema."
)

st.image("https://raw.githubusercontent.com/pmarcosf/sispagto/main/img/modelo_dados.png", caption="Modelo de Dados do Sistema")