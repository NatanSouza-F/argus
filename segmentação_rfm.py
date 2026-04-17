# NOVA TAB: Segmentação RFM

with tab3:
    st.markdown("### 🎯 Segmentação de Clientes (RFM)")
    st.markdown("*Recency • Frequency • Monetary*")
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        segmento_selecionado = st.multiselect(
            "Filtrar por segmento:",
            ['Campeões', 'Leais', 'Potenciais', 'Em Risco', 'Hibernando'],
            default=['Campeões', 'Leais', 'Potenciais']
        )
    
    # Métricas RFM (KPIs)
    metricas_rfm = obter_metricas_rfm()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Campeões", f"{metricas_rfm['campeoes']:,}", 
                  f"{metricas_rfm['pct_campeoes']}% da base")
    with col2:
        st.metric("Potenciais", f"{metricas_rfm['potenciais']:,}",
                  "⚡ Prioridade")
    with col3:
        st.metric("Em Risco", f"{metricas_rfm['em_risco']:,}",
                  f"⚠️ {metricas_rfm['receita_risco']}M em risco")
    with col4:
        st.metric("Hibernando", f"{metricas_rfm['hibernando']:,}",
                  "💤 Inativos")
    
    # Gráfico de dispersão 3D (RFM)
    st.markdown("#### Distribuição RFM")
    df_rfm = obter_dados_rfm(segmento_selecionado)
    
    fig = px.scatter_3d(
        df_rfm,
        x='recency',
        y='frequency', 
        z='monetary',
        color='segmento',
        size='monetary',
        color_discrete_map={
            'Campeões': '#00ff88',
            'Leais': '#00d4ff',
            'Potenciais': '#b794f6',
            'Em Risco': '#ff6b6b',
            'Hibernando': '#666666'
        },
        hover_data=['nome', 'ticket_mensal', 'dias_ultima_compra']
    )
    
    fig.update_layout(
        scene=dict(
            xaxis_title='Recency (dias)',
            yaxis_title='Frequency (# produtos)',
            zaxis_title='Monetary (R$)'
        ),
        height=600,
        **layout_padrao()
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabela de ações recomendadas
    st.markdown("#### 🎯 Ações Recomendadas por Segmento")
    
    acoes = pd.DataFrame({
        'Segmento': ['Campeões', 'Potenciais', 'Em Risco'],
        'Ação Recomendada': [
            '🎁 Programa de Indicação (ganhe R$ 100)',
            '📞 Ligação para cross-sell de Consórcio',
            '💌 Oferta de retenção: 20% off próxima mensalidade'
        ],
        'Impacto Estimado': [
            '+R$ 150k/mês em novas receitas',
            '+R$ 320k/mês em cross-sell',
            'Recuperar R$ 180k/mês'
        ],
        'Prioridade': ['Média', '🔥 ALTA', '🔥 ALTA']
    })
    
    st.dataframe(acoes, use_container_width=True, hide_index=True)