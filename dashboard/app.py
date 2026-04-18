if df_leads.empty:
    st.warning("Nenhum lead encontrado com esses filtros.")
else:
    # Formata valores monetários
    df_leads["Renda_Mensal_Fmt"] = df_leads["Renda_Mensal"].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    df_leads["ticket_mensal_Fmt"] = df_leads["ticket_mensal"].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    
    # Cria mensagem personalizada para WhatsApp
    df_leads["Mensagem"] = df_leads["Nome"].apply(
        lambda nome: f"Olá {nome.split()[0]}, tudo bem? Vi que você é cliente Atlas e identifiquei uma oportunidade especial de consórcio. Podemos conversar?"
    )
    
    # Cria link do WhatsApp
    df_leads["WhatsApp"] = df_leads.apply(
        lambda row: f"https://wa.me/{row['Telefone']}?text={row['Mensagem'].replace(' ', '%20')}", axis=1
    )
    
    # Exibe tabela com coluna de ação
    st.dataframe(
        df_leads[["Nome", "UF", "Renda_Mensal_Fmt", "produtos_ativos", "ticket_mensal_Fmt", "WhatsApp"]]
        .rename(columns={
            "Renda_Mensal_Fmt": "Renda Mensal",
            "produtos_ativos": "Produtos Ativos",
            "ticket_mensal_Fmt": "Ticket Mensal",
            "WhatsApp": "Ação"
        }),
        use_container_width=True,
        hide_index=True,
        height=600,
        column_config={
            "Ação": st.column_config.LinkColumn(
                "📱 WhatsApp",
                display_text="Abrir Chat"
            )
        }
    )
