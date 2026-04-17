"""
Configurações compartilhadas do projeto.
"""
import pymssql
import logging
import os
from dotenv import load_dotenv

load_dotenv()


def configurar_logging():
    """Configura logging básico para os módulos"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )


def conectar_banco():
    """Retorna uma conexão com o Azure SQL Database"""
    server = os.getenv('DB_SERVER')
    database = os.getenv('DB_NAME')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')

    return pymssql.connect(
        server=server,
        user=user,
        password=password,
        database=database,
        timeout=120,
        login_timeout=90,
        tds_version='7.1'
    )
