"""
Configurações compartilhadas do projeto.
"""
import pymssql
import logging
import os
from dotenv import load_dotenv

load_dotenv()


def configurar_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )


def conectar_banco():
    server = os.getenv('DB_SERVER')
    database = os.getenv('DB_NAME')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    
    return pymssql.connect(
        server=server,
        user=user,
        password=password,
        database=database,
        timeout=90,           # ← AUMENTADO para 90 segundos
        login_timeout=60,     # ← Timeout de login
        tds_version='7.0'     # ← Compatibilidade com Azure
    )
