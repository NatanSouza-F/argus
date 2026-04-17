"""
Configurações compartilhadas do projeto.
Centraliza conexão com o banco e setup de logging.
"""
import pyodbc
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
    conexao = pyodbc.connect(
        f"Driver={{SQL Server}};Server={server};Database={database};Trusted_Connection=yes;",
        timeout=60  # aumenta tempo de espera para conexões em base grande
    )
    return conexao