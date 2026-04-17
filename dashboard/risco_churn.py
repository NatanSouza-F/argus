# NOVA TAB: Risco de Churn

with tab7:
    st.markdown("### ⚠️ Previsão de Churn (Próximos 60 dias)")
    
    # Carrega modelo
    modelo = carregar_modelo_churn()
    
    # Métricas de risco
    metricas_risco = obter_metricas_risco()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Clientes em Risco Alto", 
                  f"{metricas_risco['risco_alto']:,}",
                  f"{metricas_risco['pct_risco']:.1f}% da base")
    with col2:
        st.metric("Receita em Risco", 
                  f"R$ {metricas_risco['receita_risco']/1e6:.1f}M",
                  "⚠️ Ação urgente")
    with col3:
        st.metric("Churn Previsto (60d)", 
                  f"{metricas_risco['churn_previsto']:.1f}%",
                  f"{metricas_risco['variacao']:+.1f}pp vs mês anterior")
    
    # Tabela de clientes em risco
    st.markdown("#### 🔴 Clientes com Maior Probabilidade de Churn")
    
    df_risco = prever_clientes_risco(modelo)
    
    # Formatação condicional
    def colorir_risco(val):
        if val > 90:
            return 'background-color: #ff000033; color: #ff6b6b'
        elif val > 70:
            return 'background-color: #ffa50033; color: #f1c40f'
        return ''
    
    st.dataframe(
        df_risco.style.applymap(colorir_risco, subset=['Probabilidade']),
        use_container_width=True,
        hide_index=True,
        height=400
    )
    
    # Ações recomendadas
    st.markdown("#### 🎯 Plano de Ação Anti-Churn")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **Ações Imediatas (24h)**
        - 📞 Ligar para top 50 clientes em risco
        - 🎁 Oferecer 1 mês grátis de Proteção
        - 📊 Agendar revisão de conta
        """)
    
    with col2:
        st.success("""
        **Ações Preventivas (7 dias)**
        - 📧 Campanha de engajamento para score 70-90%
        - 💬 Pesquisa de satisfação
        - 🎯 Programa de fidelidade acelerado
        """)
    
    # Feature importance
    st.markdown("#### 📊 O que mais influencia o churn?")
    
    importancia = obter_feature_importance(modelo)
    
    fig = px.bar(
        importancia,
        x='importancia',
        y='feature',
        orientation='h',
        color='importancia',
        color_continuous_scale='reds'
    )
    fig.update_layout(**layout_padrao(300))
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption("💡 Insight: Tempo sem interação é o maior preditor de churn")
