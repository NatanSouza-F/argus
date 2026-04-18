"""
Sistema de autenticação do dashboard Argus.
Tela de login com todos os elementos contidos em um único quadro centralizado.
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

    # Container principal que envolve TUDO (o "quadro vermelho")
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        /* Fundo da página */
        .stApp {
            background: radial-gradient(circle at 10% 20%, rgba(240, 248, 255, 0.8), rgba(255, 255, 255, 0.95));
        }
        
        /* Wrapper centralizador */
        .login-outer {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 20px;
        }
        
        /* O QUADRO PRINCIPAL (glassmorphism) */
        .login-main-card {
            max-width: 1000px;
            width: 100%;
            background: rgba(255, 255, 255, 0.5);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(0, 255, 136, 0.2);
            border-radius: 48px;
            padding: 2rem 1.8rem;
            box-shadow: 0 30px 50px -20px rgba(0,0,0,0.1);
        }
        
        /* Grid interno: duas colunas perfeitamente alinhadas */
        .login-grid {
            display: flex;
            flex-wrap: wrap;
            align-items: center;      /* centraliza verticalmente */
            gap: 1.5rem;
        }
        
        .login-left {
            flex: 1.2;
            min-width: 280px;
        }
        
        .login-right {
            flex: 1;
            min-width: 260px;
        }
        
        /* Carrossel */
        .login-carousel {
            position: relative;
            width: 100%;
            height: 260px;
            display: flex;
            justify-content: center;
            align-items: center;
            perspective: 1200px;
            margin-bottom: 15px;
        }
        .login-card {
            position: absolute;
            width: 250px;
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 28px;
            padding: 18px 22px;
            box-shadow: 0 20px 30px -10px rgba(0,0,0,0.1);
            text-align: left;
            transform-origin: center center;
            animation: loginSlide 7.5s ease-in-out infinite;
            opacity: 0;
        }
        @keyframes loginSlide {
            0% { transform: translateX(180px) scale(0.8) rotateY(15deg); opacity: 0; z-index: 1; }
            10% { opacity: 0.9; z-index: 5; }
            25% { transform: translateX(0px) scale(1) rotateY(0deg); opacity: 1; z-index: 20; }
            50% { transform: translateX(-60px) scale(0.95) rotateY(-5deg); opacity: 0.8; z-index: 10; }
            75% { transform: translateX(-160px) scale(0.8) rotateY(-12deg); opacity: 0.3; z-index: 1; }
            100% { transform: translateX(180px) scale(0.8) rotateY(15deg); opacity: 0; z-index: 1; }
        }
        .login-card-1 { animation-delay: 0s; }
        .login-card-2 { animation-delay: 1.8s; }
        .login-card-3 { animation-delay: 3.6s; }
        .login-card-4 { animation-delay: 5.4s; }
        
        .argus-title {
            font-family: 'Inter', sans-serif;
            font-size: 2.8rem;
            font-weight: 800;
            background: linear-gradient(135deg, #059669, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            letter-spacing: 5px;
            margin: 0 0 2px 0;
        }
        .argus-slogan {
            font-family: 'Inter', sans-serif;
            font-size: 0.9rem;
            color: #475569;
            text-align: center;
            font-weight: 400;
            letter-spacing: 1px;
        }
        
        .card-label {
            font-family: 'Inter', sans-serif;
            font-size: 0.9rem;
            font-weight: 600;
            color: #2c3e50;
            letter-spacing: 0.3px;
            margin-bottom: 5px;
        }
        .card-value {
            font-family: 'Inter', sans-serif;
            font-size: 1.9rem;
            font-weight: 700;
            color: #059669;
            line-height: 1.2;
        }
        .card-trend {
            font-family: 'Inter', sans-serif;
            font-size: 0.8rem;
            color: #64748b;
            margin-top: 6px;
        }
        
        /* Formulário */
        .login-form-title {
            font-family: 'Inter', sans-serif;
            font-size: 1.7rem;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 0.3rem;
        }
        .login-form-subtitle {
            font-family: 'Inter', sans-serif;
            color: #64748b;
            margin-bottom: 1.8rem;
            font-size: 0.9rem;
        }
        
        /* Inputs proporcionais */
        div[data-baseweb="input"] {
            background: rgba(255, 255, 255, 0.7) !important;
            border: 1px solid rgba(0, 255, 136, 0.35) !important;
            border-radius: 30px !important;
            margin-bottom: 1rem;
            height: 48px !important;
            display: flex;
            align-items: center;
        }
        div[data-baseweb="input"] input {
            color: #1e293b !important;
            font-family: 'Inter', sans-serif !important;
            padding: 0.5rem 1rem !important;
            font-size: 0.95rem !important;
            background: transparent !important;
        }
        div[data-baseweb="input"] input::placeholder {
            color: #94a3b8 !important;
        }
        
        /* Botão */
        .stButton button {
            background: #00ff88 !important;
            color: #0b1e2e !important;
            border-radius: 40px !important;
            font-weight: 600 !important;
            padding: 0.6rem 1.2rem !important;
            width: 100%;
            border: none !important;
            font-size: 1rem;
            height: 48px;
            transition: 0.2s;
        }
        .stButton button:hover {
            background: #00cc6a !important;
            box-shadow: 0 8px 20px rgba(0,255,136,0.3);
        }
        
        .login-footer {
            margin-top: 18px;
            color: #64748b;
            font-size: 0.75rem;
            text-align: left;
        }
        
        /* Mobile */
        @media (max-width: 768px) {
            .login-main-card {
                padding: 1.5rem;
            }
            .login-grid {
                flex-direction: column;
                gap: 1rem;
            }
            .login-carousel {
                height: 240px;
            }
            .argus-title {
                font-size: 2.3rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)

    # Estrutura HTML do quadro principal
    st.markdown('<div class="login-outer">', unsafe_allow_html=True)
    st.markdown('<div class="login-main-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-grid">', unsafe_allow_html=True)

    # Coluna da esquerda: carrossel + título
    st.markdown('<div class="login-left">', unsafe_allow_html=True)
    st.markdown("""
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
        <div class="argus-title">ARGUS</div>
        <div class="argus-slogan">A decisão certa começa com inteligência.</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # fecha login-left

    # Coluna da direita: formulário
    st.markdown('<div class="login-right">', unsafe_allow_html=True)
    st.markdown("""
        <div class="login-form-title">Acesse sua conta</div>
        <div class="login-form-subtitle">Insira suas credenciais</div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        usuario = st.text_input("Usuário", placeholder="Digite seu usuário", label_visibility="collapsed")
        senha = st.text_input("Senha", type="password", placeholder="Digite sua senha", label_visibility="collapsed")
        submit = st.form_submit_button("Entrar")
        if submit:
            if validar_credenciais(usuario, senha):
                st.session_state.autenticado = True
                st.session_state.usuario = usuario
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos")
    
    st.markdown("""
        <div class="login-footer">
            Credenciais fornecidas pelo administrador • Ambiente seguro
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # fecha login-right

    st.markdown('</div>', unsafe_allow_html=True)  # fecha login-grid
    st.markdown('</div>', unsafe_allow_html=True)  # fecha login-main-card
    st.markdown('</div>', unsafe_allow_html=True)  # fecha login-outer

    return False


def logout_button():
    if st.sidebar.button("Sair", use_container_width=True):
        st.session_state.autenticado = False
        st.session_state.usuario = None
        st.rerun()
