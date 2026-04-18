def tela_login():
    if 'autenticado' in st.session_state and st.session_state.autenticado:
        return True

    # Container principal com duas colunas
    col_anim, col_form = st.columns([1.2, 1] if not is_mobile() else [1])

    with col_anim:
        # Animação 3D contínua (mesma estrutura da splash, mas sem fadeOut)
        st.markdown("""
        <style>
            .login-carousel {
                position: relative;
                width: 100%;
                height: 320px;
                display: flex;
                justify-content: center;
                align-items: center;
                perspective: 1200px;
                margin-top: 20px;
            }
            .login-card {
                position: absolute;
                width: 260px;
                background: rgba(255, 255, 255, 0.85);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 32px;
                padding: 20px 24px;
                box-shadow: 0 25px 35px -10px rgba(0,0,0,0.15);
                text-align: left;
                transform-origin: center center;
                animation: loginSlide 6s ease-in-out infinite;
                opacity: 0;
            }
            @keyframes loginSlide {
                0% { transform: translateX(180px) scale(0.8) rotateY(12deg); opacity: 0; z-index: 1; }
                10% { opacity: 0.9; z-index: 5; }
                25% { transform: translateX(0px) scale(1) rotateY(0deg); opacity: 1; z-index: 20; }
                50% { transform: translateX(-60px) scale(0.95) rotateY(-4deg); opacity: 0.8; z-index: 10; }
                75% { transform: translateX(-160px) scale(0.8) rotateY(-10deg); opacity: 0.3; z-index: 1; }
                100% { transform: translateX(180px) scale(0.8) rotateY(12deg); opacity: 0; z-index: 1; }
            }
            .login-card-1 { animation-delay: 0s; }
            .login-card-2 { animation-delay: 1.5s; }
            .login-card-3 { animation-delay: 3.0s; }
            .login-card-4 { animation-delay: 4.5s; }
            .argus-login-title {
                font-family: 'Inter', sans-serif;
                font-size: 2.8rem;
                font-weight: 800;
                background: linear-gradient(135deg, #059669, #00ff88);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-align: center;
                margin-top: 10px;
                letter-spacing: 6px;
            }
            .card-label {
                font-family: 'Inter', sans-serif;
                font-size: 1rem;
                font-weight: 600;
                color: #2c3e50;
                margin-bottom: 6px;
            }
            .card-value {
                font-family: 'Inter', sans-serif;
                font-size: 2.2rem;
                font-weight: 700;
                color: #059669;
            }
        </style>
        <div class="login-carousel">
            <div class="login-card login-card-1">
                <div class="card-label">📋 LEADS ATIVOS</div>
                <div class="card-value">2.431</div>
                <div style="color:#64748b; margin-top:8px;">▲ +12% este mês</div>
            </div>
            <div class="login-card login-card-2">
                <div class="card-label">💰 RECEITA (MRR)</div>
                <div class="card-value">R$ 1.2M</div>
                <div style="color:#64748b; margin-top:8px;">▲ +8.3% vs. anterior</div>
            </div>
            <div class="login-card login-card-3">
                <div class="card-label">🔄 CROSS-SELL</div>
                <div class="card-value">34.7%</div>
                <div style="color:#64748b; margin-top:8px;">▲ +5.1pp últimos 30d</div>
            </div>
            <div class="login-card login-card-4">
                <div class="card-label">⚠️ EM RISCO</div>
                <div class="card-value">847</div>
                <div style="color:#e67e22; margin-top:8px;">▼ -3% redução positiva</div>
            </div>
        </div>
        <div class="argus-login-title">ARGUS</div>
        """, unsafe_allow_html=True)

    with col_form:
        st.markdown("""
        <div style="margin-top: 40px; text-align: center;">
            <h2 style="font-family: 'Inter', sans-serif; font-weight: 600;">Acesse sua conta</h2>
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
