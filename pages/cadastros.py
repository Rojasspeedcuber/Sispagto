# pages/1_✔️_Cadastros.py
import streamlit as st
from src import database, business_rules

st.header("Módulo de Cadastros e Edições [cite: 79]")

tab_pagto, tab_contrato, tab_credor, tab_produto = st.tabs([
    "Pagamentos", "Contratos e Aditivos", "Credores", "Produtos/Serviços"
])

with tab_pagto:
    st.subheader("Cadastro de Pagamentos [cite: 80]")
    
    with st.form("form_pagamento", clear_on_submit=True):
        # Campos do formulário baseados na seção 2.1.A do PDF [cite: 81]
        data_pag = st.date_input("Data do pagamento (obrigatório) [cite: 82]")
        periodo = st.text_input("Período do pagamento (obrigatório) [cite: 83]")
        valor = st.number_input("Valor do pagamento (obrigatório) [cite: 85]", format="%.2f")
        
        # Selecionar credor, contrato e produtos de listas vindas do banco
        credores = database.listar_credores()
        credor_selecionado = st.selectbox("Credor (obrigatório) [cite: 88, 102]", options=credores)
        
        tipo_pagamento = st.selectbox("Tipo de pagamento [cite: 89]", ["Nota Fiscal", "Recibo", "Fatura", "Boleto"])
        
        submitted = st.form_submit_button("Cadastrar Pagamento")
        
        if submitted:
            # 1. Chamar as funções de validação das regras de negócio
            valido, msg = business_rules.validar_data_pagamento(data_pag, 'CONTRATO_X')
            if not valido:
                st.error(f"Cadastro impedido! {msg} [cite: 162]")
            else:
                # 2. Se tudo estiver OK, chamar a função de cadastro do banco de dados
                # database.cadastrar_pagamento(...)
                st.success("Pagamento cadastrado com sucesso!")

with tab_contrato:
    st.subheader("Cadastro de Contratos [cite: 107]")
    # Formulário para cadastrar contratos conforme seção 2.1.B [cite: 108]
    # ...

with tab_credor:
    st.subheader("Cadastro de Credores [cite: 131]")
    # Formulário para cadastrar credores conforme seção 2.1.D [cite: 132]
    # ...

with tab_produto:
    st.subheader("Cadastro de Produtos/Serviços [cite: 135]")
    # Formulário para cadastrar produtos conforme seção 2.1.E [cite: 136]
    # ...