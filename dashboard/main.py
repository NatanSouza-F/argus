"""
Orquestrador do pipeline.
Uso:
  python main.py                    → roda tudo
  python main.py --skip-ingestao    → pula a Camada 1
"""
import logging
import time
import sys

from config import configurar_logging
from gerar_dados import main as rodar_ingestao
from exportar_excel import main as rodar_leads
from insights_comerciais import main as rodar_insights

configurar_logging()
log = logging.getLogger(__name__)


def executar_pipeline(pular_ingestao=False):
    inicio = time.time()

    etapas = [
        ("Camada 1 - Ingestão", rodar_ingestao),
        ("Camada 2 - Leads", rodar_leads),
        ("Camada 3 - Insights", rodar_insights),
    ]

    if pular_ingestao:
        etapas = etapas[1:]

    for nome, funcao in etapas:
        log.info(f"Iniciando: {nome}")
        t_etapa = time.time()
        try:
            funcao()
            log.info(f"Concluído: {nome} ({time.time() - t_etapa:.0f}s)")
        except Exception as erro:
            log.error(f"Falha em {nome}: {erro}")
            raise

    log.info(f"Pipeline finalizado em {time.time() - inicio:.0f}s")


if __name__ == "__main__":
    pular = '--skip-ingestao' in sys.argv
    executar_pipeline(pular_ingestao=pular)
