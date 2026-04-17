"""
Camada 2 - Identificação de Leads
Identifica clientes com perfil para cross-sell e calcula score de propensão.
"""
import pandas as pd
import logging
import os
from datetime import datetime

from config import conectar_banco, configurar_logging

configurar_logging()
log = logging.getLogger(__name__)


def buscar_leads(conexao):
    # LEFT JOIN + IS NULL é mais performático que NOT IN em grandes volumes
    query = """
    SELECT
        c.ID_Cliente,
        c.Nome,
        c.UF,
        c.Renda_Mensal,
        COUNT(f.ID_Contrato) AS Qtd_Produtos_Ativos,
        MAX(CASE WHEN f.Produto LIKE '%Proteção%' THEN 1 ELSE 0 END) AS Tem_Seguro,
        MAX(CASE WHEN f.Produto = 'Atlas Club' THEN 1 ELSE 0 END) AS Tem_Club,
        MAX(CASE WHEN f.Produto = 'NomadPass' THEN 1 ELSE 0 END) AS Tem_NomadPass
    FROM Dim_Clientes c
    INNER JOIN Fato_Contratos f
        ON c.ID_Cliente = f.ID_Cliente
        AND f.Status_Contrato = 'Ativo'
    LEFT JOIN Fato_Contratos fc
        ON c.ID_Cliente = fc.ID_Cliente
        AND fc.Produto = 'Atlas Consórcios'
    WHERE c.Renda_Mensal > 10000
      AND fc.ID_Contrato IS NULL
    GROUP BY c.ID_Cliente, c.Nome, c.UF, c.Renda_Mensal
    """
    log.info("Buscando leads qualificados")
    df = pd.read_sql(query, conexao)
    log.info(f"{len(df):,} leads encontrados")
    return df


def calcular_score(df):
    # Score baseado em perfil socioeconômico + engajamento com a marca
    df['Score'] = 0
    df.loc[df['Renda_Mensal'] > 15000, 'Score'] += 2
    df.loc[(df['Renda_Mensal'] > 10000) & (df['Renda_Mensal'] <= 15000), 'Score'] += 1
    df.loc[df['Tem_Seguro'] == 1, 'Score'] += 1
    df.loc[df['Tem_Club'] == 1, 'Score'] += 1
    df.loc[df['Tem_NomadPass'] == 1, 'Score'] += 1
    df.loc[df['Qtd_Produtos_Ativos'] > 1, 'Score'] += 1

    df['Propensao'] = pd.cut(
        df['Score'],
        bins=[-1, 1, 3, 6],
        labels=['Baixa', 'Média', 'Alta']
    )

    df['Sugestao'] = 'Cross-Sell: Atlas Consórcios'
    df = df.sort_values('Score', ascending=False)

    qtd_alta = (df['Propensao'] == 'Alta').sum()
    qtd_media = (df['Propensao'] == 'Média').sum()
    qtd_baixa = (df['Propensao'] == 'Baixa').sum()
    log.info(f"Score: {qtd_alta:,} Alta | {qtd_media:,} Média | {qtd_baixa:,} Baixa")

    return df


def exportar_relatorio(df):
    data_hora = datetime.now().strftime('%Y%m%d_%H%M%S')
    pasta = os.path.dirname(os.path.abspath(__file__))
    caminho = os.path.join(pasta, f'Atlas_CrossSell_Leads_{data_hora}.xlsx')

    colunas_leads = ['Nome', 'UF', 'Renda_Mensal', 'Qtd_Produtos_Ativos',
                     'Score', 'Propensao', 'Sugestao']

    # Excel tem limite de 1.048.576 linhas por aba.
    # Estratégia: top priorizado + visões agregadas.
    LIMITE_EXCEL = 1_000_000  # margem de segurança

    top_leads = df.head(10000)

    resumo_uf = df.groupby('UF').agg(
        Total_Leads=('ID_Cliente', 'count'),
        Score_Medio=('Score', 'mean'),
        Renda_Media=('Renda_Mensal', 'mean')
    ).round(2).sort_values('Total_Leads', ascending=False).reset_index()

    distribuicao_score = df['Score'].value_counts().sort_index().reset_index()
    distribuicao_score.columns = ['Score', 'Quantidade']

    distribuicao_prop = df['Propensao'].value_counts().reset_index()
    distribuicao_prop.columns = ['Propensao', 'Quantidade']

    # Base completa filtrada pelos scores mais altos (cabe no limite do Excel)
    leads_score_alto = df[df['Score'] >= 4][colunas_leads].head(LIMITE_EXCEL)
    leads_score_medio = df[(df['Score'] >= 2) & (df['Score'] < 4)][colunas_leads].head(LIMITE_EXCEL)

    with pd.ExcelWriter(caminho, engine='openpyxl') as writer:
        top_leads[colunas_leads].to_excel(writer, sheet_name='Top 10k Leads', index=False)
        leads_score_alto.to_excel(writer, sheet_name='Score Alto (4+)', index=False)
        leads_score_medio.to_excel(writer, sheet_name='Score Médio (2-3)', index=False)
        resumo_uf.to_excel(writer, sheet_name='Resumo por UF', index=False)
        distribuicao_score.to_excel(writer, sheet_name='Distribuição por Score', index=False)
        distribuicao_prop.to_excel(writer, sheet_name='Distribuição Propensão', index=False)

    log.info(f"Relatório salvo: {os.path.basename(caminho)}")
    log.info(f"  Top 10k: {len(top_leads):,} | Alto: {len(leads_score_alto):,} | Médio: {len(leads_score_medio):,}")


def main():
    conexao = None
    try:
        conexao = conectar_banco()
        df_leads = buscar_leads(conexao)

        if df_leads.empty:
            log.warning("Nenhum lead encontrado")
            return

        df_leads = calcular_score(df_leads)
        exportar_relatorio(df_leads)

    except Exception as erro:
        log.error(f"Erro no ETL: {erro}")
        raise

    finally:
        if conexao:
            conexao.close()


if __name__ == "__main__":
    main()