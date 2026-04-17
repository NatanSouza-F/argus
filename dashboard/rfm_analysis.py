"""
Análise RFM - Segmentação de Clientes
Recency, Frequency, Monetary Value
"""
import pandas as pd
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import conectar_banco, configurar_logging

configurar_logging()
log = logging.getLogger(__name__)

# Corrige o path para encontrar o config.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import conectar_banco, configurar_logging

configurar_logging()
log = logging.getLogger(__name__)


def calcular_rfm():
    """
    Calcula scores RFM para segmentação de clientes
    """
    conexao = None
    try:
        conexao = conectar_banco()
        
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
            LEFT JOIN Fato_Contratos f 
                ON c.ID_Cliente = f.ID_Cliente
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
        
        log.info("Calculando segmentação RFM...")
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
        
        log.info(f"Segmentação concluída: {len(df):,} clientes analisados")
        
        return df, resumo
        
    except Exception as erro:
        log.error(f"Erro na análise RFM: {erro}")
        raise
    finally:
        if conexao:
            conexao.close()


def exportar_rfm():
    """Exporta análise RFM para Excel"""
    from datetime import datetime
    
    df, resumo = calcular_rfm()
    
    data_hora = datetime.now().strftime('%Y%m%d_%H%M%S')
    caminho = f'Atlas_RFM_Segmentacao_{data_hora}.xlsx'
    
    with pd.ExcelWriter(caminho, engine='openpyxl') as writer:
        df[df['segmento'] == 'Campeoes'].head(5000).to_excel(writer, sheet_name='Campeoes', index=False)
        df[df['segmento'] == 'Potenciais'].head(5000).to_excel(writer, sheet_name='Potenciais', index=False)
        df[df['segmento'] == 'Em Risco'].head(5000).to_excel(writer, sheet_name='Em Risco', index=False)
        resumo.to_excel(writer, sheet_name='Resumo', index=True)
        df.head(10000).to_excel(writer, sheet_name='Amostra_Geral', index=False)
    
    log.info(f"Relatório RFM salvo: {caminho}")
    return caminho


if __name__ == "__main__":
    exportar_rfm()
