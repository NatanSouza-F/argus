"""
Configurações compartilhadas do projeto.
"""
import pymssql
import logging
import os
import time
from dotenv import load_dotenv

load_dotenv()

def configurar_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )

def conectar_banco(tentativas=3):
    """Tenta conectar ao Azure SQL Database com retry automático"""
    server = os.getenv('DB_SERVER')
    database = os.getenv('DB_NAME')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')

    for i in range(tentativas):
        try:
            conn = pymssql.connect(
                server=server,
                user=user,
                password=password,
                database=database,
                timeout=120,
                login_timeout=90,
                tds_version='7.1'
            )
            return conn
        except Exception as e:
            if i == tentativas - 1:
                raise e
            time.sleep(10)  # espera 10 segundos antes de tentar de novo
