
# SISPAGTO - Sistema de Controle de Pagamentos

""`SISPAGTO` é um sistema para controle de pagamentos efetuados pelo Departamento Administrativo Financeiro, conforme as especificações da Emprel[cite: 1]. A aplicação foi desenvolvida em Python e utiliza uma interface web interativa para facilitar a gestão de dados.

## Funcionalidades Principais

  * ""**Cadastro de Pagamentos:** Permite o registro detalhado de cada pagamento, associando-o a credores, produtos e contratos[cite: 25].
  * **Gestão de Entidades:** Cadastro completo de Credores [cite: 51], Contratos [cite: 41], Produtos/Serviços [cite: 52] e Aditivos[cite: 47].
  * ""**Geração de Relatórios:** Emissão de relatórios em formato de planilha (`.xlsx`) com opções de filtros dinâmicos, como intervalo de datas, período, credor e contrato[cite: 59, 62, 64].
  * ""**Validação de Regras de Negócio:** O sistema impede o cadastro de dados inconsistentes, garantindo a integridade das informações[cite: 65]. Por exemplo:
      * ""Um pagamento não pode ser registrado com data fora da vigência do contrato associado[cite: 66].
      * ""O valor de um pagamento não pode exceder o saldo disponível no contrato[cite: 66].
      * ""A data de término de um contrato não pode ser anterior à sua data de início[cite: 68].
  * **Interface Gráfica Web:** Uma interface de usuário moderna e intuitiva desenvolvida com Streamlit para facilitar a interação com o sistema.

## Tecnologias Utilizadas

  * **Backend:** Python 3
  * **Interface Web:** Streamlit
  * **Banco de Dados:** SQLite
  * **Mapeamento Objeto-Relacional (ORM):** SQLAlchemy
  * **Manipulação de Dados e Relatórios:** Pandas

## Estrutura do Projeto

O projeto está organizado da seguinte forma para separar as responsabilidades:

```
sispagto/
├── frontend.py           # Aplicação web principal (interface gráfica)
├── logic.py              # Contém a lógica e as regras de negócio [cite: 65]
├── models.py             # Define as tabelas do banco de dados (ORM) [cite: 1]
├── reports.py            # Lógica para a geração dos relatórios em Excel [cite: 59]
├── database.py           # Configuração da conexão com o banco de dados
├── app.py                # (Opcional) Interface de linha de comando legada
├── requirements.txt      # Lista de dependências do projeto
└── sispagto.db           # Arquivo do banco de dados (gerado na 1ª execução)
```

## Instalação e Execução

Siga os passos abaixo para configurar e executar o projeto em seu ambiente local.

### Pré-requisitos

  * Python 3.8 ou superior

### Passos

1.  **Clone o repositório:**

    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    cd sispagto
    ```

2.  **Crie e ative um ambiente virtual (Recomendado):**

      * **Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
      * **macOS / Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Instale as dependências:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute a aplicação:**

    ```bash
    streamlit run frontend.py
    ```

    Após executar o comando, uma nova aba será aberta automaticamente em seu navegador com a aplicação web em funcionamento.

## Como Usar o Sistema

A navegação principal é feita pela barra lateral à esquerda, onde você pode selecionar a operação desejada.

### 1\. Cadastros Iniciais

Antes de registrar pagamentos ou contratos, é necessário ter dados básicos no sistema.

  * ""**Cadastrar Credor:** Use esta página para adicionar os credores (fornecedores)[cite: 51].
  * ""**Cadastrar Produto/Serviço:** Cadastre os produtos ou serviços que serão objeto dos pagamentos[cite: 52].

### 2\. Cadastro de Contrato

Com credores e produtos já cadastrados:

1.  Navegue para **"Cadastrar Contrato"**.
2.  ""Preencha os dados do contrato, como número, datas de vigência, valor global e o credor associado[cite: 41].

### 3\. Registro de Pagamentos

Esta é a operação principal do dia a dia.

1.  Navegue para **"Registrar Pagamento"**.
2.  ""Preencha o formulário com os dados do pagamento, como data, valor, período, e selecione o credor e o produto/serviço correspondente[cite: 25].
3.  ""Opcionalmente, associe o pagamento a um contrato já existente e forneça detalhes do documento de cobrança (Nota Fiscal, Boleto, etc.)[cite: 25].

### 4\. Geração de Relatórios

1.  Navegue para **"Gerar Relatório"**.
2.  ""Utilize os filtros no topo da página para refinar sua busca por data, credor ou contrato[cite: 63].
3.  Clique em **"Gerar Relatório"** para visualizar os dados na tela.
4.  ""Clique em **"Baixar Relatório em Excel"** para fazer o download da planilha no formato `.xlsx`[cite: 64].