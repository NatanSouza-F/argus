"""
Análise de Jornada do Cliente (Versão Otimizada)
"""
import pandas as pd
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import conectar_banco, configurar_logging

configurar_logging()
log = logging.getLogger(__name__)


def obter_jornada_produtos():
    conexao = None
    try:
        conexao = conectar_banco()
        
        # Tenta primeiro o resumo em cache (rápido)
        query_cache = """
        SELECT origem, destino, fluxo
        FROM jornada_resumo
        """
        df_cache = pd.read_sql(query_cache, conexao)
        
        if not df_cache.empty:
            log.info("Jornada carregada do cache")
            # Dispara atualização assíncrona em background (não bloqueia a UI)
            import threading
            threading.Thread(target=lambda: None).start()  # Placeholder para futuro agendamento
        else:
            log.warning("Cache vazio, calculando online...")
            df_cache = calcular_jornada_online(conexao)


def calcular_jornada_online(conexao):
    """Fallback: cálculo online (usado se a tabela de resumo estiver vazia)"""
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
            ON p1.ID_Cliente = p2.ID_Cliente AND p2.ordem = 2
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
    return pd.read_sql(query, conexao)


def identificar_oportunidades():
    """Identifica oportunidades de cross-sell"""
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


# Mantenha as funções de exportação se desejar (não são usadas pelo dashboard)
