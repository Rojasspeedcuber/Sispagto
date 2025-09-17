import streamlit as st

# st.header("Perfil do Usuário")
st.subheader("Dados do Usuário")

# st.write(f"Olá, {st.session_state.usuario_nome}, você está logado como {st.session_state.role}.")
st.write(f"Nome: {st.session_state.usuario_nome}\r\rE-mail: {st.session_state.usuario_email}\r\rCPF: {st.session_state.usuario_cpf}\r\rPerfil: {st.session_state.role}")
