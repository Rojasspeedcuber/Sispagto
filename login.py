#  Autor: Luan Tenório
#  E-mail: luan.tenorio@recife.pe.gov.br
#  Data de desenvolvimento: 27/07/2025 19:01

# Descrição: Classe App, frontend do sistema do projeto Sispagto.
#  A classe App é responsável por criar a interface do usuário, gerenciar o estado da aplicação e interagir com os dados.

import configparser
import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakAuthenticationError

# Configurações globais
st.set_page_config(
    page_title="SisPagto - Login",
    page_icon="🏠",
    layout="wide"
)

class App:
    
    def __init__(self):
        try:
            global configuracao
            global cookies

            # Configuração do Keycloak
            configuracao = configparser.ConfigParser()
            configuracao.read('ignore/config.ini')
            cookies = EncryptedCookieManager(prefix="spgto_", key_params_cookie="data", password=configuracao['cookies']['cookey'])

            # Ícones do App
            st.logo(image=configuracao['app']['img_logo'], icon_image=configuracao['app']['img_icon'])

            if "access_token" not in st.session_state or st.session_state.access_token is None: # o usuário ainda não logou?
                st.session_state.access_token = None
                st.session_state.usuario_id = None
                st.session_state.usuario_nome = None
                st.session_state.usuario_email = None
                st.session_state.usuario_cpf = None
                st.session_state.role = None

                if cookies.ready(): # os cookies estão prontos para leitura?

                    # Atualização de página
                    if cookies.get("access_token") is not None and cookies.get("access_token") != "": # os cookies estão preenchidos?
                        # Armazena os dados do usuário na sessão do Streamlit
                        st.session_state.access_token = cookies.get("access_token")
                        st.session_state["usuario_id"] = cookies.get("usuario_id")
                        st.session_state["usuario_nome"] = cookies.get("usuario_nome")
                        st.session_state["usuario_email"] = cookies.get("usuario_email")
                        st.session_state["usuario_cpf"] = cookies.get('usuario_cpf')
                        st.session_state.role = cookies.get("role")
                        self.run()

                    else: # usuário não está logado nos cookies
                        self.login()
                    
            else: # usuário já está logado
                self.run()

        except Exception as e:
            print(f"Erro ao iniciar o App: {e}")
            pass


    def st_small_screen(self):
        _, col, _ = st.columns([1, 2, 1])
        return col

    def login(self):
        # Configuração Keycloak
        SERVER_URL     = configuracao['keycloak']['server_url']
        REALM          = configuracao['keycloak']['realm']
        CLIENT_ID      = configuracao['keycloak']['client_id']
        CLIENT_SECRET  = configuracao['keycloak']['client_secret']

        keycloak_openid = KeycloakOpenID(
            server_url= SERVER_URL,
            realm_name = REALM,
            client_id = CLIENT_ID,
            client_secret_key = CLIENT_SECRET
        )

        with self.st_small_screen():

            with st.form(key="login_form", clear_on_submit=False, enter_to_submit=True):
            
                st.subheader("Login:")
                usuario = st.text_input("USUÁRIO", key="username")
                senha = st.text_input("SENHA",type="password", key = "password")
                
                btn_submit = st.form_submit_button(label="Login", type="primary")

                if btn_submit:
                    try:
                        # Captura o token de acesso do Keycloak
                        token = keycloak_openid.token(username=usuario,password=senha)
                
                        # Armazena o token de acesso na sessão do Streamlit
                        st.session_state.access_token = token["access_token"]
                
                        # Armazena os dados do usuário na sessão do Streamlit
                        dados_usuario = keycloak_openid.userinfo(st.session_state.access_token)
                        st.session_state["usuario_id"] = dados_usuario["sub"]
                        st.session_state["usuario_nome"] = dados_usuario["name"]
                        st.session_state["usuario_email"] = dados_usuario["email"]
                        st.session_state["usuario_cpf"] = dados_usuario["preferred_username"]
                
                        # Armazena as informações do token para obter o acesso
                        token_info = keycloak_openid.decode_token(token["access_token"])
                        print(token_info)
                        if CLIENT_ID in token_info.get('resource_access', {}):
                            st.session_state.role = str(token_info['resource_access'][CLIENT_ID].get('roles', [])) # string casting
                
                            # Quando st.session_state.role is not None and st.session_state.role != "":
                            # Salva nos cookies
                            cookies['access_token'] = token["access_token"]
                            cookies['usuario_nome'] = st.session_state["usuario_nome"]
                            cookies['usuario_email'] = st.session_state["usuario_email"]
                            cookies['usuario_cpf'] = st.session_state["usuario_cpf"]
                            cookies['usuario_id'] = st.session_state["usuario_id"]
                            cookies['role'] = st.session_state["role"]
                            cookies.save()
                
                        st.rerun()
                
                    except KeycloakAuthenticationError as e:
                        st.error(f"Erro ao realizar o login: {e}")

    def logout(self):
        # Limpa o token da sessão do Streamlit
        for key in ["access_token", "usuario_nome", "usuario_email", "usuario_cpf", "usuario_id", "role"]:
            st.session_state.pop(key, None)
        
        cookies["access_token"] = ""
        cookies["usuario_nome"] = ""
        cookies["usuario_email"] = ""
        cookies["usuario_cpf"] = ""
        cookies["usuario_id"] = ""
        cookies["role"] = ""
        cookies.save()

        with self.st_small_screen():
            st.success("Você foi desconectado.")

        # Redireciona para a página de login
        pg = st.navigation([st.Page(self.login)])
        pg.run()

    def run(self):
        # st.header("Sispagto")

        # Registra as páginas do aplicativo
        pg_home = st.Page(
            "pages_/home.py",
            title="Início",
            icon=":material/account_circle:",
            default=(True)
        )
        pg_account = st.Page(
            "pages_/conta.py",
            title="Conta do Usuário",
            icon=":material/account_circle:"
        )
        pg_logout = st.Page(
            self.logout,
            title="Logout",
            icon=":material/logout:"
        )
        pg_cadastros = st.Page(
            "pages_/cadastros.py",
            title="Cadastros",
            icon=":material/dashboard:"
        )
        pg_relatorios = st.Page(
            "pages_/relatorios.py",
            title="Relatórios",
            icon=":material/dashboard:"
        )
        pg_upload = st.Page(
            "pages_/upload.py",
            title="Uploads de Tabelas",
            icon=":material/dashboard:"
        )


        # Agrupa as páginas do aplicativo em listas. Obs: no Keycloak deve haver a inclusão de um dos grupos de acesso no perfil do usuário
        home_page = [pg_home]
        account_pages = [pg_account, pg_logout]
        dashboard_pages = [pg_cadastros, pg_relatorios, pg_upload]

        page_dict = {}
        
        if st.session_state.role is not None and st.session_state.role != "":
            page_dict.update({"Home": home_page})
            if "PERFIL" in st.session_state.role: # Keycloak: obrigatório para aparecer a página de logout
                page_dict.update({"Conta": account_pages})
            if "RELATORIOS" in st.session_state.role:
                page_dict.update({"Dashboards": dashboard_pages})
                
            
        if len(page_dict) > 0:
            pg = st.navigation(page_dict)
        else:
            st.warning("Usuário sem perfil de acesso")
            pg = st.navigation([st.Page(self.login)])

        pg.run()

if __name__ == '__main__':
    App()