"""
Sistema de autenticação do dashboard Argus.
Os usuários são cadastrados via variáveis de ambiente (.env).
Formato: DASH_USERS=usuario1:senha1,usuario2:senha2
"""
import streamlit as st
import os
import hashlib
from dotenv import load_dotenv

load_dotenv()


def carregar_usuarios():
    """Lê credenciais do .env e retorna dict {usuario: senha}."""
    raw = os.getenv('DASH_USERS', '')
    if not raw:
        return {}

    usuarios = {}
    for par in raw.split(','):
        if ':' in par:
            user, senha = par.split(':', 1)
            usuarios[user.strip()] = senha.strip()
    return usuarios


def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


def validar_credenciais(usuario, senha):
    usuarios = carregar_usuarios()
    return usuarios.get(usuario) == senha


def tela_login():
    """Renderiza a tela de login. Retorna True se autenticado."""
    if 'autenticado' in st.session_state and st.session_state.autenticado:
        return True

    # Layout centralizado
    st.markdown("""
        <style>
            .login-container {
                max-width: 400px;
                margin: 0 auto;
                padding: 40px;
                margin-top: 80px;
            }
            .login-title {
                font-family: 'Georgia', serif;
                font-size: 48px;
                color: #00ff88;
                text-align: center;
                letter-spacing: 3px;
                margin-bottom: 8px;
            }
            .login-subtitle {
                text-align: center;
                color: #8a99b0;
                letter-spacing: 2px;
                font-size: 11px;
                margin-bottom: 40px;
            }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-title">ARGUS</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">REVENUE INTELLIGENCE</div>', unsafe_allow_html=True)

        with st.form("login_form"):
            usuario = st.text_input("Usuário", placeholder="Digite seu usuário")
            senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            submit = st.form_submit_button("Entrar", use_container_width=True)

            if submit:
                if validar_credenciais(usuario, senha):
                    st.session_state.autenticado = True
                    st.session_state.usuario = usuario
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos")

        st.markdown(
            '<div style="text-align: center; color: #556; font-size: 11px; margin-top: 32px;">'
            'Acesso restrito • Credenciais fornecidas pelo administrador'
            '</div>',
            unsafe_allow_html=True
        )

    return False


def logout_button():
    if st.sidebar.button("Sair", use_container_width=True):
        st.session_state.autenticado = False
        st.session_state.usuario = None
        st.rerun()