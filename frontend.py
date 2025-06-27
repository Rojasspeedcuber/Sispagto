# frontend.py

import streamlit as st
import pandas as pd
from datetime import date

# Importa os módulos do nosso projeto
from database import SessionLocal, engine
from models import Base, Credor, ProdutosServicos, Contrato
import logic
import reports
import locale
# Cria as tabelas no banco de dados na primeira execução
Base.metadata.create_all(bind=engine)

# Função para obter a sessão do banco de dados
def get_session():
    return SessionLocal()

st.set_page_config(page_title="SISPAGTO", layout="wide")

st.title("SISPAGTO - Sistema de Controle de Pagamentos")
st.markdown("Aplicação para gestão de pagamentos do Departamento Administrativo Financeiro.")

# --- BARRA LATERAL DE NAVEGAÇÃO ---
st.sidebar.title("Navegação")
page = st.sidebar.radio("Selecione a operação", [
    "Registrar Pagamento",
    "Gerar Relatório",
    "Cadastrar Credor",
    "Cadastrar Produto/Serviço",
    "Cadastrar Contrato"
])

# --- PÁGINA: CADASTRAR CREDOR ---
def page_add_credor():
    st.header("Cadastrar Novo Credor")
    with st.form("credor_form", clear_on_submit=True):
        doc = st.text_input("CPF/CNPJ do Credor *")
        name = st.text_input("Nome do Credor *")
        submitted = st.form_submit_button("Cadastrar Credor")

        if submitted:
            if not doc or not name:
                st.warning("Por favor, preencha todos os campos obrigatórios (*).")
            else:
                try:
                    db = get_session()
                    logic.create_credor(db, credor_doc=doc, nome=name)
                    st.success(f"Credor '{name}' cadastrado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao cadastrar credor: {e}")
                finally:
                    db.close()

# --- PÁGINA: CADASTRAR PRODUTO/SERVIÇO ---
def page_add_product():
    st.header("Cadastrar Novo Produto/Serviço")
    with st.form("product_form", clear_on_submit=True):
        description = st.text_input("Descrição do Produto/Serviço *")
        # ALTERAÇÃO: Input de valor em Reais (float)
        value = st.number_input("Valor Unitário (em R$) *", min_value=0.0, step=0.01, format="%.2f")
        submitted = st.form_submit_button("Cadastrar Produto")

        if submitted:
            if not description or value <= 0:
                st.warning("Por favor, preencha a descrição e um valor maior que zero.")
            else:
                try:
                    db = get_session()
                    # ALTERAÇÃO: Converte o valor para centavos (int) antes de enviar para a lógica
                    logic.create_produto_servico(db, descricao=description, valor=int(value * 100))
                    st.success(f"Produto '{description}' cadastrado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao cadastrar produto: {e}")
                finally:
                    db.close()

# --- PÁGINA: CADASTRAR CONTRATO ---
def page_add_contract():
    st.header("Cadastrar Novo Contrato")
    db = get_session()
    credores = db.query(Credor).all()
    credor_options = {f"{c.credor_nome} ({c.credor_doc})": c.credor_doc for c in credores}
    db.close()

    if not credor_options:
        st.warning("Nenhum credor cadastrado. Por favor, cadastre um credor primeiro.")
        return

    with st.form("contract_form", clear_on_submit=True):
        number = st.text_input("Número do Contrato *")
        credor_display = st.selectbox("Credor *", list(credor_options.keys()))
        start_date = st.date_input("Data de Início da Vigência *",format="DD/MM/YYYY", value=date.today())
        end_date = st.date_input("Data de Término da Vigência *",format="DD/MM/YYYY", value=date.today())
        # ALTERAÇÃO: Input de valor em Reais (float)
        value = st.number_input("Valor Global do Contrato (em R$) *", min_value=0.0, step=0.01, format="%.2f")
        submitted = st.form_submit_button("Cadastrar Contrato")

        if submitted:
            creditor_doc = credor_options[credor_display]
            if not all([number, creditor_doc, start_date, end_date]) or value <= 0:
                st.warning("Por favor, preencha todos os campos obrigatórios (*).")
            else:
                try:
                    db = get_session()
                    # ALTERAÇÃO: Converte o valor para centavos (int) antes de enviar para a lógica
                    logic.create_contrato(db, contrato_n=number, credor_doc=creditor_doc,
                                          data_ini=start_date.strftime('%Y-%m-%d'),
                                          data_fim=end_date.strftime('%Y-%m-%d'),
                                          valor=int(value * 100))
                    st.success(f"Contrato '{number}' cadastrado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao cadastrar contrato: {e}")
                finally:
                    db.close()

# --- PÁGINA: REGISTRAR PAGAMENTO ---
def page_add_payment():
    st.header("Registrar Novo Pagamento")
    db = get_session()
    credores = db.query(Credor).all()
    produtos = db.query(ProdutosServicos).all()
    contratos = db.query(Contrato).all()
    db.close()

    credor_options = {f"{c.credor_nome} ({c.credor_doc})": c.credor_doc for c in credores}
    # O display do produto já estava correto, mostrando o valor em R$
    produto_options = {f"{p.prod_serv_descricao} (R$ {p.prod_serv_valor/100:.2f})": p.prod_serv_n for p in produtos}
    contrato_options = {"Nenhum": None}
    contrato_options.update({c.contrato_n: c.contrato_n for c in contratos})

    if not credor_options or not produto_options:
        st.warning("É necessário ter ao menos um credor e um produto/serviço cadastrado para registrar um pagamento.")
        return

    with st.form("payment_form", clear_on_submit=True):
        st.subheader("Detalhes do Pagamento")
        date_pagto = st.date_input("Data do Pagamento *",format="DD/MM/YYYY", value=date.today())
        period = st.text_input("Período Orçamentário *", placeholder="Ex: 2025-06")
        # ALTERAÇÃO: Input de valor em Reais (float)
        value = st.number_input("Valor do Pagamento (em R$) *", min_value=0.01, step=0.01, format="%.2f")
        quantity = st.number_input("Quantidade de Produto/Serviço *", min_value=1, step=1)

        st.subheader("Associações")
        credor_display = st.selectbox("Credor *", list(credor_options.keys()))
        produto_display = st.selectbox("Produto/Serviço *", list(produto_options.keys()))
        contract_number = st.selectbox("Contrato (Opcional)", list(contrato_options.keys()))

        st.subheader("Documento de Cobrança (Opcional)")
        payment_type = st.selectbox("Tipo de Documento", ["Nenhum", "NF", "Recibo", "Fatura", "Boleto"])
        doc_number = st.text_input("Número do Documento (se aplicável)")
        doc_date = st.date_input("Data do Documento (se aplicável)",format="DD/MM/YYYY", value=date.today())

        submitted = st.form_submit_button("Registrar Pagamento")

        if submitted:
            creditor_doc = credor_options[credor_display]
            product_id = produto_options[produto_display]
            selected_contract = contrato_options[contract_number]

            if not all([date_pagto, period, creditor_doc, product_id]) or value <= 0 or quantity <= 0:
                st.warning("Por favor, preencha todos os campos obrigatórios de pagamento.")
            else:
                try:
                    db = get_session()
                    # ALTERAÇÃO: Converte o valor para centavos (int) antes de enviar para a lógica
                    logic.create_payment(
                        db, data=date_pagto.strftime('%d-%m-%Y'), periodo=period, valor=int(value * 100),
                        prod_serv_n=product_id, prod_serv_qtd=int(quantity), credor_doc=creditor_doc,
                        contrato_n=selected_contract, tipo_pagamento=payment_type.lower() if payment_type != "Nenhum" else None,
                        doc_n=doc_number, doc_data=doc_date.strftime('%d-%m-%Y')
                    )
                    st.success("Pagamento registrado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao registrar pagamento: {e}")
                finally:
                    db.close()


# --- PÁGINA: GERAR RELATÓRIO ---
def page_generate_report():
    st.header("Gerar Relatório de Pagamentos")
    db = get_session()
    credores = db.query(Credor).all()
    contratos = db.query(Contrato).all()
    db.close()

    credor_options = {"Todos": None}
    credor_options.update({f"{c.credor_nome} ({c.credor_doc})": c.credor_doc for c in credores})
    contrato_options = {"Todos": None}
    contrato_options.update({c.contrato_n: c.contrato_n for c in contratos})

    with st.expander("Filtros do Relatório"):
        start_date = st.date_input("Data Inicial",format="DD/MM/YYYY", value=None)
        end_date = st.date_input("Data Final",format="DD/MM/YYYY", value=None)
        period = st.text_input("Período do Pagamento")
        credor_display = st.selectbox("Credor", list(credor_options.keys()))
        contract_number = st.selectbox("Contrato", list(contrato_options.keys()))

    if st.button("Gerar Relatório"):
        with st.spinner("Gerando relatório..."):
            db = get_session()
            try:
                report_file = reports.generate_report(
                    db,
                    data_inicio=start_date.strftime('%Y-%m-%d') if start_date else None,
                    data_fim=end_date.strftime('%Y-%m-%d') if end_date else None,
                    periodo=period if period else None,
                    credor_doc=credor_options[credor_display],
                    contrato_n=contrato_options[contract_number]
                )

                st.success(f"Relatório gerado com sucesso!")
                df = pd.read_excel(report_file)
                
                # ALTERAÇÃO: Formata a coluna de valor para exibição em R$
                if 'Valor' in df.columns and pd.api.types.is_numeric_dtype(df['Valor']):
                     st.dataframe(df.style.format({"Valor": "R$ {:,.2f}"}))
                else:
                    st.dataframe(df)

                with open(report_file, "rb") as file:
                    st.download_button(
                        label="Baixar Relatório em Excel",
                        data=file,
                        file_name="relatorio_pagamentos.xlsx",
                        mime="application/vnd.ms-excel"
                    )
            except Exception as e:
                st.error(f"Erro ao gerar relatório: {e}")
            finally:
                db.close()


# --- ROTEADOR PRINCIPAL ---
if page == "Cadastrar Credor":
    page_add_credor()
elif page == "Cadastrar Produto/Serviço":
    page_add_product()
elif page == "Cadastrar Contrato":
    page_add_contract()
elif page == "Registrar Pagamento":
    page_add_payment()
elif page == "Gerar Relatório":
    page_generate_report()