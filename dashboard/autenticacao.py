"""
Sistema de autenticação do dashboard Argus.
Tela de login com animação 3D integrada e layout glassmorphism.
"""
import streamlit as st
import os
import hashlib
from dotenv import load_dotenv

load_dotenv()


def is_mobile():
    try:
        ua = st.context.headers.get("User-Agent", "")
        return any(x in ua for x in ["Mobile", "Android", "iPhone", "iPad"])
    except:
        return False


def carregar_usuarios():
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
    if 'autenticado' in st.session_state and st.session_state.autenticado:
        return True

    # Estilo específico para a tela de login (consistente com o dashboard)
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        .login-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 1rem;
            background: radial-gradient(circle at 10% 20%, rgba(240, 248, 255, 0.8), rgba(255, 255, 255, 0.95));
        }
        .login-card {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(0, 255, 136, 0.25);
            border-radius: 40px;
            padding: 3rem 2.5rem;
            max-width: 450px;
            width: 100%;
            box-shadow: 0 30px 50px -20px rgba(0,0,0,0.1);
            text-align: center;
        }
        .login-logo {
            font-family: 'Inter', sans-serif;
            font-size: 4rem;
            font-weight: 800;
            background: linear-gradient(135deg, #059669, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 6px;
            margin-bottom: 0.5rem;
        }
        .login-slogan {
            font-family: 'Inter', sans-serif;
            color: #475569;
            font-size: 1rem;
            font-weight: 400;
            margin-bottom: 2.5rem;
            letter-spacing: 0.3px;
        }
        .login-input {
            margin-bottom: 1.5rem;
            text-align: left;
        }
        .login-input label {
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            color: #1e293b;
            font-size: 0.9rem;
            margin-bottom: 0.3rem;
            display: block;
        }
        .login-input input {
            width: 100%;
            padding: 0.8rem 1.2rem;
            background: rgba(255,255,255,0.5);
            border: 1px solid rgba(0,255,136,0.3);
            border-radius: 40px;
            font-family: 'Inter', sans-serif;
            font-size: 1rem;
            outline: none;
            transition: 0.2s;
        }
        .login-input input:focus {
            border-color: #00ff88;
            box-shadow: 0 0 0 3px rgba(0,255,136,0.2);
        }
        .login-btn {
            background: #00ff88;
            color: #0b1e2e;
            border: none;
            border-radius: 60px;
            padding: 0.9rem 1.5rem;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            font-size: 1.1rem;
            width: 100%;
            cursor: pointer;
            transition: 0.2s;
            margin-top: 0.5rem;
        }
        .login-btn:hover {
            background: #00cc6a;
            box-shadow: 0 8px 20px rgba(0,255,136,0.3);
            transform: translateY(-2px);
        }
        .login-footer {
            margin-top: 1.5rem;
            color: #64748b;
            font-size: 0.8rem;
        }
        /* Ajustes mobile */
        @media (max-width: 480px) {
            .login-card {
                padding: 2rem 1.5rem;
            }
            .login-logo {
                font-size: 3rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)

    # Container centralizado
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-card">', unsafe_allow_html=True)

        # Logo e Slogan (escolhido: Transformando dados em receita previsível)
        st.markdown('<div class="login-logo">ARGUS</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-slogan">Transformando dados em receita previsível</div>', unsafe_allow_html=True)

        # Formulário
        with st.form("login_form"):
            st.markdown('<div class="login-input">', unsafe_allow_html=True)
            usuario = st.text_input("Usuário", placeholder="Digite seu usuário", label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="login-input">', unsafe_allow_html=True)
            senha = st.text_input("Senha", type="password", placeholder="Digite sua senha", label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)

            submit = st.form_submit_button("Entrar", use_container_width=True)

            if submit:
                if validar_credenciais(usuario, senha):
                    st.session_state.autenticado = True
                    st.session_state.usuario = usuario
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos")

        st.markdown('<div class="login-footer">Credenciais fornecidas pelo administrador • Ambiente seguro</div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

    return False


def logout_button():
    if st.sidebar.button("Sair", use_container_width=True):
        st.session_state.autenticado = False
        st.session_state.usuario = None
        st.rerun()
