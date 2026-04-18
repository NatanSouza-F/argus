# ═══════════════════════════════════════════════════════════════════════════
# SPLASH SCREEN (Carrossel de Cards 3D)
# ═══════════════════════════════════════════════════════════════════════════
if 'splash_shown' not in st.session_state:
    st.session_state.splash_shown = False

if not st.session_state.splash_shown:
    st.markdown("""
    <style>
        /* Container principal da splash - cobre toda a tela */
        .splash-3d {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle at 20% 30%, #eafff2, #d4f5e5);
            z-index: 9999;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            perspective: 1200px;
            animation: fadeOutSplash 0.6s ease-in-out 4.2s forwards;
        }
        
        @keyframes fadeOutSplash {
            0% { opacity: 1; visibility: visible; }
            100% { opacity: 0; visibility: hidden; }
        }
        
        /* Esteira de cards */
        .card-carousel {
            position: relative;
            width: 100%;
            max-width: 500px;
            height: 220px;
            display: flex;
            justify-content: center;
            align-items: center;
            transform-style: preserve-3d;
        }
        
        /* Estilo base de cada card */
        .splash-card-3d {
            position: absolute;
            width: 300px;
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 32px;
            padding: 24px 28px;
            box-shadow: 0 30px 45px -15px rgba(0,0,0,0.2), 0 0 0 1px rgba(0,255,136,0.2) inset;
            text-align: left;
            transform-origin: center center;
            animation: slideLeft 4s ease-in-out forwards;
            opacity: 0;
        }
        
        /* Animação de deslizar da direita para esquerda com variação de profundidade */
        @keyframes slideLeft {
            0% {
                transform: translateX(200px) scale(0.85) rotateY(15deg);
                opacity: 0;
                z-index: 1;
            }
            15% {
                opacity: 1;
                z-index: 10;
            }
            40% {
                transform: translateX(0px) scale(1) rotateY(0deg);
                opacity: 1;
                z-index: 20;
            }
            70% {
                transform: translateX(-80px) scale(0.95) rotateY(-5deg);
                opacity: 0.7;
                z-index: 5;
            }
            100% {
                transform: translateX(-250px) scale(0.8) rotateY(-15deg);
                opacity: 0;
                z-index: 1;
            }
        }
        
        /* Atrasos individuais para criar o efeito cascata */
        .card-1 { animation-delay: 0.1s; }
        .card-2 { animation-delay: 0.5s; }
        .card-3 { animation-delay: 0.9s; }
        .card-4 { animation-delay: 1.3s; }
        
        /* Logo final */
        .argus-final-3d {
            font-family: 'Inter', sans-serif;
            font-size: 5.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #059669, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 10px;
            margin-top: 30px;
            opacity: 0;
            animation: logoReveal 0.7s cubic-bezier(0.175, 0.885, 0.32, 1.275) 2.8s forwards;
            text-shadow: 0 10px 30px rgba(0,255,136,0.2);
        }
        
        @keyframes logoReveal {
            0% { opacity: 0; transform: scale(0.9); }
            100% { opacity: 1; transform: scale(1); }
        }
        
        /* Conteúdo do card */
        .card-label {
            font-family: 'Inter', sans-serif;
            font-size: 1.1rem;
            font-weight: 600;
            color: #2c3e50;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }
        .card-value {
            font-family: 'Inter', sans-serif;
            font-size: 2.8rem;
            font-weight: 700;
            color: #059669;
            line-height: 1.2;
        }
        .card-trend {
            font-family: 'Inter', sans-serif;
            font-size: 0.9rem;
            color: #64748b;
            margin-top: 8px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .trend-up { color: #00a86b; }
        .trend-badge {
            background: rgba(0,255,136,0.15);
            padding: 2px 8px;
            border-radius: 30px;
        }
    </style>
    
    <div class="splash-3d">
        <div class="card-carousel">
            <!-- Card 1: Leads Ativos -->
            <div class="splash-card-3d card-1">
                <div class="card-label">📋 LEADS ATIVOS</div>
                <div class="card-value">2.431</div>
                <div class="card-trend">
                    <span class="trend-up">▲ +12%</span> 
                    <span class="trend-badge">este mês</span>
                </div>
            </div>
            <!-- Card 2: Receita Mensal -->
            <div class="splash-card-3d card-2">
                <div class="card-label">💰 RECEITA (MRR)</div>
                <div class="card-value">R$ 1.2M</div>
                <div class="card-trend">
                    <span class="trend-up">▲ +8.3%</span> 
                    <span class="trend-badge">vs. mês anterior</span>
                </div>
            </div>
            <!-- Card 3: Taxa de Cross-Sell -->
            <div class="splash-card-3d card-3">
                <div class="card-label">🔄 CROSS-SELL</div>
                <div class="card-value">34.7%</div>
                <div class="card-trend">
                    <span class="trend-up">▲ +5.1pp</span> 
                    <span class="trend-badge">últimos 30d</span>
                </div>
            </div>
            <!-- Card 4: Clientes em Risco -->
            <div class="splash-card-3d card-4">
                <div class="card-label">⚠️ EM RISCO</div>
                <div class="card-value">847</div>
                <div class="card-trend">
                    <span style="color:#e67e22;">▼ -3%</span> 
                    <span class="trend-badge">redução positiva</span>
                </div>
            </div>
        </div>
        <div class="argus-final-3d">ARGUS</div>
    </div>
    """, unsafe_allow_html=True)
    st.session_state.splash_shown = True
    time.sleep(4.5)  # Tempo total da animação
    st.rerun()
