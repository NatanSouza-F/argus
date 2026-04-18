"""
Dashboard Argus — Revenue Intelligence
Interface completa com tema claro, comando de voz, PWA e modelo preditivo.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
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
    prever_probabilidade,      # ← modelo preditivo
)

# NOVOS IMPORTS - ANÁLISES AVANÇADAS
from rfm_analysis import calcular_rfm
from cohort_analysis import calcular_cohort_matrix
from jornada_cliente import obter_jornada_produtos, identificar_oportunidades


def is_mobile():
    """Detecta se o dispositivo é mobile via user agent"""
    try:
        user_agent = st.context.headers.get("User-Agent", "")
        return any(
            x in user_agent for x in ["Mobile", "Android", "iPhone", "iPad"]
        )
    except:
        return False


# ═══════════════════════════════════════════════════════
# CONFIGURAÇÃO DA PÁGINA
# ═══════════════════════════════════════════════════════
st.set_page_config(
    page_title="Argus • Revenue Intelligence",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ═══════════════════════════════════════════════════════
# TEMA CLARO + NEON
# ═══════════════════════════════════════════════════════
st.markdown("""
<style>
    .stApp { background: #f8fafc; }
    h1, h2, h3, h4 {
        color: #1e293b !important;
        font-family: 'Inter', system-ui, sans-serif;
        font-weight: 600;
    }
    [data-testid="stMetric"] {
        background: white;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #00ff88;
        padding: 20px 16px;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }
    [data-testid="stMetricLabel"] {
        color: #64748b !important;
        font-size: 12px !important;
        font-weight: 500;
        letter-spacing: 0.5px;
    }
    [data-testid="stMetricValue"] {
        color: #059669 !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }
    .stButton button {
        background: #00ff88 !important;
        color: #0f172a !important;
        border: none !important;
        font-weight: 600;
        border-radius: 30px;
        padding: 8px 20px;
        transition: 0.2s;
    }
    .stButton button:hover {
        background: #00cc6a !important;
        box-shadow: 0 4px 12px rgba(0,255,136,0.3);
    }
    .stTabs [data-baseweb="tab-list"] {
        background: transparent;
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background: white;
        color: #475569;
        border: 1px solid #e2e8f0;
        border-radius: 30px;
        padding: 8px 20px;
        font-weight: 500;
        margin-right: 4px;
    }
    .stTabs [aria-selected="true"] {
        background: #00ff88 !important;
        color: #0f172a !important;
        border-color: #00ff88 !important;
    }
    .stDataFrame {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 4px;
    }
    .streamlit-expanderHeader {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 30px;
        font-weight: 500;
        color: #1e293b;
    }
    .argus-header {
        padding: 24px 0 16px 0;
        border-bottom: 2px solid #00ff88;
        margin-bottom: 24px;
    }
    .argus-logo {
        font-family: 'Inter', sans-serif;
        font-size: 36px;
        font-weight: 700;
        color: #059669;
        letter-spacing: -0.5px;
    }
    .argus-tagline {
        color: #64748b;
        font-size: 13px;
        font-weight: 400;
        letter-spacing: 1px;
    }
    @media (max-width: 768px) {
        .argus-logo { font-size: 28px; }
        [data-testid="stMetric"] { padding: 12px; }
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# PWA - Manifest e Service Worker
# ═══════════════════════════════════════════════════════
st.markdown("""
<link rel="manifest" href="/manifest.json">
<script>
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js')
        .then(reg => console.log('Service Worker registrado!', reg))
        .catch(err => console.log('Falha no Service Worker', err));
    });
  }
</script>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# AUTENTICAÇÃO
# ═══════════════════════════════════════════════════════
if not tela_login():
    st.stop()


# ═══════════════════════════════════════════════════════
# TEMPLATE DE GRÁFICOS PLOTLY
# ═══════════════════════════════════════════════════════
def layout_padrao(altura=380):
    return {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0.02)",
        "font": {"family": "Inter, sans-serif", "color": "#1e293b"},
        "xaxis": {"gridcolor": "#e2e8f0", "linecolor": "#cbd5e1"},
        "yaxis": {"gridcolor": "#e2e8f0", "linecolor": "#cbd5e1"},
        "margin": {"t": 40, "b": 40, "l": 40, "r": 40},
        "height": altura,
    }


CORES_NEON = ["#00ff88", "#00d4ff", "#b794f6", "#ff79c6", "#f1c40f", "#ff6b6b"]


# ═══════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"### Bem-vindo")
    st.markdown(f"**{st.session_state.usuario}**")
    st.markdown("---")
    logout_button()
    st.markdown("---")
    st.markdown(
        f'<div style="color: #64748b; font-size: 10px; letter-spacing: 1px;">'
        f'ÚLTIMA ATUALIZAÇÃO<br>{datetime.now().strftime("%d/%m/%Y • %H:%M")}'
        f'</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════
col_logo, col_meta = st.columns([3, 1])
with col_logo:
    st.markdown(
        '<div class="argus-header">'
        '<div class="argus-logo">ARGUS</div>'
        '<div class="argus-tagline">Revenue Intelligence • Cross-Sell Pipeline</div>'
        '</div>',
        unsafe_allow_html=True,
    )
with col_meta:
    st.markdown(
        '<div class="argus-header" style="text-align: right;">'
        f'<div class="argus-meta">CASE 01 / 2026</div>'
        f'<div class="argus-meta" style="color: #00ff88; margin-top: 8px;">● AO VIVO</div>'
        '</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════
# KPIs COM TAXA DE CONVERSÃO
# ═══════════════════════════════════════════════════════
try:
    kpis = obter_kpis_gerais()
    taxa_conv = obter_taxa_conversao()

    cols = st.columns(1 if is_mobile() else 5)
    metricas = [
        ("BASE DE CLIENTES", f"{int(kpis['total_clientes']):,}".replace(",", ".")),
        ("CONTRATOS ATIVOS", f"{int(kpis['contratos_ativos']):,}".replace(",", ".")),
        ("MRR (R$)", f"{kpis['mrr']/1000000:.1f}M"),
        ("RENDA MÉDIA", f"R$ {kpis['renda_media']:,.0f}".replace(",", ".")),
        ("TAXA CROSS-SELL", f"{taxa_conv:.1f}%"),
    ]
    for col, (label, value) in zip(cols, metricas):
        with col:
            st.metric(label, value)
except Exception as e:
    st.error(f"Erro ao carregar KPIs: {e}")
    st.stop()

st.markdown("<br>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# TABS DE INSIGHTS (REORDENADAS PARA AÇÃO RÁPIDA)
# ═══════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🎯 Top Leads",
    "👥 Segmentação RFM",
    "📊 Visão Geral",
    "🗺️ Geografia",
    "📈 Cohort",
    "🔄 Jornada",
    "📈 Comportamental",
    "💰 Curva ABC",
])


# ─── TAB 1: Top Leads (com WhatsApp, Voz e Modelo Preditivo) ─────────────
with tab1:
    st.markdown("#### Filtros")
    with st.expander("🔍 Filtrar Leads", expanded=not is_mobile()):
        cols = st.columns([1, 1, 1] if not is_mobile() else [1])
        try:
            ufs_disponiveis = ["Todos"] + obter_lista_ufs()
        except:
            ufs_disponiveis = ["Todos"]

        # Captura comandos de voz via query params
        query_params = st.query_params
        uf_voz = query_params.get("uf_voz", None)
        renda_voz = query_params.get("renda_voz", None)

        default_uf = uf_voz if uf_voz in ufs_disponiveis else "Todos"
        default_renda = int(renda_voz) if renda_voz and renda_voz.isdigit() else 15000

        with cols[0]:
            uf_selecionada = st.selectbox(
                "Estado (UF)", ufs_disponiveis,
                index=ufs_disponiveis.index(default_uf) if default_uf in ufs_disponiveis else 0,
                key="uf_leads"
            )
        with cols[1] if len(cols) > 1 else cols[0]:
            renda_min_leads = st.slider(
                "Renda mínima (R$)",
                min_value=10000, max_value=20000, value=default_renda, step=1000,
                key="renda_leads",
            )
        with cols[2] if len(cols) > 2 else cols[0]:
            qtd_leads = st.slider(
                "Quantidade de leads",
                min_value=10, max_value=100, value=20, step=10,
                key="qtd_leads",
            )

    # Botão de comando de voz
    st.markdown("---")
    col_voz, _ = st.columns([1, 3])
    with col_voz:
        voz_acionado = st.button("🎤 Comando de Voz", help="Fale algo como 'Estado São Paulo, renda mínima 15 mil'")

    if voz_acionado:
        st.components.v1.html("""
        <script>
        (function() {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {
                alert('Seu navegador não suporta reconhecimento de voz. Use Chrome ou Edge.');
                return;
            }
            const recognition = new SpeechRecognition();
            recognition.lang = 'pt-BR';
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript.toLowerCase();
                console.log('Você disse:', transcript);
                
                let uf = null;
                let renda = null;
                
                const ufs = ['ac','al','ap','am','ba','ce','df','es','go','ma','mt','ms','mg','pa','pb','pr','pe','pi','rj','rn','rs','ro','rr','sc','sp','se','to'];
                for (let sigla of ufs) {
                    if (transcript.includes(sigla)) {
                        uf = sigla.toUpperCase();
                        break;
                    }
                }
                if (transcript.includes('são paulo')) uf = 'SP';
                else if (transcript.includes('rio de janeiro')) uf = 'RJ';
                else if (transcript.includes('minas gerais')) uf = 'MG';
                
                const rendaMatch = transcript.match(/renda\s*(?:mínima\s*)?(?:de\s*)?(\d+)\s*(?:mil)?/i) ||
                                  transcript.match(/(\d+)\s*mil/i);
                if (rendaMatch) {
                    let valor = parseInt(rendaMatch[1]);
                    if (transcript.includes('mil') && valor < 1000) valor *= 1000;
                    renda = valor;
                }
                
                const params = new URLSearchParams(window.location.search);
                if (uf) params.set('uf_voz', uf);
                if (renda) params.set('renda_voz', renda);
                const newUrl = window.location.pathname + '?' + params.toString();
                window.location.href = newUrl;
            };

            recognition.onerror = (event) => {
                alert('Erro no reconhecimento: ' + event.error);
            };

            recognition.start();
        })();
        </script>
        """, height=0)

    st.markdown(f"#### Top {qtd_leads} leads priorizados para Atlas Consórcios")

    df_leads = pd.DataFrame()
    try:
        df_leads = obter_top_leads(
            renda_min=renda_min_leads,
            uf_filtro=uf_selecionada,
            limite=qtd_leads,
        )

        if df_leads.empty:
            st.warning("Nenhum lead encontrado com esses filtros.")
        else:
            # Formata valores
            df_leads["Renda_Mensal_Fmt"] = df_leads["Renda_Mensal"].apply(
                lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )
            df_leads["ticket_mensal_Fmt"] = df_leads["ticket_mensal"].apply(
                lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )

            # Mensagem WhatsApp
            df_leads["Mensagem"] = df_leads["Nome"].apply(
                lambda nome: f"Olá {nome.split()[0]}, tudo bem? Vi que você é cliente Atlas e identifiquei uma oportunidade especial de consórcio. Podemos conversar?"
            )
            df_leads["WhatsApp"] = df_leads.apply(
                lambda row: f"https://wa.me/{row['Telefone']}?text={row['Mensagem'].replace(' ', '%20')}",
                axis=1
            )

            # Modelo preditivo
            try:
                probabilidades = prever_probabilidade(df_leads)
                df_leads['Probabilidade'] = (probabilidades * 100).round(1).astype(str) + '%'
            except Exception as e:
                df_leads['Probabilidade'] = 'N/A'

            colunas_exibir = ["Nome", "UF", "Renda_Mensal_Fmt", "produtos_ativos", "ticket_mensal_Fmt", "Probabilidade", "WhatsApp"]
            mapeamento = {
                "Renda_Mensal_Fmt": "Renda Mensal",
                "produtos_ativos": "Produtos Ativos",
                "ticket_mensal_Fmt": "Ticket Mensal",
                "WhatsApp": "Ação",
                "Probabilidade": "🤖 Prob. Conversão"
            }

            st.dataframe(
                df_leads[colunas_exibir].rename(columns=mapeamento),
                use_container_width=True,
                hide_index=True,
                height=600,
                column_config={
                    "Ação": st.column_config.LinkColumn("📱 WhatsApp", display_text="Abrir Chat")
                }
            )
    except Exception as e:
        st.error(f"Erro ao carregar leads: {e}")


# ─── TAB 2: Segmentação RFM ─────────────────────────────────────────
with tab2:
    st.markdown("### 🎯 Segmentação RFM de Clientes")
    st.markdown("*Recency • Frequency • Monetary Value*")

    try:
        with st.spinner("Carregando segmentação RFM..."):
            df_rfm, resumo_rfm = calcular_rfm()

        cols = st.columns(1 if is_mobile() else 4)
        campeoes = resumo_rfm.loc["Campeoes"] if "Campeoes" in resumo_rfm.index else {"Total_Clientes": 0, "Pct_Receita": 0}
        potenciais = resumo_rfm.loc["Potenciais"] if "Potenciais" in resumo_rfm.index else {"Total_Clientes": 0, "Pct_Receita": 0}
        em_risco = resumo_rfm.loc["Em Risco"] if "Em Risco" in resumo_rfm.index else {"Total_Clientes": 0, "Pct_Receita": 0}
        leais = resumo_rfm.loc["Leais"] if "Leais" in resumo_rfm.index else {"Total_Clientes": 0, "Pct_Receita": 0}

        with cols[0]:
            st.metric("🏆 Campeões", f"{campeoes['Total_Clientes']:,}", f"{campeoes['Pct_Receita']:.1f}% da receita")
        with cols[1] if len(cols) > 1 else cols[0]:
            st.metric("⚡ Potenciais", f"{potenciais['Total_Clientes']:,}", "Prioridade Cross-sell")
        with cols[2] if len(cols) > 2 else cols[0]:
            st.metric("⭐ Leais", f"{leais['Total_Clientes']:,}", "Base sólida")
        with cols[3] if len(cols) > 3 else cols[0]:
            st.metric("⚠️ Em Risco", f"{em_risco['Total_Clientes']:,}", "Ação necessária")

        st.markdown("---")
        resumo_display = resumo_rfm.copy()
        resumo_display["Receita_Total"] = resumo_display["Receita_Total"].apply(lambda x: f"R$ {x/1000:.0f}k")
        resumo_display["Renda_Media"] = resumo_display["Renda_Media"].apply(lambda x: f"R$ {x:.0f}")
        resumo_display["Pct_Base"] = resumo_display["Pct_Base"].apply(lambda x: f"{x:.1f}%")
        resumo_display["Pct_Receita"] = resumo_display["Pct_Receita"].apply(lambda x: f"{x:.1f}%")
        st.dataframe(
            resumo_display[["Total_Clientes", "Pct_Base", "Receita_Total", "Pct_Receita", "Renda_Media", "Produtos_Medios"]],
            use_container_width=True,
        )

        fig = px.bar(
            resumo_rfm.reset_index(),
            x="Total_Clientes" if is_mobile() else "segmento",
            y="segmento" if is_mobile() else "Total_Clientes",
            color="segmento",
            orientation="h" if is_mobile() else "v",
            color_discrete_map={
                "Campeoes": "#00ff88",
                "Leais": "#00d4ff",
                "Potenciais": "#b794f6",
                "Em Risco": "#ff6b6b",
                "Hibernando": "#666666",
                "Novos/Outros": "#8a99b0",
            },
            text="Total_Clientes",
        )
        fig.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig.update_layout(**layout_padrao(400 if not is_mobile() else 500), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.success("**Segmentos Prioritários:**\n1. **Potenciais** → Cross-sell\n2. **Em Risco** → Retenção\n3. **Campeões** → Indicação")
        with col2:
            st.info("**Próximos Passos:**\n• Baixar lista de Potenciais\n• Agendar follow-up com Em Risco")
    except Exception as e:
        st.error(f"Erro ao carregar análise RFM: {e}")


# ─── TAB 3: Visão Geral ─────────────────────────────────────────────
with tab3:
    col_a, col_b = st.columns(1 if is_mobile() else 2)
    with col_a:
        st.markdown("#### Segmentação por faixa de renda")
        try:
            df_renda = obter_segmentacao_renda()
            fig = px.bar(df_renda, x="faixa", y="total", color_discrete_sequence=["#00ff88"])
            fig.update_layout(**layout_padrao(300 if is_mobile() else 380), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Erro: {e}")
    with col_b:
        st.markdown("#### Evolução da base")
        try:
            df_evolucao = obter_evolucao_cadastros()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_evolucao["periodo"], y=df_evolucao["acumulado"],
                                     mode="lines", line={"color": "#00ff88", "width": 2.5},
                                     fill="tozeroy", fillcolor="rgba(0,255,136,0.1)"))
            fig.update_layout(**layout_padrao(300 if is_mobile() else 380), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Erro: {e}")


# ─── TAB 4: Geografia ───────────────────────────────────────────────
with tab4:
    st.markdown("#### Filtros")
    renda_min_geo = st.slider("Renda mínima (R$)", 2500, 20000, 10000, 1000, key="renda_geo")
    try:
        df_uf = obter_distribuicao_uf(renda_min=renda_min_geo)
        fig_mapa = px.choropleth(
            df_uf,
            geojson="https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/brazil-states.geojson",
            locations="UF",
            featureidkey="properties.sigla",
            color="total_clientes",
            color_continuous_scale=[[0, "#f8fafc"], [0.3, "#a7f3d0"], [0.6, "#10b981"], [1, "#059669"]],
            scope="south america",
        )
        fig_mapa.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
        fig_mapa.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#1e293b"},
            height=400 if is_mobile() else 500,
            margin={"t": 0, "b": 0, "l": 0, "r": 0},
        )
        st.plotly_chart(fig_mapa, use_container_width=True)

        col_a, col_b = st.columns(1 if is_mobile() else 2)
        with col_a:
            df_top = df_uf.head(10)
            fig = px.bar(df_top.sort_values("total_clientes"), x="total_clientes", y="UF",
                         orientation="h", color_discrete_sequence=["#00ff88"])
            fig.update_layout(**layout_padrao(400), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            df_prod = obter_portfolio_produtos()
            fig = px.pie(df_prod, values="receita_mensal", names="Produto", hole=0.5,
                         color_discrete_sequence=CORES_NEON)
            fig.update_layout(**layout_padrao(400))
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Erro: {e}")


# ─── TAB 5: Cohort ──────────────────────────────────────────────────
with tab5:
    st.markdown("### 📈 Retenção por Safra")
    try:
        with st.spinner("Calculando cohort..."):
            matriz, insights = calcular_cohort_matrix()
        if matriz is not None and not matriz.empty:
            cols = st.columns(1 if is_mobile() else 3)
            with cols[0]:
                st.metric("Retenção M1", f"{insights['retencao_media_m1']:.1f}%")
            with cols[1] if len(cols) > 1 else cols[0]:
                st.metric("Retenção M3", f"{insights['retencao_media_m3']:.1f}%")
            with cols[2] if len(cols) > 2 else cols[0]:
                st.metric("Retenção M6", f"{insights['retencao_media_m6']:.1f}%")

            fig = px.imshow(
                matriz,
                text_auto=".0f",
                aspect="auto",
                color_continuous_scale=[[0, "#fee2e2"], [0.5, "#fef08a"], [0.7, "#a7f3d0"], [1, "#00ff88"]],
            )
            fig.update_layout(**layout_padrao(450 if is_mobile() else 500))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Dados insuficientes.")
    except Exception as e:
        st.error(f"Erro: {e}")


# ─── TAB 6: Jornada do Cliente ──────────────────────────────────────
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
                use_container_width=True,
                hide_index=True,
                column_config={"Conversão %": st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=100)},
            )
        else:
            st.info("Aguardando dados.")
    except Exception as e:
        st.error(f"Erro: {e}")


# ─── TAB 7: Comportamental ──────────────────────────────────────────
with tab7:
    st.markdown("#### Renda × Ticket Mensal")
    try:
        df_scatter = obter_scatter_renda_ticket()
        fig = px.scatter(
            df_scatter, x="Renda_Mensal", y="ticket_mensal", color="produtos", size="produtos",
            color_continuous_scale=[[0, "#a7f3d0"], [0.5, "#10b981"], [1, "#059669"]],
        )
        fig.update_layout(**layout_padrao(450 if is_mobile() else 500))
        st.plotly_chart(fig, use_container_width=True)

        df_heatmap = obter_heatmap_uf_produto()
        fig2 = px.imshow(df_heatmap, color_continuous_scale=[[0, "#f8fafc"], [0.5, "#10b981"], [1, "#059669"]],
                         aspect="auto", text_auto=".0f")
        fig2.update_layout(**layout_padrao(500 if is_mobile() else 550))
        st.plotly_chart(fig2, use_container_width=True)
    except Exception as e:
        st.error(f"Erro: {e}")


# ─── TAB 8: Curva ABC ───────────────────────────────────────────────
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


# ═══════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    '<div style="text-align: center; color: #94a3b8; font-size: 11px; letter-spacing: 2px; '
    'padding: 24px 0; border-top: 1px solid #e2e8f0; margin-top: 48px;">'
    'PROJETO ARGUS • DATA ENGINEERING CASE STUDY • 2026'
    '</div>',
    unsafe_allow_html=True,
)
