# verificar_estrutura.py
import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

server = os.getenv('DB_SERVER')
database = os.getenv('DB_NAME')

conn = pyodbc.connect(
    f"Driver={{SQL Server}};Server={server};Database={database};Trusted_Connection=yes;"
)

cursor = conn.cursor()

# Ver colunas da Dim_Clientes
print("=== Dim_Clientes ===")
cursor.execute("SELECT TOP 1 * FROM Dim_Clientes")
columns = [column[0] for column in cursor.description]
print(f"Colunas: {columns}\n")

# Ver colunas da Fato_Contratos
print("=== Fato_Contratos ===")
cursor.execute("SELECT TOP 1 * FROM Fato_Contratos")
columns = [column[0] for column in cursor.description]
print(f"Colunas: {columns}\n")

conn.close()