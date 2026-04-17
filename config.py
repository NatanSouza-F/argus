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
        timeout=90,
        login_timeout=60
    )
