"""
Dashboard Argus — Revenue Intelligence
Interface principal com tema neon dark.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
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
)

# NOVOS IMPORTS - ANÁLISES AVANÇADAS
from rfm_analysis import calcular_rfm
from cohort_analysis import calcular_cohort_matrix
from jornada_cliente import obter_jornada_produtos, identificar_oportunidades

# ═══════════════════════════════════════════════════════
# CONFIGURAÇÃO DA PÁGINA
# ═══════════════════════════════════════════════════════
st.set_page_config(
    page_title="Argus • Revenue Intelligence",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ═══════════════════════════════════════════════════════
# TEMA NEON DARK
# ═══════════════════════════════════════════════════════
st.markdown("""
<style>
    .stApp { background: #0a0e14; }
    header[data-testid="stHeader"] { background: transparent; }

    h1, h2, h3, h4 {
        color: #e8eef7 !important;
        font-family: 'Georgia', serif;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #0f1620 0%, #0a0e14 100%);
        border: 1px solid rgba(0, 255, 136, 0.2);
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.05);
    }

    [data-testid="stMetricLabel"] {
        color: #8a99b0 !important;
        font-size: 11px !important;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    [data-testid="stMetricValue"] {
        color: #00ff88 !important;
        font-size: 32px !important;
        font-weight: 500 !important;
    }

    [data-testid="stMetricDelta"] {
        color: #8a99b0 !important;
    }

    .stTextInput input, .stSelectbox select, .stNumberInput input {
        background: #0f1620 !important;
        color: #e8eef7 !important;
        border: 1px solid rgba(0, 255, 136, 0.3) !important;
    }

    .stButton button, .stFormSubmitButton button {
        background: linear-gradient(90deg, #00ff88 0%, #00cc6a 100%) !important;
        color: #0a0e14 !important;
        border: none !important;
        font-weight: 500 !important;
        letter-spacing: 1px;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: transparent;
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background: #0f1620;
        color: #8a99b0;
        border: 1px solid rgba(0, 255, 136, 0.1);
        border-radius: 8px;
        padding: 12px 24px;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(0, 255, 136, 0.1) !important;
        color: #00ff88 !important;
        border-color: #00ff88 !important;
    }

    .stDataFrame {
        background: #0f1620;
        border: 1px solid rgba(0, 255, 136, 0.15);
        border-radius: 8px;
    }

    hr { border-color: rgba(0, 255, 136, 0.15) !important; }

    .argus-header {
        padding: 32px 0 24px 0;
        border-bottom: 1px solid rgba(0, 255, 136, 0.15);
        margin-bottom: 32px;
    }

    .argus-logo {
        font-family: 'Georgia', serif;
        font-size: 42px;
        color: #00ff88;
        letter-spacing: 4px;
        margin-bottom: 4px;
    }

    .argus-tagline {
        color: #8a99b0;
        font-size: 11px;
        letter-spacing: 3px;
        text-transform: uppercase;
    }

    .argus-meta {
        text-align: right;
        color: #8a99b0;
        font-size: 11px;
        letter-spacing: 2px;
    }

    .filtros-container {
        background: rgba(15, 22, 32, 0.5);
        border: 1px solid rgba(0, 255, 136, 0.15);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 24px;
    }
    
    .streamlit-expanderHeader {
        background: #0f1620;
        border: 1px solid rgba(0, 255, 136, 0.1);
        border-radius: 8px;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #00ff88 !important;
    }
</style>
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
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(15, 22, 32, 0.5)',
        'font': {'family': 'Georgia, serif', 'color': '#e8eef7'},
        'xaxis': {'gridcolor': 'rgba(0, 255, 136, 0.1)', 'linecolor': 'rgba(0, 255, 136, 0.2)'},
        'yaxis': {'gridcolor': 'rgba(0, 255, 136, 0.1)', 'linecolor': 'rgba(0, 255, 136, 0.2)'},
        'margin': {'t': 40, 'b': 40, 'l': 40, 'r': 40},
        'height': altura,
    }


CORES_NEON = ['#00ff88', '#00d4ff', '#b794f6', '#ff79c6', '#f1c40f', '#ff6b6b']


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
        f'<div style="color: #556; font-size: 10px; letter-spacing: 1px;">'
        f'ÚLTIMA ATUALIZAÇÃO<br>{datetime.now().strftime("%d/%m/%Y • %H:%M")}'
        f'</div>',
        unsafe_allow_html=True
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
        unsafe_allow_html=True
    )
with col_meta:
    st.markdown(
        '<div class="argus-header" style="text-align: right;">'
        f'<div class="argus-meta">CASE 01 / 2026</div>'
        f'<div class="argus-meta" style="color: #00ff88; margin-top: 8px;">● AO VIVO</div>'
        '</div>',
        unsafe_allow_html=True
    )


# ═══════════════════════════════════════════════════════
# KPIs COM TAXA DE CONVERSÃO
# ═══════════════════════════════════════════════════════
try:
    kpis = obter_kpis_gerais()
    taxa_conv = obter_taxa_conversao()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("BASE DE CLIENTES", f"{int(kpis['total_clientes']):,}".replace(',', '.'))
    with col2:
        st.metric("CONTRATOS ATIVOS", f"{int(kpis['contratos_ativos']):,}".replace(',', '.'))
    with col3:
        st.metric("MRR (R$)", f"{kpis['mrr']/1000000:.1f}M")
    with col4:
        st.metric("RENDA MÉDIA", f"R$ {kpis['renda_media']:,.0f}".replace(',', '.'))
    with col5:
        st.metric("TAXA CROSS-SELL", f"{taxa_conv:.1f}%")
except Exception as e:
    st.error(f"Erro ao carregar KPIs: {e}")
    st.stop()

st.markdown("<br>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# TABS DE INSIGHTS (VERSÃO COMPLETA COM 8 TABS)
# ═══════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📊 Visão Geral",
    "🗺️ Geografia",
    "📈 Comportamental",
    "👥 Segmentação RFM",
    "📊 Análise Cohort",
    "🔄 Jornada do Cliente",
    "🎯 Top Leads",
    "💰 Curva ABC"
])


# ─── TAB 1: Visão Geral ─────────────────────────────────────────────
with tab1:
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Segmentação por faixa de renda")
        try:
            df_renda = obter_segmentacao_renda()
            fig = px.bar(
                df_renda,
                x='faixa',
                y='total',
                color_discrete_sequence=['#00ff88']
            )
            fig.update_layout(**layout_padrao(380), showlegend=False)
            fig.update_traces(marker_line_width=0)
            fig.update_xaxes(title='')
            fig.update_yaxes(title='Clientes')
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao carregar segmentação: {e}")

    with col_b:
        st.markdown("#### Evolução da base de clientes")
        try:
            df_evolucao = obter_evolucao_cadastros()
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_evolucao['periodo'],
                y=df_evolucao['acumulado'],
                mode='lines',
                line={'color': '#00ff88', 'width': 2.5},
                fill='tozeroy',
                fillcolor='rgba(0, 255, 136, 0.1)'
            ))
            fig.update_layout(**layout_padrao(380), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao carregar evolução: {e}")


# ─── TAB 2: Geografia ───────────────────────────────────────────────
with tab2:
    st.markdown("#### Filtros")
    col_f1, col_f2 = st.columns([1, 3])
    with col_f1:
        renda_min_geo = st.slider(
            "Renda mínima (R$)",
            min_value=2500,
            max_value=20000,
            value=10000,
            step=1000,
            key="renda_geo"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("#### Concentração de leads por estado")
    try:
        df_uf = obter_distribuicao_uf(renda_min=renda_min_geo)

        fig_mapa = px.choropleth(
            df_uf,
            geojson="https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/brazil-states.geojson",
            locations='UF',
            featureidkey='properties.sigla',
            color='total_clientes',
            color_continuous_scale=[
                [0, '#0a0e14'],
                [0.3, '#003d1f'],
                [0.6, '#00a855'],
                [1, '#00ff88']
            ],
            scope='south america',
            hover_data={'UF': True, 'total_clientes': ':,', 'renda_media': ':.2f'}
        )
        fig_mapa.update_geos(
            fitbounds="locations",
            visible=False,
            bgcolor='rgba(0,0,0,0)',
        )
        fig_mapa.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'family': 'Georgia, serif', 'color': '#e8eef7'},
            margin={'t': 0, 'b': 0, 'l': 0, 'r': 0},
            height=500,
            coloraxis_colorbar={
                'title': 'Leads',
                'tickfont': {'color': '#e8eef7'},
                'bgcolor': 'rgba(0,0,0,0)',
            }
        )
        st.plotly_chart(fig_mapa, use_container_width=True)

        col_a, col_b = st.columns([1, 1])

        with col_a:
            st.markdown("#### Top 10 estados")
            df_top = df_uf.head(10)
            fig = px.bar(
                df_top.sort_values('total_clientes'),
                x='total_clientes',
                y='UF',
                orientation='h',
                color_discrete_sequence=['#00ff88']
            )
            fig.update_layout(**layout_padrao(400), showlegend=False)
            fig.update_traces(marker_line_width=0)
            fig.update_xaxes(title='Clientes')
            fig.update_yaxes(title='')
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            st.markdown("#### Receita mensal por produto")
            df_prod = obter_portfolio_produtos()
            fig = px.pie(
                df_prod,
                values='receita_mensal',
                names='Produto',
                color_discrete_sequence=CORES_NEON,
                hole=0.5
            )
            fig.update_layout(**layout_padrao(400))
            fig.update_traces(textfont_color='#e8eef7')
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao carregar dados geográficos: {e}")


# ─── TAB 3: Análise Comportamental ──────────────────────────────────
with tab3:
    st.markdown("#### Renda × Ticket Mensal")
    st.markdown(
        '<div style="color: #8a99b0; font-size: 13px; margin-bottom: 16px;">'
        'Cada ponto é um cliente. Identifica concentração natural e outliers.'
        '</div>',
        unsafe_allow_html=True
    )

    try:
        df_scatter = obter_scatter_renda_ticket()
        fig = px.scatter(
            df_scatter,
            x='Renda_Mensal',
            y='ticket_mensal',
            color='produtos',
            size='produtos',
            color_continuous_scale=[
                [0, '#003d1f'],
                [0.5, '#00a855'],
                [1, '#00ff88']
            ],
            hover_data={'UF': True, 'produtos': True},
        )
        fig.update_layout(**layout_padrao(500))
        fig.update_xaxes(title='Renda Mensal (R$)')
        fig.update_yaxes(title='Ticket Mensal (R$)')
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### Concentração de contratos • UF × Produto")
        df_heatmap = obter_heatmap_uf_produto()
        fig = px.imshow(
            df_heatmap,
            color_continuous_scale=[
                [0, '#0a0e14'],
                [0.25, '#003d1f'],
                [0.5, '#006b3f'],
                [0.75, '#00a855'],
                [1, '#00ff88']
            ],
            aspect='auto',
            text_auto='.0f'
        )
        fig.update_layout(**layout_padrao(550))
        fig.update_xaxes(title='')
        fig.update_yaxes(title='')
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao carregar análise comportamental: {e}")


# ─── TAB 4: Segmentação RFM ─────────────────────────────────────────
with tab4:
    st.markdown("### 🎯 Segmentação RFM de Clientes")
    st.markdown("*Recency • Frequency • Monetary Value*")
    
    try:
        with st.spinner('Calculando segmentação RFM...'):
            df_rfm, resumo_rfm = calcular_rfm()
        
        st.markdown("#### 📊 Distribuição por Segmento")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Extrai valores do resumo (sem acentos)
        campeoes = resumo_rfm.loc['Campeoes'] if 'Campeoes' in resumo_rfm.index else {'Total_Clientes': 0, 'Pct_Receita': 0}
        potenciais = resumo_rfm.loc['Potenciais'] if 'Potenciais' in resumo_rfm.index else {'Total_Clientes': 0, 'Pct_Receita': 0}
        em_risco = resumo_rfm.loc['Em Risco'] if 'Em Risco' in resumo_rfm.index else {'Total_Clientes': 0, 'Pct_Receita': 0}
        leais = resumo_rfm.loc['Leais'] if 'Leais' in resumo_rfm.index else {'Total_Clientes': 0, 'Pct_Receita': 0}
        
        with col1:
            st.metric(
                "🏆 Campeões", 
                f"{campeoes['Total_Clientes']:,}",
                f"{campeoes['Pct_Receita']:.1f}% da receita"
            )
        with col2:
            st.metric(
                "⚡ Potenciais", 
                f"{potenciais['Total_Clientes']:,}",
                "Prioridade Cross-sell"
            )
        with col3:
            st.metric(
                "⭐ Leais", 
                f"{leais['Total_Clientes']:,}",
                "Base sólida"
            )
        with col4:
            st.metric(
                "⚠️ Em Risco", 
                f"{em_risco['Total_Clientes']:,}",
                "Ação necessária"
            )
        
        st.markdown("---")
        
        st.markdown("#### 📋 Resumo por Segmento")
        
        resumo_display = resumo_rfm.copy()
        resumo_display['Receita_Total'] = resumo_display['Receita_Total'].apply(lambda x: f"R$ {x/1000:.0f}k")
        resumo_display['Renda_Media'] = resumo_display['Renda_Media'].apply(lambda x: f"R$ {x:.0f}")
        resumo_display['Pct_Base'] = resumo_display['Pct_Base'].apply(lambda x: f"{x:.1f}%")
        resumo_display['Pct_Receita'] = resumo_display['Pct_Receita'].apply(lambda x: f"{x:.1f}%")
        
        st.dataframe(
            resumo_display[['Total_Clientes', 'Pct_Base', 'Receita_Total', 'Pct_Receita', 'Renda_Media', 'Produtos_Medios']],
            use_container_width=True
        )
        
        st.markdown("#### 📊 Distribuição de Clientes por Segmento")
        
        fig = px.bar(
            resumo_rfm.reset_index(),
            x='segmento',
            y='Total_Clientes',
            color='segmento',
            color_discrete_map={
                'Campeoes': '#00ff88',
                'Leais': '#00d4ff',
                'Potenciais': '#b794f6',
                'Em Risco': '#ff6b6b',
                'Hibernando': '#666666',
                'Novos/Outros': '#8a99b0'
            },
            text='Total_Clientes'
        )
        fig.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig.update_layout(
            **layout_padrao(400),
            showlegend=False,
            xaxis_title="",
            yaxis_title="Clientes"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("#### 🎯 Ações Recomendadas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("""
            **Segmentos Prioritários:**
            1. **Potenciais** → Cross-sell de Consórcio
            2. **Em Risco** → Campanha de retenção
            3. **Campeões** → Programa de indicação
            """)
        
        with col2:
            st.info("""
            **Próximos Passos:**
            • Baixar lista de Potenciais
            • Agendar follow-up com Em Risco
            • Criar oferta exclusiva para Campeões
            """)
            
    except Exception as e:
        st.error(f"Erro ao carregar análise RFM: {e}")
        st.info("Certifique-se de que os dados foram gerados (execute o pipeline primeiro)")


# ─── TAB 5: Análise Cohort ──────────────────────────────────────────
with tab5:
    st.markdown("### 📈 Retenção por Safra (Cohort Analysis)")
    st.markdown("*Acompanhe como diferentes grupos de clientes evoluem ao longo do tempo*")
    
    try:
        with st.spinner('Calculando matriz de cohort...'):
            matriz, insights = calcular_cohort_matrix()
        
        if matriz is not None and not matriz.empty:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Retenção Média M1", 
                    f"{insights['retencao_media_m1']:.1f}%",
                    "1º mês"
                )
            with col2:
                st.metric(
                    "Retenção Média M3", 
                    f"{insights['retencao_media_m3']:.1f}%",
                    "3º mês"
                )
            with col3:
                st.metric(
                    "Retenção Média M6", 
                    f"{insights['retencao_media_m6']:.1f}%",
                    "6º mês"
                )
            
            st.markdown("#### 🗺️ Matriz de Retenção (%)")
            st.markdown("*Linhas = mês de entrada | Colunas = meses após entrada*")
            
            # CORREÇÃO AQUI - Layout simplificado
            fig = px.imshow(
                matriz,
                text_auto='.0f',
                aspect='auto',
                color_continuous_scale=[
                    [0, '#ff6b6b'],
                    [0.5, '#f1c40f'],
                    [0.7, '#00d4ff'],
                    [0.85, '#00cc6a'],
                    [1, '#00ff88']
                ],
                labels=dict(x="Meses após entrada", y="Mês de entrada", color="Retenção %")
            )
            
            # Layout aplicado diretamente sem conflitos
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(15, 22, 32, 0.5)',
                font={'family': 'Georgia, serif', 'color': '#e8eef7'},
                height=500,
                margin={'t': 40, 'b': 40, 'l': 40, 'r': 40}
            )
            fig.update_xaxes(tickmode='linear', dtick=1, gridcolor='rgba(0, 255, 136, 0.1)')
            fig.update_yaxes(gridcolor='rgba(0, 255, 136, 0.1)')
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### 💡 Insights Detectados")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if insights['melhor_cohort']:
                    st.success(f"""
                    **✅ Melhor Cohort:** {insights['melhor_cohort']}
                    - Clientes adquiridos neste mês têm a maior retenção
                    """)
                
            with col2:
                if insights['pior_cohort']:
                    st.warning(f"""
                    **⚠️ Pior Cohort:** {insights['pior_cohort']}
                    - Retenção abaixo da média
                    """)
            
            if len(matriz) >= 3:
                st.markdown("#### 📉 Tendência de Retenção")
                
                retencao_media_mensal = matriz.mean()
                
                fig2 = px.line(
                    x=retencao_media_mensal.index,
                    y=retencao_media_mensal.values,
                    markers=True,
                    labels={'x': 'Meses após aquisição', 'y': 'Retenção Média (%)'}
                )
                fig2.update_traces(line_color='#00ff88', line_width=3)
                fig2.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(15, 22, 32, 0.5)',
                    font={'family': 'Georgia, serif', 'color': '#e8eef7'},
                    height=350,
                    margin={'t': 40, 'b': 40, 'l': 40, 'r': 40}
                )
                fig2.update_xaxes(gridcolor='rgba(0, 255, 136, 0.1)')
                fig2.update_yaxes(gridcolor='rgba(0, 255, 136, 0.1)')
                
                st.plotly_chart(fig2, use_container_width=True)
                
        else:
            st.warning("Dados insuficientes para análise de cohort.")
            
    except Exception as e:
        st.error(f"Erro ao carregar análise cohort: {e}")


# ─── TAB 6: Jornada do Cliente ──────────────────────────────────────
with tab6:
    st.markdown("### 🔄 Jornada de Cross-Sell")
    st.markdown("*Fluxo de produtos - Identifique oportunidades de cross-sell*")
    
    try:
        with st.spinner('Analisando jornada dos clientes...'):
            oportunidades = identificar_oportunidades()
            df_jornada, insights_jornada = obter_jornada_produtos()
        
        if not oportunidades.empty:
            st.metric(
                "Total de Jornadas Analisadas", 
                f"{insights_jornada['total_jornadas']:,}",
                "Sequências de produtos"
            )
            
            st.markdown("#### 💡 Principais Oportunidades de Cross-Sell")
            
            oportunidades_display = oportunidades.copy()
            oportunidades_display.columns = ['Produto Origem', 'Produto Destino', 'Clientes', 'Conversão %', 'Recomendação', 'Timing (dias)', 'Canal']
            
            st.dataframe(
                oportunidades_display,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Conversão %": st.column_config.ProgressColumn(
                        "Conversão %",
                        format="%.1f%%",
                        min_value=0,
                        max_value=100,
                    )
                }
            )
            
            st.markdown("#### 🎯 Top 3 Ações Imediatas")
            
            top_3 = oportunidades.head(3)
            
            for idx, row in top_3.iterrows():
                with st.expander(f"💼 **{row['origem']} → {row['destino']}** ({row['conversao']:.1f}% conversão)"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"""
                        **Estratégia Recomendada:**
                        - 🎯 Gatilho: {row['timing_dias']} dias após compra
                        - 📢 Canal: {row['canal']}
                        - 👥 Base: {row['clientes']:,} clientes elegíveis
                        """)
                    
                    with col2:
                        ticket_medio = 200
                        potencial = row['clientes'] * ticket_medio * (row['conversao'] / 100)
                        
                        st.markdown(f"""
                        **Impacto Projetado:**
                        - 💰 Receita potencial: R$ {potencial/1000:.0f}k/mês
                        - 📈 Aumento esperado: +{row['conversao']:.1f}% cross-sell
                        - ⏱️ Time to value: {row['timing_dias']} dias
                        """)
            
            if insights_jornada['fluxos_churn'] is not None and not insights_jornada['fluxos_churn'].empty:
                st.markdown("#### ⚠️ Pontos de Atenção - Churn na Jornada")
                
                churn_display = insights_jornada['fluxos_churn'].copy()
                churn_display.columns = ['Produto', 'Destino (Cancelou)', 'Clientes']
                
                st.dataframe(
                    churn_display,
                    use_container_width=True,
                    hide_index=True
                )
                
                st.warning("""
                **Ação Recomendada:**
                Produtos com alta taxa de cancelamento como primeira compra precisam de:
                - Onboarding mais robusto
                - Acompanhamento nos primeiros 30 dias
                """)
                
        else:
            st.info("Aguardando dados de jornada.")
            
    except Exception as e:
        st.error(f"Erro ao carregar jornada do cliente: {e}")


# ─── TAB 7: Top Leads ───────────────────────────────────────────────
with tab7:
    st.markdown("#### Filtros")
    col_f1, col_f2, col_f3 = st.columns(3)

    try:
        ufs_disponiveis = ["Todos"] + obter_lista_ufs()
    except:
        ufs_disponiveis = ["Todos"]

    with col_f1:
        uf_selecionada = st.selectbox("Estado (UF)", ufs_disponiveis, key="uf_leads")
    with col_f2:
        renda_min_leads = st.slider(
            "Renda mínima (R$)",
            min_value=10000,
            max_value=20000,
            value=15000,
            step=1000,
            key="renda_leads"
        )
    with col_f3:
        qtd_leads = st.slider(
            "Quantidade de leads",
            min_value=10,
            max_value=100,
            value=20,
            step=10,
            key="qtd_leads"
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"#### Top {qtd_leads} leads priorizados para Atlas Consórcios")

    try:
        df_leads = obter_top_leads(
            renda_min=renda_min_leads,
            uf_filtro=uf_selecionada,
            limite=qtd_leads
        )

        if df_leads.empty:
            st.warning("Nenhum lead encontrado com esses filtros.")
        else:
            df_leads['Renda_Mensal'] = df_leads['Renda_Mensal'].apply(
                lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            )
            df_leads['ticket_mensal'] = df_leads['ticket_mensal'].apply(
                lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            )
            df_leads.columns = ['Nome', 'UF', 'Renda Mensal', 'Produtos Ativos', 'Ticket Mensal']
            st.dataframe(df_leads, use_container_width=True, hide_index=True, height=600)
    except Exception as e:
        st.error(f"Erro ao carregar leads: {e}")


# ─── TAB 8: Curva ABC ───────────────────────────────────────────────
with tab8:
    try:
        df_abc = obter_curva_abc()

        if not df_abc.empty:
            col_a, col_b = st.columns([1, 2])

            with col_a:
                st.markdown("#### Distribuição de clientes")
                fig = go.Figure(data=[go.Pie(
                    labels=df_abc['classe'],
                    values=df_abc['clientes'],
                    hole=0.6,
                    marker_colors=['#00ff88', '#00d4ff', '#b794f6']
                )])
                fig.update_layout(**layout_padrao(400))
                fig.update_traces(textfont_color='#0a0e14', textfont_size=14)
                st.plotly_chart(fig, use_container_width=True)

            with col_b:
                st.markdown("#### Participação na receita")
                fig = px.bar(
                    df_abc,
                    x='classe',
                    y='pct_receita',
                    text='pct_receita',
                    color='classe',
                    color_discrete_sequence=['#00ff88', '#00d4ff', '#b794f6']
                )
                fig.update_traces(texttemplate='%{text}%', textposition='outside', marker_line_width=0)
                fig.update_layout(**layout_padrao(400), showlegend=False)
                fig.update_xaxes(title='Classe')
                fig.update_yaxes(title='% da Receita')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Dados da Curva ABC não disponíveis.")
    except Exception as e:
        st.error(f"Erro ao carregar Curva ABC: {e}")


# ═══════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    '<div style="text-align: center; color: #556; font-size: 11px; letter-spacing: 2px; '
    'padding: 24px 0; border-top: 1px solid rgba(0, 255, 136, 0.1); margin-top: 48px;">'
    'PROJETO ARGUS • DATA ENGINEERING CASE STUDY • 2026'
    '</div>',
    unsafe_allow_html=True
)