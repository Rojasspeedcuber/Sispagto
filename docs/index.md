# Documentação do Projeto: SisPagto - Sistema de Controle de Pagamentos

## 1. Visão Geral

O **SisPagto** é uma aplicação web desenvolvida em Python com a biblioteca Streamlit. O sistema tem como objetivo principal gerenciar e controlar os pagamentos efetuados por um departamento financeiro, com base em um modelo de dados detalhado que inclui pagamentos, contratos, credores, produtos e outros documentos fiscais.

A aplicação permite que o usuário:
-   **Carregue dados** de diversas tabelas a partir de arquivos CSV.
-   **Cadastre** novas entidades como Credores, Produtos, Contratos e Pagamentos.
-   **Gere relatórios** dinâmicos e filtráveis sobre os pagamentos.
-   **Exporte** os relatórios para o formato Excel (`.xlsx`).

## 2. Estrutura de Arquivos do Projeto

O projeto é organizado da seguinte forma para garantir modularidade e clareza:

sispagto/│├── 📂 data/│   └── (Vazio ou com banco de dados, se implementado)│├── 📂 pages/│   ├── 1_✔️_Cadastros.py        # Página para cadastrar novas entidades.│   ├── 2_📊_Relatórios.py       # Página para visualizar e filtrar os pagamentos.│   └── 3_⬆️_Upload_de_Tabelas.py # Página para fazer o upload de dados via CSV.│├── 🏠_Home.py                   # Página inicial da aplicação.│└── requirements.txt             # Arquivo com as dependências do projeto.
-   **`pages/`**: Diretório especial do Streamlit onde cada arquivo `.py` se torna uma página navegável na barra lateral da aplicação.
-   **`🏠_Home.py`**: O arquivo principal que serve como página de entrada.
-   **`requirements.txt`**: Lista todas as bibliotecas Python necessárias para a execução do projeto.

## 3. Configuração e Execução

Para executar o projeto em um ambiente local, siga os passos abaixo.

### 3.1. Pré-requisitos

-   Python 3.8 ou superior instalado.

### 3.2. Passos para Execução

1.  **Clone ou baixe o projeto** para o seu computador.
2.  **Crie um ambiente virtual** (recomendado) para isolar as dependências:
    ```bash
    python -m venv .venv
    ```
3.  **Ative o ambiente virtual**:
    -   **Windows:** `.venv\Scripts\activate`
    -   **macOS/Linux:** `source .venv/bin/activate`
4.  **Instale as dependências** listadas no `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```
5.  **Execute a aplicação** com o comando do Streamlit:
    ```bash
    streamlit run 🏠_Home.py
    ```
Após a execução, uma aba será aberta no seu navegador com a aplicação rodando.

## 4. Funcionalidades Detalhadas

A aplicação é dividida em quatro páginas principais.

### 4.1. ⬆️ Upload de Tabelas

Esta é a porta de entrada dos dados.
-   **Objetivo**: Carregar os dados de todas as tabelas do sistema (PAGTO, CREDOR, NF, etc.) a partir de arquivos CSV.
-   **Funcionamento**:
    1.  O usuário visualiza um campo de upload para cada tabela necessária.
    2.  Ele seleciona os arquivos CSV correspondentes. É crucial que o delimitador dos arquivos seja ponto e vírgula (`;`).
    3.  Ao clicar em "Processar Arquivos Carregados", o sistema lê cada arquivo e armazena os dados em `DataFrames` do Pandas.
    4.  Esses `DataFrames` são salvos no estado da sessão do Streamlit (`st.session_state`), tornando-os acessíveis em todas as outras páginas da aplicação.
    5.  Uma tabela de status informa quais dados foram carregados com sucesso.

### 4.2. ✔️ Cadastros

Esta página permite a inserção de novos registros no sistema.
-   **Objetivo**: Adicionar novos credores, produtos, contratos e pagamentos.
-   **Funcionamento**:
    -   A página é dividida em abas para cada tipo de cadastro.
    -   Os formulários são preenchidos pelo usuário.
    -   As listas de seleção (como "Credor" ou "Produtos") são populadas dinamicamente com os dados carregados na aba de Upload.
    -   Ao submeter um formulário, o novo registro é adicionado ao `DataFrame` correspondente no `st.session_state`. Isso simula uma inserção em um banco de dados, atualizando os dados em tempo real para a sessão atual do usuário.
    -   Abaixo de cada formulário, uma tabela exibe os registros atuais.

### 4.3. 📊 Relatórios

O coração da visualização de dados do sistema.
-   **Objetivo**: Apresentar uma planilha consolidada de pagamentos, permitindo filtros e exportação.
-   **Funcionamento**:
    1.  A página primeiro verifica se as tabelas essenciais (Pagamentos, Credores, Produtos) foram carregadas.
    2.  Ela une (faz um `merge`) esses `DataFrames` para criar uma visão completa, ligando o pagamento ao nome do credor e à descrição do produto.
    3.  **Tratamento de Dados**: Realiza conversões importantes, como transformar a coluna de valores (que pode ser lida como texto "1.250,50") em um formato numérico (`float`) para permitir cálculos.
    4.  **Filtros**: Na barra lateral, o usuário pode filtrar a planilha por intervalo de datas, credor, contrato e tipo de pagamento.
    5.  **Visualização**: O `DataFrame` filtrado é exibido na tela. Uma métrica no final mostra a soma total dos valores dos pagamentos exibidos.
    6.  **Exportação**: Um botão permite baixar a planilha filtrada como um arquivo `.xlsx`.

### 4.4. 🏠 Home

A página inicial.
-   **Objetivo**: Apresentar o sistema ao usuário e fornecer uma visão geral das suas capacidades.
-   **Conteúdo**: Inclui uma breve descrição do projeto e pode conter imagens ou diagramas, como o modelo de dados.

## 5. Fluxo de Dados

O sistema opera sem um banco de dados persistente, utilizando o `st.session_state` do Streamlit como uma base de dados temporária para cada sessão de usuário.

1.  **Carregamento**: Os dados são carregados na página **Upload** e armazenados como `DataFrames` no `st.session_state`.
2.  **Modificação**: A página de **Cadastros** adiciona novas linhas a esses `DataFrames` no `st.session_state`.
3.  **Leitura**: A página de **Relatórios** lê os `DataFrames` do `st.session_state`, os combina e os exibe.

Esse modelo torna a aplicação leve e fácil de executar, sendo ideal para prototipagem e análise de dados baseada em arquivos.

## 6. Dependências

As bibliotecas Python necessárias estão listadas no arquivo `requirements.txt`:

-   **streamlit**: Para a criação da interface web.
-   **pandas**: Para manipulação de dados e `DataFrames`.
-   **openpyxl**: Necessário para o Pandas escrever arquivos no formato `.xlsx`.


