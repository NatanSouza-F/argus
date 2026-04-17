"""
Configurações compartilhadas do projeto.
"""
import pyodbc
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
    """Conecta ao Azure SQL Database usando pyodbc com string otimizada"""
    server = os.getenv('DB_SERVER')
    database = os.getenv('DB_NAME')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    
    # String de conexão padrão para Azure SQL
    connection_string = (
        f'DRIVER={{ODBC Driver 18 for SQL Server}};'
        f'SERVER={server},1433;'
        f'DATABASE={database};'
        f'UID={user};'
        f'PWD={password};'
        f'Encrypt=yes;'
        f'TrustServerCertificate=no;'
        f'Connection Timeout=90;'
        f'Login Timeout=90;'
    )
    
    for i in range(tentativas):
        try:
            conn = pyodbc.connect(connection_string)
            return conn
        except Exception as e:
            if i == tentativas - 1:
                raise e
            time.sleep(10)
