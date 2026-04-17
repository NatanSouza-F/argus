"""
Análise de Jornada do Cliente - Sankey Diagram
Mostra fluxo de produtos: 1º → 2º produto
"""
import pandas as pd
import logging
import sys
import os

# Corrige o path para encontrar o config.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import conectar_banco, configurar_logging

configurar_logging()
log = logging.getLogger(__name__)


def obter_jornada_produtos():
    """
    Extrai sequência de produtos por cliente
    """
    conexao = None
    try:
        conexao = conectar_banco()
        
        query = """
        WITH produtos_ordenados AS (
            SELECT 
                ID_Cliente,
                Produto,
                ID_Contrato,
                ROW_NUMBER() OVER (PARTITION BY ID_Cliente ORDER BY ID_Contrato) as ordem
            FROM Fato_Contratos
            WHERE Status_Contrato = 'Ativo'
        ),
        jornada AS (
            SELECT 
                p1.Produto as primeiro_produto,
                p2.Produto as segundo_produto,
                COUNT(DISTINCT p1.ID_Cliente) as total_clientes
            FROM produtos_ordenados p1
            LEFT JOIN produtos_ordenados p2 
                ON p1.ID_Cliente = p2.ID_Cliente 
                AND p2.ordem = 2
            WHERE p1.ordem = 1
            GROUP BY p1.Produto, p2.Produto
        )
        SELECT 
            ISNULL(primeiro_produto, 'Sem produto') as origem,
            ISNULL(segundo_produto, 'Parou no primeiro') as destino,
            total_clientes as fluxo
        FROM jornada
        WHERE total_clientes >= 10
        ORDER BY total_clientes DESC
        """
        
        log.info("Analisando jornada de produtos...")
        df = pd.read_sql(query, conexao)
        
        if df.empty:
            log.warning("Sem dados de jornada")
            return pd.DataFrame(), {'total_jornadas': 0, 'fluxos_churn': pd.DataFrame(), 'fluxos_sucesso': pd.DataFrame()}
        
        fluxos_churn = df[df['destino'] == 'Parou no primeiro'].nlargest(3, 'fluxo')
        fluxos_sucesso = df[df['destino'] != 'Parou no primeiro'].nlargest(5, 'fluxo')
        
        insights = {
            'fluxos_churn': fluxos_churn,
            'fluxos_sucesso': fluxos_sucesso,
            'total_jornadas': df['fluxo'].sum()
        }
        
        log.info(f"Jornada analisada: {len(df)} fluxos, {insights['total_jornadas']:,} clientes")
        
        return df, insights
        
    except Exception as erro:
        log.error(f"Erro na análise de jornada: {erro}")
        raise
    finally:
        if conexao:
            conexao.close()


def identificar_oportunidades():
    """
    Identifica oportunidades de cross-sell baseado na jornada
    """
    df, insights = obter_jornada_produtos()
    
    if df.empty:
        return pd.DataFrame()
    
    oportunidades = []
    
    for _, row in insights['fluxos_sucesso'].iterrows():
        if row['destino'] != 'Parou no primeiro':
            total_origem = df[df['origem'] == row['origem']]['fluxo'].sum()
            taxa_conversao = (row['fluxo'] / total_origem * 100) if total_origem > 0 else 0
            
            oportunidades.append({
                'origem': row['origem'],
                'destino': row['destino'],
                'clientes': int(row['fluxo']),
                'conversao': round(taxa_conversao, 1),
                'recomendacao': f"Apos {row['origem']}, oferecer {row['destino']}",
                'timing_dias': 30,
                'canal': 'Email automatico' if taxa_conversao > 20 else 'Ligacao consultor'
            })
    
    return pd.DataFrame(oportunidades)


def exportar_jornada():
    """Exporta análise de jornada para Excel"""
    from datetime import datetime
    
    df, insights = obter_jornada_produtos()
    
    if df.empty:
        log.warning("Nada para exportar")
        return
    
    oportunidades = identificar_oportunidades()
    
    data_hora = datetime.now().strftime('%Y%m%d_%H%M%S')
    caminho = f'Atlas_Jornada_Cliente_{data_hora}.xlsx'
    
    with pd.ExcelWriter(caminho, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Fluxos_Completos', index=False)
        if not oportunidades.empty:
            oportunidades.to_excel(writer, sheet_name='Oportunidades', index=False)
        if not insights['fluxos_churn'].empty:
            insights['fluxos_churn'].to_excel(writer, sheet_name='Fluxos_Churn', index=False)
    
    log.info(f"Relatório Jornada salvo: {caminho}")
    return caminho


if __name__ == "__main__":
    exportar_jornada()
