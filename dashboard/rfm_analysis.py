"""
Análise RFM - Segmentação de Clientes (Versão Otimizada)
"""
import pandas as pd
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import conectar_banco, configurar_logging

configurar_logging()
log = logging.getLogger(__name__)


def calcular_rfm():
    """
    Retorna dados RFM, priorizando tabela de resumo pré-calculada.
    """
    conexao = None
    try:
        conexao = conectar_banco()
        
        # 1. Tenta obter da tabela de resumo (atualizada nas últimas 24h)
        query_resumo = """
        SELECT segmento, total_clientes, receita_total, renda_media, 
               produtos_medios, pct_base, pct_receita
        FROM rfm_resumo
        WHERE ultima_atualizacao >= DATEADD(hour, -24, GETDATE())
        """
        
        df_resumo = pd.read_sql(query_resumo, conexao)
        
        if not df_resumo.empty:
            log.info("RFM carregado da tabela de resumo (cache de 24h)")
            resumo = df_resumo.set_index('segmento')
            resumo.columns = ['Total_Clientes', 'Receita_Total', 'Renda_Media',
                              'Produtos_Medios', 'Pct_Base', 'Pct_Receita']
            # DataFrame vazio para compatibilidade com a interface
            df_vazio = pd.DataFrame(columns=['ID_Cliente', 'Nome', 'segmento'])
            return df_vazio, resumo
        else:
            log.warning("Tabela de resumo desatualizada. Atualize com EXEC sp_atualizar_rfm.")
            # Fallback para cálculo online (caso a procedure não tenha rodado)
            return calcular_rfm_online(conexao)
            
    except Exception as erro:
        log.error(f"Erro na análise RFM: {erro}")
        raise
    finally:
        if conexao:
            conexao.close()


def calcular_rfm_online(conexao):
    """Fallback: cálculo completo (mais lento)"""
    query = """
    WITH rfm_base AS (
        SELECT 
            c.ID_Cliente,
            c.Nome,
            c.UF,
            c.Renda_Mensal,
            DATEDIFF(day, c.Data_Cadastro, GETDATE()) as recency_dias,
            COUNT(DISTINCT CASE WHEN f.Status_Contrato = 'Ativo' THEN f.ID_Contrato END) as frequency,
            ISNULL(SUM(CASE WHEN f.Status_Contrato = 'Ativo' THEN f.Valor_Mensalidade END), 0) as monetary
        FROM Dim_Clientes c
        LEFT JOIN Fato_Contratos f ON c.ID_Cliente = f.ID_Cliente
        GROUP BY c.ID_Cliente, c.Nome, c.UF, c.Renda_Mensal, c.Data_Cadastro
    ),
    rfm_scores AS (
        SELECT *,
            NTILE(5) OVER (ORDER BY recency_dias ASC) as r_score,
            NTILE(5) OVER (ORDER BY frequency DESC) as f_score,
            NTILE(5) OVER (ORDER BY monetary DESC) as m_score
        FROM rfm_base
        WHERE monetary > 0
    )
    SELECT 
        ID_Cliente,
        Nome,
        UF,
        Renda_Mensal,
        recency_dias,
        frequency,
        monetary,
        r_score,
        f_score,
        m_score,
        (r_score + f_score + m_score) as score_total,
        CASE 
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Campeoes'
            WHEN r_score >= 4 AND f_score >= 3 AND m_score >= 4 THEN 'Leais'
            WHEN r_score >= 4 AND f_score <= 2 AND m_score >= 3 THEN 'Potenciais'
            WHEN r_score <= 2 AND f_score >= 3 AND m_score >= 3 THEN 'Em Risco'
            WHEN r_score <= 2 AND f_score <= 2 AND m_score <= 2 THEN 'Hibernando'
            WHEN r_score <= 2 AND frequency = 0 THEN 'Inativos'
            ELSE 'Novos/Outros'
        END as segmento
    FROM rfm_scores
    """
    
    df = pd.read_sql(query, conexao)
    
    resumo = df.groupby('segmento').agg({
        'ID_Cliente': 'count',
        'monetary': 'sum',
        'Renda_Mensal': 'mean',
        'frequency': 'mean'
    }).round(2)
    
    resumo.columns = ['Total_Clientes', 'Receita_Total', 'Renda_Media', 'Produtos_Medios']
    resumo['Pct_Base'] = (resumo['Total_Clientes'] / resumo['Total_Clientes'].sum() * 100).round(1)
    resumo['Pct_Receita'] = (resumo['Receita_Total'] / resumo['Receita_Total'].sum() * 100).round(1)
    
    return df, resumo


# Mantenha as funções de exportação se desejar
def exportar_rfm():
    """Exporta análise RFM para Excel"""
    from datetime import datetime
    
    df, resumo = calcular_rfm()
    
    data_hora = datetime.now().strftime('%Y%m%d_%H%M%S')
    caminho = f'Atlas_RFM_Segmentacao_{data_hora}.xlsx'
    
    with pd.ExcelWriter(caminho, engine='openpyxl') as writer:
        resumo.to_excel(writer, sheet_name='Resumo', index=True)
        if not df.empty:
            df.head(10000).to_excel(writer, sheet_name='Amostra_Geral', index=False)
    
    log.info(f"Relatório RFM salvo: {caminho}")
    return caminho


if __name__ == "__main__":
    exportar_rfm()
