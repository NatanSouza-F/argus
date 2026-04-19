"""
Dashboard Argus — Revenue Intelligence
Tema SaaS claro unificado, totalmente responsivo.
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
# CONFIGURAÇÃO DA PÁGINA
# ═══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Argus • Revenue Intelligence",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# Paleta SaaS clara
COR_PRIMARIA = "#059669"
COR_ACCENT = "#00ff88"
COR_AZUL = "#3b82f6"
COR_ROXO = "#8b5cf6"
COR_AMBAR = "#f59e0b"
COR_VERMELHO = "#ef4444"
COR_VERDE_SUAVE = "#10b981"

ESCALA_VERDE = [[0, "#ecfdf5"], [0.3, "#a7f3d0"], [0.6, "#10b981"], [1, "#047857"]]


# CSS global
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp {
        background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        letter-spacing: -0.02em;
        color: #0f172a;
    }

    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem 1.25rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        transition: all 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        border-color: #00ff88;
        box-shadow: 0 8px 16px rgba(0, 255, 136, 0.1);
        transform: translateY(-1px);
    }
    [data-testid="stMetricLabel"] {
        color: #64748b !important;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    [data-testid="stMetricValue"] {
        color: #059669 !important;
        font-size: 1.75rem !important;
        font-weight: 700;
    }
    [data-testid="stMetricDelta"] { color: #64748b !important; }

    .stButton button {
        background: #00ff88;
        color: #0b1e2e;
        border: none;
        border-radius: 12px;
        padding: 0.5rem 1.25rem;
        font-weight: 600;
        transition: 0.2s;
    }
    .stButton button:hover {
        background: #00cc6a;
        box-shadow: 0 4px 12px rgba(0, 255, 136, 0.3);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
        border-bottom: 1px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 0.5rem 1.25rem;
        font-weight: 500;
        font-size: 0.9rem;
        color: #475569;
    }
    .stTabs [aria-selected="true"] {
        background: #00ff88 !important;
        color: #0b1e2e !important;
        border-color: #00ff88 !important;
    }

    /* DATAFRAMES — REMOVER PRETO */
    .stDataFrame {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }
    div[data-testid="stDataFrame"] {
        background: #ffffff !important;
    }
    div[data-testid="stDataFrame"] > div,
    div[data-testid="stDataFrame"] div[role="grid"],
    div[data-testid="stDataFrame"] div[role="row"],
    div[data-testid="stDataFrame"] div[role="columnheader"],
    div[data-testid="stDataFrame"] div[role="gridcell"] {
        background: #ffffff !important;
        color: #0f172a !important;
    }
    div[data-testid="stDataFrame"] div[role="columnheader"] {
        background: #f8fafc !important;
        color: #475569 !important;
        font-weight: 600 !important;
        border-bottom: 1px solid #e2e8f0 !important;
    }
    div[data-testid="stDataFrame"] div[role="row"]:nth-child(even) div[role="gridcell"] {
        background: #f8fafc !important;
    }

    .streamlit-expanderHeader {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 10px !important;
        color: #0f172a !important;
        font-weight: 500 !important;
    }
    .streamlit-expanderContent {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
    }

    div[data-baseweb="input"], div[data-baseweb="select"] {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="input"] input, div[data-baseweb="select"] > div {
        background: #ffffff !important;
        color: #0f172a !important;
    }

    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e2e8f0;
    }

    .stAlert {
        background: #ffffff !important;
        border-radius: 12px !important;
    }

    .argus-hero {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1.5rem;
        padding: 1rem 0;
    }
    .argus-hero h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: #0f172a;
    }
    .argus-hero p {
        color: #64748b;
        margin: 0.25rem 0 0 0;
        font-size: 0.9rem;
    }
    .argus-live-badge {
        background: #ecfdf5;
        border: 1px solid #10b981;
        padding: 6px 16px;
        border-radius: 60px;
    }
    .argus-live-badge span {
        color: #059669;
        font-weight: 600;
        font-size: 0.85rem;
    }

    .section-header {
        font-size: 1.15rem;
        font-weight: 600;
        color: #0f172a;
        margin: 0.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #00ff88;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)


# Autenticação
if not tela_login():
    st.stop()


# Helpers
def is_mobile():
    try:
        ua = st.context.headers.get("User-Agent", "")
        return any(x in ua for x in ["Mobile", "Android", "iPhone", "iPad"])
    except:
        return False


def layout_claro(altura=380):
    return {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(248, 250, 252, 0.5)",
        "font": {"family": "Inter, sans-serif", "color": "#0f172a", "size": 12},
        "xaxis": {
            "gridcolor": "#e2e8f0",
            "linecolor": "#cbd5e1",
            "tickfont": {"color": "#475569"},
        },
        "yaxis": {
            "gridcolor": "#e2e8f0",
            "linecolor": "#cbd5e1",
            "tickfont": {"color": "#475569"},
        },
        "margin": {"t": 40, "b": 50, "l": 60, "r": 30},
        "height": altura,
        "hoverlabel": {
            "bgcolor": "white",
            "bordercolor": "#e2e8f0",
            "font": {"color": "#0f172a"},
        },
    }


# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:12px; padding:10px 0;">
        <div style="width:44px; height:44px; background:#00ff88; border-radius:12px;
                    display:flex; align-items:center; justify-content:center;
                    color:#0b1e2e; font-weight:800; font-size:22px;">A</div>
        <div>
            <strong style="font-size:16px; color:#0f172a;">Argus</strong><br>
            <span style="color:#64748b; font-size:12px;">Revenue Intelligence</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"**{st.session_state.usuario}**")
    st.markdown("---")
    logout_button()
    st.caption(f"Atualizado: {datetime.now().strftime('%d/%m %H:%M')}")


# Header
st.markdown("""
<div class="argus-hero">
    <div>
        <h1>Revenue Intelligence</h1>
        <p>Visão 360° da operação comercial • Dados atualizados em tempo real</p>
    </div>
    <div class="argus-live-badge">
        <span>● AO VIVO</span>
    </div>
</div>
""", unsafe_allow_html=True)


# KPIs
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


st.markdown("<br>", unsafe_allow_html=True)


# Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🎯 Top Leads", "👥 RFM", "📊 Visão Geral", "🗺️ Geografia",
    "📈 Cohort", "🔄 Jornada", "💡 Comportamental", "💰 Curva ABC"
])


# TAB 1: Top Leads
with tab1:
    st.markdown('<div class="section-header">🎯 Leads Prioritários</div>', unsafe_allow_html=True)

    with st.expander("⚙️ Painel de Controle", expanded=not is_mobile()):
        ufs = ["Todos"] + (obter_lista_ufs() if callable(obter_lista_ufs) else [])

        if is_mobile():
            # Mobile: cada filtro em uma linha (mais legível em tela pequena)
            uf_sel = st.selectbox("📍 Estado", ufs, key="uf_leads")
            renda_min = st.slider("💰 Renda mínima (R$)", 10000, 20000, 15000, 1000, key="renda_leads")
            qtd = st.slider("🔢 Quantidade", 10, 100, 20, 10, key="qtd_leads")
        else:
            # Desktop: três colunas lado a lado
            col1, col2, col3 = st.columns(3)
            with col1:
                uf_sel = st.selectbox("📍 Estado", ufs, key="uf_leads")
            with col2:
                renda_min = st.slider("💰 Renda mínima (R$)", 10000, 20000, 15000, 1000, key="renda_leads")
            with col3:
                qtd = st.slider("🔢 Quantidade", 10, 100, 20, 10, key="qtd_leads")

        c1, c2 = st.columns([1, 4])
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
    default_uf = params.get("uf_voz", uf_sel)
    default_renda = int(params.get("renda_voz", renda_min))

    try:
        df_leads = obter_top_leads(renda_min=default_renda, uf_filtro=default_uf, limite=qtd)
        if not df_leads.empty:
            df_leads["Renda_fmt"] = df_leads["Renda_Mensal"].apply(lambda x: f"R$ {x:,.0f}")
            df_leads["Ticket_fmt"] = df_leads["ticket_mensal"].apply(lambda x: f"R$ {x:,.0f}")
            df_leads["Msg"] = df_leads["Nome"].apply(lambda n: f"Olá {n.split()[0]}, oportunidade especial!")
            df_leads["WA"] = df_leads.apply(
                lambda r: f"https://wa.me/{r['Telefone']}?text={r['Msg'].replace(' ','%20')}", axis=1
            )
            prob = prever_probabilidade(df_leads)
            df_leads["Prob"] = (pd.Series(prob) * 100).round(1).astype(str) + '%'

            st.dataframe(
                df_leads[["Nome", "UF", "Renda_fmt", "produtos_ativos", "Ticket_fmt", "Prob", "WA"]]
                .rename(columns={
                    "Renda_fmt": "Renda", "Ticket_fmt": "Ticket",
                    "Prob": "🤖 Conv.", "WA": "Ação"
                }),
                column_config={"Ação": st.column_config.LinkColumn("📱 Abrir Chat")},
                use_container_width=True, hide_index=True, height=600
            )
        else:
            st.info("Nenhum lead encontrado com esses filtros.")
    except Exception as e:
        st.error(f"Erro: {e}")


# TAB 2: RFM
with tab2:
    st.markdown('<div class="section-header">👥 Segmentação RFM</div>', unsafe_allow_html=True)

    try:
        with st.spinner("Analisando comportamento..."):
            resultado = calcular_rfm()
            if resultado is None or len(resultado) != 2:
                st.warning("Não foi possível carregar os dados RFM.")
            else:
                _, resumo = resultado

                if resumo is not None and not resumo.empty:
                    cols = st.columns(4)
                    segmentos_kpi = [
                        ("🏆 Campeões", "Campeoes"),
                        ("⚡ Potenciais", "Potenciais"),
                        ("⚠️ Em Risco", "Em Risco"),
                        ("⭐ Leais", "Leais"),
                    ]
                    for col, (label, key) in zip(cols, segmentos_kpi):
                        with col:
                            val = resumo.loc[key, 'Total_Clientes'] if key in resumo.index else 0
                            st.metric(label, f"{int(val):,}")

                    st.markdown("<br>", unsafe_allow_html=True)

                    mapa_cores_rfm = {
                        "Campeoes": COR_ACCENT,
                        "Potenciais": COR_ROXO,
                        "Em Risco": COR_VERMELHO,
                        "Leais": COR_AZUL,
                        "Hibernando": "#94a3b8",
                        "Novos/Outros": COR_VERDE_SUAVE,
                    }

                    df_plot = resumo.reset_index().sort_values("Total_Clientes", ascending=True)
                    fig = px.bar(
                        df_plot,
                        x="Total_Clientes",
                        y="segmento",
                        orientation='h',
                        color="segmento",
                        color_discrete_map=mapa_cores_rfm,
                        text="Total_Clientes",
                    )
                    fig.update_traces(
                        texttemplate='%{text:,}',
                        textposition='outside',
                        marker_line_width=0,
                    )
                    fig.update_layout(**layout_claro(450), showlegend=False)
                    fig.update_xaxes(title="Clientes")
                    fig.update_yaxes(title="")
                    st.plotly_chart(fig, use_container_width=True)

                    st.markdown('<div class="section-header">📋 Detalhamento por segmento</div>', unsafe_allow_html=True)

                    resumo_view = resumo.reset_index().copy()
                    resumo_view["Total_Clientes"] = resumo_view["Total_Clientes"].apply(lambda x: f"{int(x):,}")
                    resumo_view["Receita_Total"] = resumo_view["Receita_Total"].apply(lambda x: f"R$ {x:,.0f}")
                    resumo_view["Renda_Media"] = resumo_view["Renda_Media"].apply(lambda x: f"R$ {x:,.0f}")
                    resumo_view["Produtos_Medios"] = resumo_view["Produtos_Medios"].apply(lambda x: f"{x:.1f}")
                    resumo_view["Pct_Base"] = resumo_view["Pct_Base"].apply(lambda x: f"{x:.1f}%")
                    resumo_view["Pct_Receita"] = resumo_view["Pct_Receita"].apply(lambda x: f"{x:.1f}%")
                    resumo_view.columns = ["Segmento", "Clientes", "Receita Total",
                                           "Renda Média", "Produtos", "% Base", "% Receita"]

                    st.dataframe(resumo_view, use_container_width=True, hide_index=True)
                else:
                    st.warning("Dados RFM indisponíveis.")
    except Exception as e:
        st.error(f"Erro RFM: {e}")


# TAB 3: Visão Geral
with tab3:
    # Função auxiliar pra renderizar cada gráfico (evita duplicação)
    def render_segmentacao_renda():
        st.markdown('<div class="section-header">📊 Segmentação por renda</div>', unsafe_allow_html=True)
        df_renda = obter_segmentacao_renda()
        fig = px.bar(
            df_renda, x="faixa", y="total",
            color_discrete_sequence=[COR_PRIMARIA],
            text="total",
        )
        fig.update_traces(texttemplate='%{text:,}', textposition='outside', marker_line_width=0)
        fig.update_layout(**layout_claro(380))
        fig.update_xaxes(title="Faixa")
        fig.update_yaxes(title="Clientes")
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📋 Detalhamento por faixa"):
            df_view = df_renda.copy()
            df_view["total"] = df_view["total"].apply(lambda x: f"{int(x):,}")
            df_view.columns = ["Faixa de renda", "Total de clientes"]
            st.dataframe(df_view, use_container_width=True, hide_index=True)

    def render_evolucao_base():
        st.markdown('<div class="section-header">📈 Evolução da base</div>', unsafe_allow_html=True)
        df_evol = obter_evolucao_cadastros()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_evol["periodo"],
            y=df_evol["acumulado"],
            line=dict(color=COR_ACCENT, width=2.5),
            fill='tozeroy',
            fillcolor='rgba(0, 255, 136, 0.15)',
            name="Total acumulado",
        ))
        fig.update_layout(**layout_claro(380), showlegend=False)
        fig.update_xaxes(title="Período")
        fig.update_yaxes(title="Clientes acumulados")
        st.plotly_chart(fig, use_container_width=True)

    if is_mobile():
        # Mobile: empilhado
        render_segmentacao_renda()
        st.markdown("<br>", unsafe_allow_html=True)
        render_evolucao_base()
    else:
        # Desktop: lado a lado
        c1, c2 = st.columns(2)
        with c1:
            render_segmentacao_renda()
        with c2:
            render_evolucao_base()


# TAB 4: Geografia
with tab4:
    st.markdown('<div class="section-header">🗺️ Concentração geográfica</div>', unsafe_allow_html=True)

    col_f1, col_f2 = st.columns([1, 3])
    with col_f1:
        renda_geo = st.slider("Renda mínima (R$)", 2500, 20000, 10000, 1000, key="renda_geo")

    try:
        df_uf = obter_distribuicao_uf(renda_min=renda_geo)

        col_zoom, _ = st.columns([1, 3])
        with col_zoom:
            uf_zoom = st.selectbox(
                "🔍 Filtrar por estado",
                ["Todos"] + sorted(df_uf["UF"].unique().tolist()),
                key="uf_zoom"
            )

        if uf_zoom != "Todos":
            df_uf_filtrado = df_uf[df_uf["UF"] == uf_zoom]
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.metric(
                    f"📌 Clientes em {uf_zoom}",
                    f"{df_uf_filtrado['total_clientes'].values[0]:,}".replace(",", ".")
                )
            with col_m2:
                st.metric(
                    f"💵 Renda média em {uf_zoom}",
                    f"R$ {df_uf_filtrado['renda_media'].values[0]:,.0f}".replace(",", ".")
                )

        fig = px.choropleth(
            df_uf,
            geojson="https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/brazil-states.geojson",
            locations="UF",
            featureidkey="properties.sigla",
            color="total_clientes",
            color_continuous_scale=ESCALA_VERDE,
            scope="south america",
            labels={"total_clientes": "Clientes"},
            hover_data={"renda_media": ":.0f"},
        )
        fig.update_geos(fitbounds="locations", visible=False, bgcolor='rgba(0,0,0,0)')
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={"family": "Inter, sans-serif", "color": "#0f172a"},
            height=500 if not is_mobile() else 400,
            margin={"t": 0, "b": 0, "l": 0, "r": 0},
            coloraxis_colorbar=dict(
                title="Clientes",
                tickfont={"color": "#475569"},
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#e2e8f0",
                borderwidth=1,
            )
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-header">📌 Top 10 estados</div>', unsafe_allow_html=True)
        df_top = df_uf.head(10).sort_values("total_clientes")
        fig2 = px.bar(
            df_top, x="total_clientes", y="UF",
            orientation='h',
            color_discrete_sequence=[COR_PRIMARIA],
            text="total_clientes",
        )
        fig2.update_traces(texttemplate='%{text:,}', textposition='outside', marker_line_width=0)
        fig2.update_layout(**layout_claro(400), showlegend=False)
        fig2.update_xaxes(title="Clientes")
        fig2.update_yaxes(title="")
        st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao carregar mapa: {e}")


# TAB 5: Cohort
with tab5:
    st.markdown('<div class="section-header">📈 Retenção por safra</div>', unsafe_allow_html=True)

    try:
        with st.spinner("Calculando cohort..."):
            matriz, insights = calcular_cohort_matrix()

        if matriz is not None and not matriz.empty:
            cols = st.columns(1 if is_mobile() else 3)
            metricas_cohort = [
                ("Retenção M1", insights['retencao_media_m1']),
                ("Retenção M3", insights['retencao_media_m3']),
                ("Retenção M6", insights['retencao_media_m6']),
            ]
            for col, (label, val) in zip(cols, metricas_cohort):
                with col:
                    st.metric(label, f"{val:.1f}%")

            st.markdown("<br>", unsafe_allow_html=True)

            fig = px.imshow(
                matriz,
                text_auto=".0f",
                aspect="auto",
                color_continuous_scale=[
                    [0, "#fee2e2"],
                    [0.4, "#fef08a"],
                    [0.7, "#a7f3d0"],
                    [1, COR_ACCENT]
                ],
            )
            fig.update_layout(**layout_claro(500 if not is_mobile() else 400))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Dados insuficientes.")
    except Exception as e:
        st.error(f"Erro: {e}")


# TAB 6: Jornada
with tab6:
    st.markdown('<div class="section-header">🔄 Jornada de Cross-Sell</div>', unsafe_allow_html=True)

    try:
        with st.spinner("Analisando jornada..."):
            oportunidades = identificar_oportunidades()
            df_jornada, insights_jornada = obter_jornada_produtos()

        if not oportunidades.empty:
            col_m1, col_m2 = st.columns([1, 3])
            with col_m1:
                st.metric(
                    "Jornadas analisadas",
                    f"{insights_jornada['total_jornadas']:,}".replace(",", ".")
                )

            st.markdown("<br>", unsafe_allow_html=True)

            st.dataframe(
                oportunidades.rename(columns={
                    "origem": "Origem",
                    "destino": "Destino",
                    "clientes": "Clientes",
                    "conversao": "Conversão %",
                    "recomendacao": "Recomendação",
                    "timing_dias": "Timing (dias)",
                    "canal": "Canal",
                }),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Conversão %": st.column_config.ProgressColumn(
                        format="%.1f%%",
                        min_value=0,
                        max_value=100,
                        width="medium",
                    ),
                    "Clientes": st.column_config.NumberColumn(format="%d"),
                }
            )
        else:
            st.info("Aguardando dados.")
    except Exception as e:
        st.error(f"Erro: {e}")


# TAB 7: Comportamental
with tab7:
    st.markdown('<div class="section-header">💡 Análise comportamental</div>', unsafe_allow_html=True)
    st.caption(
        "Cada ponto representa um cliente, posicionado pela renda mensal (eixo X) "
        "e ticket total (eixo Y). A cor indica quantos produtos o cliente possui."
    )

    try:
        df_scatter = obter_scatter_renda_ticket()

        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            amostra = st.slider("Amostra exibida", 200, 1500, 500, 100, key="scatter_amostra")
        with col_f2:
            ufs_disp = ["Todos"] + sorted(df_scatter["UF"].unique().tolist())
            uf_scatter = st.selectbox("Estado", ufs_disp, key="scatter_uf")
        with col_f3:
            produtos_min = st.slider(
                "Produtos mínimos", 1, int(df_scatter["produtos"].max()),
                1, 1, key="scatter_prod"
            )

        df_filtrado = df_scatter[df_scatter["produtos"] >= produtos_min]
        if uf_scatter != "Todos":
            df_filtrado = df_filtrado[df_filtrado["UF"] == uf_scatter]

        if len(df_filtrado) > amostra:
            df_filtrado = df_filtrado.sample(amostra, random_state=42)

        if df_filtrado.empty:
            st.warning("Nenhum cliente com esses filtros.")
        else:
            st.caption(f"Mostrando **{len(df_filtrado):,}** clientes de uma amostra de **{len(df_scatter):,}**.")

            fig = px.scatter(
                df_filtrado,
                x="Renda_Mensal",
                y="ticket_mensal",
                color="produtos",
                size="produtos",
                size_max=14,
                color_continuous_scale=[
                    [0, "#a7f3d0"],
                    [0.5, COR_VERDE_SUAVE],
                    [1, "#047857"]
                ],
                opacity=0.5,
                hover_data={"UF": True, "produtos": True},
            )
            fig.update_traces(marker=dict(line=dict(width=0)))
            fig.update_layout(**layout_claro(500))
            fig.update_xaxes(title="Renda mensal (R$)")
            fig.update_yaxes(title="Ticket mensal (R$)")
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-header">🗺️ Heatmap: Contratos por UF × Produto</div>', unsafe_allow_html=True)
        st.caption("Tons mais escuros indicam maior concentração de contratos ativos.")

        df_heatmap = obter_heatmap_uf_produto()

        fig2 = px.imshow(
            df_heatmap,
            color_continuous_scale=ESCALA_VERDE,
            aspect="auto",
            text_auto='.0f',
            labels={"color": "Contratos"},
        )
        fig2.update_layout(**layout_claro(600))
        fig2.update_xaxes(title="Produto", tickangle=0, side="bottom")
        fig2.update_yaxes(title="UF")
        fig2.update_traces(textfont={"size": 10, "color": "#0f172a"})
        st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f"Erro: {e}")


# TAB 8: Curva ABC
with tab8:
    st.markdown('<div class="section-header">💰 Curva ABC de Clientes</div>', unsafe_allow_html=True)

    try:
        df_abc = obter_curva_abc()

        if not df_abc.empty:
            col1, col2, col3 = st.columns(3)

            def get_classe(cls):
                if cls in df_abc['classe'].values:
                    return df_abc[df_abc['classe'] == cls].iloc[0]
                return {'clientes': 0, 'pct_receita': 0}

            classe_a = get_classe('A')
            classe_b = get_classe('B')
            classe_c = get_classe('C')

            with col1:
                st.metric("🔴 Classe A", f"{classe_a['clientes']:,}",
                          f"{classe_a['pct_receita']:.1f}% da receita")
            with col2:
                st.metric("🟡 Classe B", f"{classe_b['clientes']:,}",
                          f"{classe_b['pct_receita']:.1f}% da receita")
            with col3:
                st.metric("🟢 Classe C", f"{classe_c['clientes']:,}",
                          f"{classe_c['pct_receita']:.1f}% da receita")

            st.markdown("<br>", unsafe_allow_html=True)

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_abc['classe'],
                y=df_abc['clientes'],
                name='Clientes',
                marker_color=[COR_VERMELHO, COR_AMBAR, COR_VERDE_SUAVE],
                text=df_abc['clientes'],
                texttemplate='%{text:,}',
                textposition='outside',
                marker_line_width=0,
            ))
            fig.add_trace(go.Scatter(
                x=df_abc['classe'],
                y=df_abc['pct_receita'],
                name='% Receita',
                yaxis='y2',
                line=dict(color=COR_AZUL, width=3),
                mode='lines+markers+text',
                marker=dict(size=10),
                text=[f"{v:.1f}%" for v in df_abc['pct_receita']],
                textposition='top center',
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(248, 250, 252, 0.5)',
                font={"family": "Inter, sans-serif", "color": "#0f172a"},
                xaxis=dict(
                    title="Classe",
                    gridcolor="#e2e8f0",
                    linecolor="#cbd5e1",
                ),
                yaxis=dict(
                    title="Clientes",
                    gridcolor="#e2e8f0",
                    linecolor="#cbd5e1",
                ),
                yaxis2=dict(
                    title="% da Receita",
                    overlaying='y',
                    side='right',
                    ticksuffix='%',
                    gridcolor="#e2e8f0",
                ),
                legend=dict(orientation='h', y=1.1, x=0.5, xanchor='center'),
                height=500,
                margin={"t": 60, "b": 50, "l": 60, "r": 60},
                hoverlabel={"bgcolor": "white", "font": {"color": "#0f172a"}},
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Dados da Curva ABC não disponíveis.")
    except Exception as e:
        st.error(f"Erro na Curva ABC: {e}")


# Footer
st.markdown("---")
st.caption("© 2026 Argus Intelligence • Todos os direitos reservados")
