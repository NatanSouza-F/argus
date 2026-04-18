"""
Camada de acesso a dados do dashboard Argus.
"""
import pyodbc
import pandas as pd
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

UFS_VALIDAS = [
    'AC','AL','AP','AM','BA','CE','DF','ES','GO','MA',
    'MT','MS','MG','PA','PB','PR','PE','PI','RJ','RN',
    'RS','RO','RR','SC','SP','SE','TO'
]

def conectar_banco():
    from config import conectar_banco as _conectar
    return _conectar()

@st.cache_data(ttl=3600)
def obter_kpis_gerais():
    conexao = conectar_banco()
    query = """
    SELECT
        (SELECT COUNT(*) FROM Dim_Clientes) AS total_clientes,
        (SELECT COUNT(*) FROM Fato_Contratos) AS total_contratos,
        (SELECT COUNT(*) FROM Fato_Contratos WHERE Status_Contrato = 'Ativo') AS contratos_ativos,
        (SELECT SUM(Valor_Mensalidade) FROM Fato_Contratos WHERE Status_Contrato = 'Ativo') AS mrr,
        (SELECT AVG(Renda_Mensal) FROM Dim_Clientes) AS renda_media
    """
    df = pd.read_sql(query, conexao)
    conexao.close()
    return df.iloc[0]

@st.cache_data(ttl=3600)
def obter_taxa_conversao():
    conexao = conectar_banco()
    query = """
    SELECT
        (SELECT COUNT(DISTINCT ID_Cliente) FROM Fato_Contratos WHERE Produto = 'Atlas Consórcios') AS com_consorcio,
        (SELECT COUNT(*) FROM Dim_Clientes) AS total
    """
    df = pd.read_sql(query, conexao)
    conexao.close()
    if df.iloc[0]['total'] > 0:
        return (df.iloc[0]['com_consorcio'] / df.iloc[0]['total']) * 100
    return 0

@st.cache_data(ttl=3600)
def obter_distribuicao_uf(renda_min=10000):
    conexao = conectar_banco()
    ufs_str = ",".join([f"'{uf}'" for uf in UFS_VALIDAS])
    query = f"""
    SELECT
        c.UF,
        COUNT(DISTINCT c.ID_Cliente) AS total_clientes,
        AVG(c.Renda_Mensal) AS renda_media
    FROM Dim_Clientes c
    INNER JOIN Fato_Contratos f
        ON c.ID_Cliente = f.ID_Cliente
        AND f.Status_Contrato = 'Ativo'
    WHERE c.Renda_Mensal > {renda_min}
      AND c.UF IN ({ufs_str})
    GROUP BY c.UF
    ORDER BY total_clientes DESC
    """
    df = pd.read_sql(query, conexao)
    conexao.close()
    return df

@st.cache_data(ttl=3600)
def obter_portfolio_produtos():
    conexao = conectar_banco()
    query = """
    SELECT
        Produto,
        COUNT(*) AS contratos,
        AVG(Valor_Mensalidade) AS ticket_medio,
        SUM(Valor_Mensalidade) AS receita_mensal
    FROM Fato_Contratos
    WHERE Status_Contrato = 'Ativo'
    GROUP BY Produto
    ORDER BY receita_mensal DESC
    """
    df = pd.read_sql(query, conexao)
    conexao.close()
    return df

@st.cache_data(ttl=3600)
def obter_segmentacao_renda():
    conexao = conectar_banco()
    query = """
    SELECT
        CASE
            WHEN Renda_Mensal <= 5000   THEN '01. Até R$ 5k'
            WHEN Renda_Mensal <= 10000  THEN '02. R$ 5k - 10k'
            WHEN Renda_Mensal <= 15000  THEN '03. R$ 10k - 15k'
            WHEN Renda_Mensal <= 18000  THEN '04. R$ 15k - 18k'
            ELSE '05. Acima de R$ 18k'
        END AS faixa,
        COUNT(*) AS total
    FROM Dim_Clientes
    GROUP BY
        CASE
            WHEN Renda_Mensal <= 5000   THEN '01. Até R$ 5k'
            WHEN Renda_Mensal <= 10000  THEN '02. R$ 5k - 10k'
            WHEN Renda_Mensal <= 15000  THEN '03. R$ 10k - 15k'
            WHEN Renda_Mensal <= 18000  THEN '04. R$ 15k - 18k'
            ELSE '05. Acima de R$ 18k'
        END
    ORDER BY faixa
    """
    df = pd.read_sql(query, conexao)
    conexao.close()
    return df

@st.cache_data(ttl=3600)
def obter_top_leads(renda_min=15000, uf_filtro=None, limite=20):
    conexao = conectar_banco()
    ufs_str = ",".join([f"'{uf}'" for uf in UFS_VALIDAS])
    where_uf = f"AND c.UF = '{uf_filtro}'" if uf_filtro and uf_filtro != "Todos" else ""
    query = f"""
    SELECT TOP {limite}
        c.ID_Cliente,
        c.Nome,
        c.UF,
        c.Renda_Mensal,
        COUNT(f.ID_Contrato) AS produtos_ativos,
        SUM(f.Valor_Mensalidade) AS ticket_mensal
    FROM Dim_Clientes c
    INNER JOIN Fato_Contratos f
        ON c.ID_Cliente = f.ID_Cliente
        AND f.Status_Contrato = 'Ativo'
    LEFT JOIN Fato_Contratos fc
        ON c.ID_Cliente = fc.ID_Cliente
        AND fc.Produto = 'Atlas Consórcios'
    WHERE c.Renda_Mensal > {renda_min}
      AND fc.ID_Contrato IS NULL
      AND c.UF IN ({ufs_str})
      {where_uf}
    GROUP BY c.ID_Cliente, c.Nome, c.UF, c.Renda_Mensal
    ORDER BY c.Renda_Mensal DESC, COUNT(f.ID_Contrato) DESC
    """
    df = pd.read_sql(query, conexao)
    conexao.close()
    
    # Gera telefone fictício baseado no ID (substituir por coluna real quando disponível)
    df['Telefone'] = df['ID_Cliente'].apply(lambda x: f"55{ (x % 999999999) + 1100000000 }")
    
    return df

@st.cache_data(ttl=3600)
def obter_evolucao_cadastros():
    conexao = conectar_banco()
    query = """
    SELECT
        YEAR(Data_Cadastro) AS ano,
        MONTH(Data_Cadastro) AS mes,
        COUNT(*) AS novos_clientes
    FROM Dim_Clientes
    GROUP BY YEAR(Data_Cadastro), MONTH(Data_Cadastro)
    ORDER BY ano, mes
    """
    df = pd.read_sql(query, conexao)
    conexao.close()
    df['periodo'] = df['ano'].astype(str) + '-' + df['mes'].astype(str).str.zfill(2)
    df['acumulado'] = df['novos_clientes'].cumsum()
    return df

@st.cache_data(ttl=3600)
def obter_heatmap_uf_produto():
    conexao = conectar_banco()
    ufs_str = ",".join([f"'{uf}'" for uf in UFS_VALIDAS])
    query = f"""
    SELECT
        c.UF,
        f.Produto,
        COUNT(*) AS total
    FROM Dim_Clientes c
    INNER JOIN Fato_Contratos f
        ON c.ID_Cliente = f.ID_Cliente
        AND f.Status_Contrato = 'Ativo'
    WHERE c.UF IN ({ufs_str})
    GROUP BY c.UF, f.Produto
    """
    df = pd.read_sql(query, conexao)
    conexao.close()
    return df.pivot(index='UF', columns='Produto', values='total').fillna(0)

@st.cache_data(ttl=3600)
def obter_curva_abc():
    conexao = conectar_banco()
    query = """
    SELECT TOP 10000
        c.ID_Cliente,
        c.UF,
        SUM(f.Valor_Mensalidade) AS receita_mensal
    FROM Dim_Clientes c
    INNER JOIN Fato_Contratos f
        ON c.ID_Cliente = f.ID_Cliente
        AND f.Status_Contrato = 'Ativo'
    GROUP BY c.ID_Cliente, c.UF
    ORDER BY SUM(f.Valor_Mensalidade) DESC
    """
    df = pd.read_sql(query, conexao)
    conexao.close()
    df = df.sort_values('receita_mensal', ascending=False).reset_index(drop=True)
    total = len(df)
    corte_a = int(total * 0.20)
    corte_b = int(total * 0.50)
    df['classe'] = 'C'
    df.loc[:corte_a, 'classe'] = 'A'
    df.loc[corte_a:corte_b, 'classe'] = 'B'
    resumo = df.groupby('classe').agg(
        clientes=('ID_Cliente', 'count'),
        receita_total=('receita_mensal', 'sum')
    ).reset_index()
    resumo['pct_receita'] = (100 * resumo['receita_total'] / resumo['receita_total'].sum()).round(2)
    return resumo

@st.cache_data(ttl=3600)
def obter_scatter_renda_ticket():
    conexao = conectar_banco()
    ufs_str = ",".join([f"'{uf}'" for uf in UFS_VALIDAS])
    query = f"""
    SELECT TOP 2000
        c.Renda_Mensal,
        SUM(f.Valor_Mensalidade) AS ticket_mensal,
        COUNT(f.ID_Contrato) AS produtos,
        c.UF
    FROM Dim_Clientes c
    INNER JOIN Fato_Contratos f
        ON c.ID_Cliente = f.ID_Cliente
        AND f.Status_Contrato = 'Ativo'
    WHERE c.UF IN ({ufs_str})
      AND c.Renda_Mensal > 5000
    GROUP BY c.ID_Cliente, c.Renda_Mensal, c.UF
    ORDER BY NEWID()
    """
    df = pd.read_sql(query, conexao)
    conexao.close()
    return df

@st.cache_data(ttl=3600)
def obter_lista_ufs():
    conexao = conectar_banco()
    ufs_str = ",".join([f"'{uf}'" for uf in UFS_VALIDAS])
    query = f"""
    SELECT DISTINCT UF 
    FROM Dim_Clientes
    WHERE UF IN ({ufs_str})
    ORDER BY UF
    """
    df = pd.read_sql(query, conexao)
    conexao.close()
    return df['UF'].tolist()

import joblib
import os

@st.cache_resource
def carregar_modelo():
    """Carrega o modelo preditivo treinado."""
    caminho_modelo = os.path.join(os.path.dirname(__file__), '..', 'modelo_cross_sell.pkl')
    if not os.path.exists(caminho_modelo):
        return None
    data = joblib.load(caminho_modelo)
    return data['modelo'], data['features']

def prever_probabilidade(df_leads):
    """Aplica o modelo aos leads e retorna array de probabilidades."""
    modelo, features = carregar_modelo()
    if modelo is None:
        return np.zeros(len(df_leads))
    
    # Prepara features no mesmo formato do treino
    df = df_leads.copy()
    # One-hot encoding para UF (deve coincidir com as top UFs do treino)
    top_ufs = [f.split('_')[1] for f in features if f.startswith('UF_') and f != 'UF_OUTROS']
    df['UF_agg'] = df['UF'].apply(lambda x: x if x in top_ufs else 'OUTROS')
    df = pd.get_dummies(df, columns=['UF_agg'], prefix='UF')
    
    # Garante que todas as colunas esperadas existam
    for col in features:
        if col not in df.columns:
            df[col] = 0
    X = df[features]
    
    # Probabilidade da classe positiva (target=1)
    probas = modelo.predict_proba(X)[:, 1]
    return probas
