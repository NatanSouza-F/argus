"""
Camada de acesso a dados do dashboard Argus.
"""
import pymssql
import pandas as pd
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

UFS_VALIDAS = [
    'AC','AL','AP','AM','BA','CE','DF','ES','GO','MA',
    'MT','MS','MG','PA','PB','PR','PE','PI','RJ','RN',
    'RS','RO','RR','SC','SP','SE','TO'
]


def conectar_banco():
    """Conexão usando pymssql"""
    server = os.getenv('DB_SERVER')
    database = os.getenv('DB_NAME')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    
    return pymssql.connect(
        server=server,
        user=user,
        password=password,
        database=database,
        timeout=90,
        login_timeout=60
    )
