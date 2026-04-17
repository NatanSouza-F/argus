"""
Camada 3 - Insights Comerciais
Gera três análises estratégicas para a equipe comercial:
  1. Churn de alto valor (retenção)
  2. Produto porta de entrada (funil)
  3. Curva ABC de clientes (priorização)
"""
import pandas as pd
import logging
import os
from datetime import datetime

from config import conectar_banco, configurar_logging

configurar_logging()
log = logging.getLogger(__name__)


def buscar_churn_alto_valor(conexao):
    # Clientes com renda alta que cancelaram produto nos últimos 6 meses
    # TOP 50000 limita memória sem prejudicar análise (área comercial trabalha top leads)
    query = """
    SELECT TOP 50000
        c.Nome,
        c.UF,
        c.Renda_Mensal,
        f.Produto AS Produto_Cancelado,
        f.Valor_Mensalidade AS Ticket_Perdido,
        f.Data_Cancelamento
    FROM Dim_Clientes c
    INNER JOIN Fato_Contratos f ON c.ID_Cliente = f.ID_Cliente
    WHERE f.Status_Contrato = 'Cancelado'
      AND c.Renda_Mensal > 10000
      AND f.Data_Cancelamento >= DATEADD(DAY, -180, GETDATE())
    ORDER BY c.Renda_Mensal DESC, f.Data_Cancelamento DESC
    """
    log.info("Insight 1: Churn de alto valor")
    df = pd.read_sql(query, conexao)
    log.info(f"  {len(df):,} clientes de alto valor perdidos")
    return df


def buscar_porta_de_entrada(conexao):
    # Identifica o primeiro produto de cada cliente e calcula taxa de conversão
    query = """
    WITH PrimeiroContrato AS (
        SELECT
            ID_Cliente,
            Produto,
            ROW_NUMBER() OVER (PARTITION BY ID_Cliente ORDER BY ID_Contrato) AS ordem
        FROM Fato_Contratos
    ),
    ProdutoEntrada AS (
        SELECT ID_Cliente, Produto FROM PrimeiroContrato WHERE ordem = 1
    )
    SELECT
        pe.Produto AS Produto_Entrada,
        COUNT(DISTINCT pe.ID_Cliente) AS Clientes_Entraram,
        COUNT(DISTINCT CASE WHEN total.qtd > 1 THEN pe.ID_Cliente END) AS Clientes_Com_Segundo_Produto
    FROM ProdutoEntrada pe
    INNER JOIN (
        SELECT ID_Cliente, COUNT(*) AS qtd FROM Fato_Contratos GROUP BY ID_Cliente
    ) total ON total.ID_Cliente = pe.ID_Cliente
    GROUP BY pe.Produto
    """
    log.info("Insight 2: Produto porta de entrada")
    df = pd.read_sql(query, conexao)

    df['Taxa_Conversao_Pct'] = (
        100 * df['Clientes_Com_Segundo_Produto'] / df['Clientes_Entraram']
    ).round(2)
    df = df.sort_values('Taxa_Conversao_Pct', ascending=False)

    log.info(f"  {len(df)} produtos analisados")
    return df


def buscar_curva_abc(conexao):
    # Classificação ABC usa TOP 100000 priorizando maior receita.
    # Amostra representativa sem sobrecarregar memória.
    query = """
    SELECT TOP 100000
        c.ID_Cliente,
        c.Nome,
        c.UF,
        COUNT(f.ID_Contrato) AS Qtd_Produtos,
        SUM(f.Valor_Mensalidade) AS Receita_Mensal
    FROM Dim_Clientes c
    INNER JOIN Fato_Contratos f
        ON c.ID_Cliente = f.ID_Cliente
        AND f.Status_Contrato = 'Ativo'
    GROUP BY c.ID_Cliente, c.Nome, c.UF
    ORDER BY SUM(f.Valor_Mensalidade) DESC
    """
    log.info("Insight 3: Curva ABC")
    df = pd.read_sql(query, conexao)

    if df.empty:
        return df

    df = df.sort_values('Receita_Mensal', ascending=False).reset_index(drop=True)

    # Classificação ABC: 20% top / 30% meio / 50% cauda
    total = len(df)
    corte_a = int(total * 0.20)
    corte_b = int(total * 0.50)

    df['Classe'] = 'C'
    df.loc[:corte_a, 'Classe'] = 'A'
    df.loc[corte_a:corte_b, 'Classe'] = 'B'

    qtd_a = (df['Classe'] == 'A').sum()
    qtd_b = (df['Classe'] == 'B').sum()
    qtd_c = (df['Classe'] == 'C').sum()
    log.info(f"  A: {qtd_a:,} | B: {qtd_b:,} | C: {qtd_c:,}")

    return df


def exportar_painel(df_churn, df_funil, df_abc):
    data_hora = datetime.now().strftime('%Y%m%d_%H%M%S')
    pasta = os.path.dirname(os.path.abspath(__file__))
    caminho = os.path.join(pasta, f'Atlas_Painel_Insights_{data_hora}.xlsx')

    # Resumo ABC agrupado por classe
    resumo_abc = df_abc.groupby('Classe').agg(
        Total_Clientes=('ID_Cliente', 'count'),
        Receita_Total=('Receita_Mensal', 'sum'),
        Receita_Media=('Receita_Mensal', 'mean')
    ).round(2).reset_index()
    resumo_abc['Pct_Receita'] = (
        100 * resumo_abc['Receita_Total'] / resumo_abc['Receita_Total'].sum()
    ).round(2)

    with pd.ExcelWriter(caminho, engine='openpyxl') as writer:
        df_churn.head(1000).to_excel(writer, sheet_name='1. Churn Alto Valor', index=False)
        df_funil.to_excel(writer, sheet_name='2. Porta de Entrada', index=False)
        df_abc.head(1000).to_excel(writer, sheet_name='3. Curva ABC (Top 1000)', index=False)
        resumo_abc.to_excel(writer, sheet_name='3b. Resumo ABC', index=False)

    log.info(f"Painel salvo: {os.path.basename(caminho)}")


def main():
    conexao = None
    try:
        conexao = conectar_banco()
        df_churn = buscar_churn_alto_valor(conexao)
        df_funil = buscar_porta_de_entrada(conexao)
        df_abc = buscar_curva_abc(conexao)
        exportar_painel(df_churn, df_funil, df_abc)

    except Exception as erro:
        log.error(f"Erro nos insights: {erro}")
        raise

    finally:
        if conexao:
            conexao.close()


if __name__ == "__main__":
    main()
