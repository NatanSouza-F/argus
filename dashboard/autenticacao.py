"""
Sistema de autenticação do dashboard Argus.
Tela de login com animação 3D integrada.
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

    # Container principal com duas colunas (animação + formulário)
    col_anim, col_form = st.columns([1.2, 1] if not is_mobile() else [1])

    with col_anim:
        # Animação 3D contínua (carrossel de cards)
        st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
            .login-carousel {
                position: relative;
                width: 100%;
                height: 340px;
                display: flex;
                justify-content: center;
                align-items: center;
                perspective: 1200px;
                margin-top: 30px;
            }
            .login-card {
                position: absolute;
                width: 280px;
                background: rgba(255, 255, 255, 0.85);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 32px;
                padding: 24px 28px;
                box-shadow: 0 25px 35px -10px rgba(0,0,0,0.15);
                text-align: left;
                transform-origin: center center;
                animation: loginSlide 7.5s ease-in-out infinite;
                opacity: 0;
            }
            @keyframes loginSlide {
                0% { transform: translateX(200px) scale(0.8) rotateY(15deg); opacity: 0; z-index: 1; }
                10% { opacity: 0.9; z-index: 5; }
                25% { transform: translateX(0px) scale(1) rotateY(0deg); opacity: 1; z-index: 20; }
                50% { transform: translateX(-70px) scale(0.95) rotateY(-5deg); opacity: 0.8; z-index: 10; }
                75% { transform: translateX(-180px) scale(0.8) rotateY(-12deg); opacity: 0.3; z-index: 1; }
                100% { transform: translateX(200px) scale(0.8) rotateY(15deg); opacity: 0; z-index: 1; }
            }
            .login-card-1 { animation-delay: 0s; }
            .login-card-2 { animation-delay: 1.8s; }
            .login-card-3 { animation-delay: 3.6s; }
            .login-card-4 { animation-delay: 5.4s; }
            .argus-login-title {
                font-family: 'Inter', sans-serif;
                font-size: 3.2rem;
                font-weight: 800;
                background: linear-gradient(135deg, #059669, #00ff88);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-align: center;
                margin-top: 20px;
                letter-spacing: 8px;
                text-shadow: 0 8px 20px rgba(0,255,136,0.15);
            }
            .card-label {
                font-family: 'Inter', sans-serif;
                font-size: 1rem;
                font-weight: 600;
                color: #2c3e50;
                letter-spacing: 0.3px;
                margin-bottom: 8px;
            }
            .card-value {
                font-family: 'Inter', sans-serif;
                font-size: 2.4rem;
                font-weight: 700;
                color: #059669;
                line-height: 1.2;
            }
            .card-trend {
                font-family: 'Inter', sans-serif;
                font-size: 0.9rem;
                color: #64748b;
                margin-top: 10px;
            }
        </style>
        <div class="login-carousel">
            <div class="login-card login-card-1">
                <div class="card-label">📋 LEADS ATIVOS</div>
                <div class="card-value">2.431</div>
                <div class="card-trend">▲ +12% este mês</div>
            </div>
            <div class="login-card login-card-2">
                <div class="card-label">💰 RECEITA (MRR)</div>
                <div class="card-value">R$ 1.2M</div>
                <div class="card-trend">▲ +8.3% vs. anterior</div>
            </div>
            <div class="login-card login-card-3">
                <div class="card-label">🔄 CROSS-SELL</div>
                <div class="card-value">34.7%</div>
                <div class="card-trend">▲ +5.1pp últimos 30d</div>
            </div>
            <div class="login-card login-card-4">
                <div class="card-label">⚠️ EM RISCO</div>
                <div class="card-value">847</div>
                <div class="card-trend" style="color:#e67e22;">▼ -3% redução positiva</div>
            </div>
        </div>
        <div class="argus-login-title">ARGUS</div>
        """, unsafe_allow_html=True)

    with col_form:
        st.markdown("""
        <div style="margin-top: 60px; text-align: center;">
            <h2 style="font-family: 'Inter', sans-serif; font-weight: 600; color: #1e293b;">Acesse sua conta</h2>
            <p style="color: #64748b; margin-bottom: 30px;">Insira suas credenciais</p>
        </div>
        """, unsafe_allow_html=True)
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
        st.caption("Credenciais fornecidas pelo administrador • Ambiente seguro")

    return False


def logout_button():
    if st.sidebar.button("Sair", use_container_width=True):
        st.session_state.autenticado = False
        st.session_state.usuario = None
        st.rerun()
