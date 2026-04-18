"""
Dashboard Argus — Revenue Intelligence
UI Moderna: Glassmorphism, Splash Screen 3D, Mobile First.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import time
from datetime import datetime

from autenticacao import tela_login, logout_button
from dados import (
    obter_kpis_gerais,
    obter_taxa_conversao,
    obter_distribuicao_uf,
    obter_portfolio_produtos,
    obter_segmentacao_renda,
    obter_top_leads,
    obter_evolucao_cadastros,
    obter_heatmap_uf_produto,
    obter_curva_abc,
    obter_scatter_renda_ticket,
    obter_lista_ufs,
    prever_probabilidade,
)
from rfm_analysis import calcular_rfm
from cohort_analysis import calcular_cohort_matrix
from jornada_cliente import obter_jornada_produtos, identificar_oportunidades

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DA PÁGINA E ESTILO GLOBAL
# ═══════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Argus • Revenue Intelligence", page_icon="◉", layout="wide", initial_sidebar_state="collapsed")

# CSS Global – Glassmorphism + Fonte Inter
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(240, 248, 255, 0.8), rgba(255, 255, 255, 0.95));
        backdrop-filter: blur(2px);
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        letter-spacing: -0.02em;
        color: #0b1e2e;
    }
    
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(0, 255, 136, 0.15);
        border-radius: 24px;
        padding: 1.5rem 1rem;
        box-shadow: 0 20px 35px -8px rgba(0, 0, 0, 0.05), 0 0 0 1px rgba(0, 255, 136, 0.1) inset;
        transition: all 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        box-shadow: 0 25px 40px -12px rgba(0, 255, 136, 0.15);
        border-color: rgba(0, 255, 136, 0.4);
    }
    
    [data-testid="stMetricLabel"] {
        color: #3a4c5e !important;
        font-size: 0.8rem;
        font-weight: 500;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }
    
    [data-testid="stMetricValue"] {
        color: #059669 !important;
        font-size: 2.2rem !important;
        font-weight: 700;
    }
    
    .stButton button {
        background: rgba(0, 255, 136, 0.85);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: #0b1e2e;
        border-radius: 40px;
        padding: 0.6rem 1.8rem;
        font-weight: 600;
        transition: 0.2s;
    }
    .stButton button:hover {
        background: #00ff88;
        box-shadow: 0 8px 20px rgba(0, 255, 136, 0.3);
        transform: translateY(-2px);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.5);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(0, 255, 136, 0.2);
        border-radius: 60px;
        padding: 0.6rem 1.8rem;
        font-weight: 500;
        color: #1e293b;
    }
    .stTabs [aria-selected="true"] {
        background: #00ff88 !important;
        color: #0b1e2e !important;
        border-color: #00ff88 !important;
        box-shadow: 0 4px 12px rgba(0, 255, 136, 0.3);
    }
    
    .stDataFrame {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(8px);
        border-radius: 24px;
        border: 1px solid rgba(0,0,0,0.05);
        padding: 8px;
    }
    
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(16px);
        border-right: 1px solid rgba(0, 255, 136, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# SPLASH SCREEN 3D (Carrossel de Cards)
# ═══════════════════════════════════════════════════════════════════════════
if 'splash_shown' not in st.session_state:
    st.session_state.splash_shown = False

if not st.session_state.splash_shown:
    st.markdown("""
    <style>
        .splash-3d {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
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
        @keyframes slideLeft {
            0% { transform: translateX(200px) scale(0.85) rotateY(15deg); opacity: 0; z-index: 1; }
            15% { opacity: 1; z-index: 10; }
            40% { transform: translateX(0px) scale(1) rotateY(0deg); opacity: 1; z-index: 20; }
            70% { transform: translateX(-80px) scale(0.95) rotateY(-5deg); opacity: 0.7; z-index: 5; }
            100% { transform: translateX(-250px) scale(0.8) rotateY(-15deg); opacity: 0; z-index: 1; }
        }
        .card-1 { animation-delay: 0.1s; }
        .card-2 { animation-delay: 0.5s; }
        .card-3 { animation-delay: 0.9s; }
        .card-4 { animation-delay: 1.3s; }
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
            <div class="splash-card-3d card-1">
                <div class="card-label">📋 LEADS ATIVOS</div>
                <div class="card-value">2.431</div>
                <div class="card-trend">
                    <span class="trend-up">▲ +12%</span> 
                    <span class="trend-badge">este mês</span>
                </div>
            </div>
            <div class="splash-card-3d card-2">
                <div class="card-label">💰 RECEITA (MRR)</div>
                <div class="card-value">R$ 1.2M</div>
                <div class="card-trend">
                    <span class="trend-up">▲ +8.3%</span> 
                    <span class="trend-badge">vs. mês anterior</span>
                </div>
            </div>
            <div class="splash-card-3d card-3">
                <div class="card-label">🔄 CROSS-SELL</div>
                <div class="card-value">34.7%</div>
                <div class="card-trend">
                    <span class="trend-up">▲ +5.1pp</span> 
                    <span class="trend-badge">últimos 30d</span>
                </div>
            </div>
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
    time.sleep(4.5)
    st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
# AUTENTICAÇÃO
# ═══════════════════════════════════════════════════════════════════════════
if not tela_login():
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES
# ═══════════════════════════════════════════════════════════════════════════
def is_mobile():
    try:
        ua = st.context.headers.get("User-Agent", "")
        return any(x in ua for x in ["Mobile", "Android", "iPhone", "iPad"])
    except:
        return False

def layout_padrao(altura=380):
    return {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(255,255,255,0.3)",
        "font": {"family": "Inter, sans-serif", "color": "#1e293b"},
        "xaxis": {"gridcolor": "#e2e8f0", "linecolor": "#cbd5e1"},
        "yaxis": {"gridcolor": "#e2e8f0", "linecolor": "#cbd5e1"},
        "margin": {"t": 40, "b": 40, "l": 40, "r": 40},
        "height": altura,
    }

CORES_NEON = ["#00ff88", "#00d4ff", "#b794f6", "#ff79c6", "#f1c40f", "#ff6b6b"]

# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:12px; padding:10px 0;">
        <div style="width:48px; height:48px; background:#00ff88; border-radius:30px; display:flex; align-items:center; justify-content:center; color:#0b1e2e; font-weight:800; font-size:24px;">A</div>
        <div><strong style="font-size:18px;">Argus</strong><br><span style="color:#64748b;">Revenue Ops</span></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"**{st.session_state.usuario}**")
    st.markdown("---")
    logout_button()
    st.caption(f"Atualizado: {datetime.now().strftime('%d/%m %H:%M')}")

# ═══════════════════════════════════════════════════════════════════════════
# CABEÇALHO PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:1.5rem;">
    <div>
        <h1 style="margin:0; font-size:2.8rem; font-weight:700; letter-spacing:-0.03em;">Revenue Intelligence</h1>
        <p style="color:#64748b; margin-top:0;">Visão 360° da sua operação comercial • Atualizado em tempo real</p>
    </div>
    <div style="background:rgba(0,255,136,0.15); padding:10px 20px; border-radius:60px;">
        <span style="color:#059669; font-weight:600;">● AO VIVO</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# KPIs
# ═══════════════════════════════════════════════════════════════════════════
try:
    kpis = obter_kpis_gerais()
    taxa_conv = obter_taxa_conversao()
    cols = st.columns(1 if is_mobile() else 5)
    metricas = [
        ("BASE ATIVA", f"{int(kpis['total_clientes']):,}".replace(",", ".")),
        ("CONTRATOS ATIVOS", f"{int(kpis['contratos_ativos']):,}".replace(",", ".")),
        ("MRR", f"R$ {kpis['mrr']/1e6:.1f}M"),
        ("RENDA MÉDIA", f"R$ {kpis['renda_media']:,.0f}".replace(",", ".")),
        ("CROSS-SELL", f"{taxa_conv:.1f}%"),
    ]
    for col, (label, val) in zip(cols, metricas):
        with col:
            st.metric(label, val)
except Exception as e:
    st.error(f"Erro nos KPIs: {e}")
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🎯 Top Leads", "👥 RFM", "📊 Visão Geral", "🗺️ Geografia",
    "📈 Cohort", "🔄 Jornada", "📈 Comportamental", "💰 Curva ABC"
])

# TAB 1: Top Leads (com WhatsApp, voz, ML)
with tab1:
    st.markdown("### 🎯 Leads Prioritários")
    with st.expander("⚙️ Painel de Controle", expanded=not is_mobile()):
        col1, col2, col3 = st.columns([1,1,1] if not is_mobile() else [1])
        ufs = ["Todos"] + (obter_lista_ufs() if callable(obter_lista_ufs) else [])
        with col1:
            uf_sel = st.selectbox("📍 Estado", ufs, key="uf_leads")
        with col2:
            renda_min = st.slider("💰 Renda mínima (R$)", 10000, 20000, 15000, 1000, key="renda_leads")
        with col3:
            qtd = st.slider("🔢 Quantidade", 10, 100, 20, 10, key="qtd_leads")
        c1, c2 = st.columns([1,4])
        with c1:
            if st.button("🎤 Comando de Voz"):
                st.components.v1.html("""
                <script>
                const r = new (window.SpeechRecognition || webkitSpeechRecognition)();
                r.lang='pt-BR'; r.onresult=e => {
                    let t = e.results[0][0].transcript.toLowerCase();
                    let uf=null, renda=null;
                    ['sp','rj','mg'].forEach(s=>{if(t.includes(s)) uf=s.toUpperCase();});
                    let m = t.match(/renda\\s*(\\d+)/) || t.match(/(\\d+)\\s*mil/);
                    if(m) renda = parseInt(m[1])*(t.includes('mil')?1000:1);
                    let p = new URLSearchParams(window.location.search);
                    if(uf) p.set('uf_voz', uf); if(renda) p.set('renda_voz', renda);
                    window.location.search = p.toString();
                }; r.start();
                </script>
                """, height=0)
    params = st.query_params
    default_uf = params.get("uf_voz", "Todos")
    default_renda = int(params.get("renda_voz", 15000))
    df_leads = pd.DataFrame()
    try:
        df_leads = obter_top_leads(renda_min=default_renda, uf_filtro=default_uf, limite=qtd)
        if not df_leads.empty:
            df_leads["Renda_fmt"] = df_leads["Renda_Mensal"].apply(lambda x: f"R$ {x:,.0f}")
            df_leads["Ticket_fmt"] = df_leads["ticket_mensal"].apply(lambda x: f"R$ {x:,.0f}")
            df_leads["Msg"] = df_leads["Nome"].apply(lambda n: f"Olá {n.split()[0]}, oportunidade especial!")
            df_leads["WA"] = df_leads.apply(lambda r: f"https://wa.me/{r['Telefone']}?text={r['Msg'].replace(' ','%20')}", axis=1)
            prob = prever_probabilidade(df_leads)
            df_leads["Prob"] = (pd.Series(prob)*100).round(1).astype(str)+'%'
            st.dataframe(
                df_leads[["Nome","UF","Renda_fmt","produtos_ativos","Ticket_fmt","Prob","WA"]]
                .rename(columns={"Renda_fmt":"Renda","Ticket_fmt":"Ticket","Prob":"🤖 Conv.","WA":"Ação"}),
                column_config={"Ação": st.column_config.LinkColumn("📱 Abrir Chat")},
                use_container_width=True, hide_index=True, height=600
            )
        else:
            st.warning("Nenhum lead encontrado.")
    except Exception as e:
        st.error(f"Erro: {e}")

# TAB 2: RFM (resumido para caber no exemplo – mantenha seu código original completo)
with tab2:
    st.markdown("### 👥 Segmentação RFM")
    try:
        with st.spinner("Analisando..."):
            _, resumo = calcular_rfm()
        # ... (seu código original da RFM)
        st.dataframe(resumo)
    except Exception as e:
        st.error(f"Erro: {e}")

# (As demais abas devem ser mantidas com seus códigos originais, apenas adaptando os layouts)

# ═══════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.caption("© 2026 Argus Intelligence • Todos os direitos reservados")
