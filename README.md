# SisPagto

O SisPagto é uma aplicação web em Streamlit para registrar e consultar pagamentos de um departamento administrativo-financeiro. Os dados ficam em um banco SQLite local. A interface oferece carga de arquivos CSV, formulários de cadastro e uma página de relatórios com filtros e edição de registros.

## Estrutura e dados

- `home.py` inicia a aplicação e cria as tabelas do banco, caso ainda não existam.
- `pages/upload.py` recebe arquivos CSV e insere registros nas tabelas.
- `pages/cadastros.py` cadastra pagamentos, contratos, credores e produtos/serviços; também permite editar contratos, credores e produtos/serviços.
- `pages/relatorios.py` consulta pagamentos e outras tabelas, aplica filtros e permite editar parte dos campos de pagamento.
- `src/database.py` define os modelos SQLAlchemy e a conexão com `data/sispagto.db`; `src/business_rules.py` contém validações, algumas ainda incompletas.

O repositório já contém `data/sispagto.db`. A aplicação usa o caminho relativo `data/sispagto.db`, portanto execute os comandos a partir da raiz do projeto. Faça uma cópia do banco antes de importar ou editar dados importantes. O banco é persistente entre execuções locais, mas não é um serviço compartilhado nem substitui uma rotina de backup.

## Pré-requisitos e execução local

Use Python com suporte às versões fixadas em `requirements.txt` (a resolução das dependências foi verificada com Python 3.12). É necessário ter `venv` e `pip` disponíveis na instalação do Python. Na raiz do repositório:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run home.py
```

No Windows, crie o ambiente com `py -m venv .venv` e ative-o com `.venv\Scripts\activate` (Prompt de Comando) ou `.venv\Scripts\Activate.ps1` (PowerShell). Depois, execute os dois últimos comandos no ambiente ativado. Abra o endereço local informado pelo Streamlit.

Não há configuração de credenciais ou serviço externo para o fluxo de dados descrito no código. O arquivo `requirements.txt` inclui dependências de documentação e integração que não são usadas diretamente pelas páginas atuais. Existe também `mkdocs.yml` para a documentação em `docs/`, mas `docs/index.md` descreve uma implementação anterior baseada em estado de sessão; para persistência e nomes de arquivos, consulte o código e este README.

## Uso

1. Na página **Upload**, selecione os CSVs das tabelas que deseja carregar e clique em **Processar e Salvar no Banco de Dados**. O código lê arquivos separados por ponto e vírgula (`;`) com vírgula decimal e espera nomes de colunas compatíveis com `src/database.py`. Cada campo de upload corresponde a uma tabela: `CREDOR`, `PRODUTOS_SERVICOS`, `LISTA_ITENS`, `CONTRATO`, `ADITIVOS`, `NF`, `RECIBO`, `FATURA`, `BOLETO` ou `PAGTO`. A carga compara chaves primárias presentes no CSV com as do banco para tentar ignorar registros existentes; arquivos incompatíveis geram erro na interface. Se houver dependências entre tabelas, carregue primeiro os registros referenciados, como credores antes de contratos. Para `PAGTO`, a coluna `PAGTO_TIPO` é derivada dos campos `NF_N`, `RECIBO_N`, `FATURA_N` e `BOLETO_N`; o arquivo precisa conter esses campos. Não há arquivos CSV de exemplo no repositório.
2. Em **Cadastros**, adicione credores, produtos/serviços, contratos e pagamentos pelos formulários. O cadastro de contrato e pagamento usa credores já existentes. As tabelas editáveis dessa página permitem salvar alterações em credores, contratos e produtos/serviços.
3. Em **Relatórios**, consulte pagamentos e filtre por datas, credor, período, tipo e contrato. A grade permite editar data, período, tipo, valor e contrato de pagamentos, com gravação pelo botão de salvar. A página também apresenta quadros de contratos, credores e produtos/serviços.

## Testes e limitações conhecidas

Não há suíte de testes automatizados nem comando de testes configurado no repositório. Para uma verificação básica, rode a aplicação com o comando acima e confira as páginas pela interface antes de usar dados de produção. Em Linux/macOS, a falha dos caminhos de imagem da página inicial descrita abaixo impede que ela termine de carregar; corrigir esses caminhos exige uma alteração no código, fora do escopo deste README.

- As funções de validação de data e valor de pagamento em `src/business_rules.py` ainda retornam sucesso sem consultar contratos ou saldos; não trate esses controles como implementados.
- Em `pages/relatorios.py`, a métrica dos pagamentos filtrados e o botão de exportação para Excel estão dentro do bloco condicionado à existência de edições na grade. Eles podem não aparecer na consulta normal, apesar de haver código de exportação.
- `home.py` usa barras invertidas nos caminhos de duas imagens locais; em Linux/macOS, a primeira delas causa erro ao abrir a página inicial. O diagrama da página inicial é carregado de uma URL externa.
- O banco SQLite versionado em `data/` pode conter registros existentes; não publique dados sensíveis nele sem revisar o histórico e a política de acesso ao repositório.
