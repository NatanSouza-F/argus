"""
Dashboard Argus — Revenue Intelligence
UI Moderna: Glassmorphism, Login com Animação 3D, Mobile First.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
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
# CONFIGURAÇÃO DA PÁGINA E ESTILO GLOBAL (GLASSMORPHISM + INTER)
# ═══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Argus • Revenue Intelligence",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
# AUTENTICAÇÃO (já contém a animação 3D)
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

# ──────────────────────────────────────────────────────────────────────────
# TAB 1: Top Leads (WhatsApp, Voz, ML)
# ──────────────────────────────────────────────────────────────────────────
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
            if st.button("🎤 Comando de Voz", help="Fale 'Estado SP, renda 18 mil'"):
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

# ──────────────────────────────────────────────────────────────────────────
# TAB 2: Segmentação RFM (Visual Aprimorado)
# ──────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("### 👥 Segmentação RFM")
    try:
        with st.spinner("Analisando comportamento..."):
            _, resumo = calcular_rfm()
        campeoes = resumo.loc["Campeoes"] if "Campeoes" in resumo.index else {"Total_Clientes": 0}
        cols = st.columns(1 if is_mobile() else 4)
        with cols[0]: st.metric("🏆 Campeões", f"{campeoes.get('Total_Clientes',0):,}")
        with cols[1] if len(cols)>1 else cols[0]: st.metric("⚡ Potenciais", f"{resumo.loc['Potenciais','Total_Clientes'] if 'Potenciais' in resumo.index else 0:,}")
        with cols[2] if len(cols)>2 else cols[0]: st.metric("⚠️ Em Risco", f"{resumo.loc['Em Risco','Total_Clientes'] if 'Em Risco' in resumo.index else 0:,}")
        with cols[3] if len(cols)>3 else cols[0]: st.metric("⭐ Leais", f"{resumo.loc['Leais','Total_Clientes'] if 'Leais' in resumo.index else 0:,}")
        
        fig = px.bar(resumo.reset_index(), x="Total_Clientes", y="segmento", orientation='h',
                     color="segmento", color_discrete_map={"Campeoes":"#00ff88","Potenciais":"#b794f6","Em Risco":"#ff6b6b","Leais":"#00d4ff"})
        fig.update_layout(**layout_padrao(450))
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Erro RFM: {e}")

# ──────────────────────────────────────────────────────────────────────────
# TAB 3: Visão Geral
# ──────────────────────────────────────────────────────────────────────────
with tab3:
    c1, c2 = st.columns(1 if is_mobile() else 2)
    with c1:
        df_renda = obter_segmentacao_renda()
        fig = px.bar(df_renda, x="faixa", y="total", color_discrete_sequence=["#059669"])
        fig.update_layout(**layout_padrao(350))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        df_evol = obter_evolucao_cadastros()
        fig = go.Figure(go.Scatter(x=df_evol["periodo"], y=df_evol["acumulado"], line=dict(color="#00ff88", width=3), fill='tozeroy'))
        fig.update_layout(**layout_padrao(350))
        st.plotly_chart(fig, use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────
# TAB 4: Geografia
# ──────────────────────────────────────────────────────────────────────────
with tab4:
    renda_geo = st.slider("Renda mínima", 2500, 20000, 10000, 1000)
    df_uf = obter_distribuicao_uf(renda_geo)
    fig = px.choropleth(df_uf, geojson="https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/brazil-states.geojson",
                        locations="UF", featureidkey="properties.sigla", color="total_clientes",
                        color_continuous_scale=["#e6fff0","#00ff88","#059669"])
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(height=450, margin=dict(t=0))
    st.plotly_chart(fig, use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────
# TAB 5: Cohort
# ──────────────────────────────────────────────────────────────────────────
with tab5:
    st.markdown("### 📈 Retenção por Safra")
    try:
        with st.spinner("Calculando cohort..."):
            matriz, insights = calcular_cohort_matrix()
        if matriz is not None and not matriz.empty:
            cols = st.columns(1 if is_mobile() else 3)
            with cols[0]: st.metric("Retenção M1", f"{insights['retencao_media_m1']:.1f}%")
            with cols[1] if len(cols)>1 else cols[0]: st.metric("Retenção M3", f"{insights['retencao_media_m3']:.1f}%")
            with cols[2] if len(cols)>2 else cols[0]: st.metric("Retenção M6", f"{insights['retencao_media_m6']:.1f}%")
            fig = px.imshow(matriz, text_auto=".0f", aspect="auto",
                            color_continuous_scale=[[0, "#fee2e2"], [0.5, "#fef08a"], [0.7, "#a7f3d0"], [1, "#00ff88"]])
            fig.update_layout(**layout_padrao(450 if is_mobile() else 500))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Dados insuficientes.")
    except Exception as e:
        st.error(f"Erro: {e}")

# ──────────────────────────────────────────────────────────────────────────
# TAB 6: Jornada do Cliente
# ──────────────────────────────────────────────────────────────────────────
with tab6:
    st.markdown("### 🔄 Jornada de Cross-Sell")
    try:
        with st.spinner("Analisando jornada..."):
            oportunidades = identificar_oportunidades()
            df_jornada, insights_jornada = obter_jornada_produtos()
        if not oportunidades.empty:
            st.metric("Jornadas analisadas", f"{insights_jornada['total_jornadas']:,}")
            st.dataframe(
                oportunidades.rename(columns={
                    "origem": "Origem", "destino": "Destino", "clientes": "Clientes",
                    "conversao": "Conversão %", "recomendacao": "Recomendação",
                    "timing_dias": "Timing", "canal": "Canal"
                }),
                use_container_width=True, hide_index=True,
                column_config={"Conversão %": st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=100)},
            )
        else:
            st.info("Aguardando dados.")
    except Exception as e:
        st.error(f"Erro: {e}")

# ──────────────────────────────────────────────────────────────────────────
# TAB 7: Comportamental
# ──────────────────────────────────────────────────────────────────────────
with tab7:
    st.markdown("#### Renda × Ticket Mensal")
    try:
        df_scatter = obter_scatter_renda_ticket()
        fig = px.scatter(df_scatter, x="Renda_Mensal", y="ticket_mensal", color="produtos", size="produtos",
                         color_continuous_scale=[[0, "#a7f3d0"], [0.5, "#10b981"], [1, "#059669"]])
        fig.update_layout(**layout_padrao(450 if is_mobile() else 500))
        st.plotly_chart(fig, use_container_width=True)

        df_heatmap = obter_heatmap_uf_produto()
        fig2 = px.imshow(df_heatmap, color_continuous_scale=[[0, "#f8fafc"], [0.5, "#10b981"], [1, "#059669"]],
                         aspect="auto", text_auto=".0f")
        fig2.update_layout(**layout_padrao(500 if is_mobile() else 550))
        st.plotly_chart(fig2, use_container_width=True)
    except Exception as e:
        st.error(f"Erro: {e}")

# ──────────────────────────────────────────────────────────────────────────
# TAB 8: Curva ABC
# ──────────────────────────────────────────────────────────────────────────
with tab8:
    try:
        df_abc = obter_curva_abc()
        if not df_abc.empty:
            col_a, col_b = st.columns(1 if is_mobile() else [1, 2])
            with col_a:
                fig = go.Figure(data=[go.Pie(labels=df_abc["classe"], values=df_abc["clientes"],
                                             hole=0.6, marker_colors=["#00ff88", "#00d4ff", "#b794f6"])])
                fig.update_layout(**layout_padrao(350))
                st.plotly_chart(fig, use_container_width=True)
            with col_b:
                fig = px.bar(df_abc, x="classe", y="pct_receita", text="pct_receita", color="classe",
                             color_discrete_sequence=["#00ff88", "#00d4ff", "#b794f6"])
                fig.update_traces(texttemplate="%{text}%", textposition="outside")
                fig.update_layout(**layout_padrao(350), showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Erro: {e}")

# ═══════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.caption("© 2026 Argus Intelligence • Todos os direitos reservados")
