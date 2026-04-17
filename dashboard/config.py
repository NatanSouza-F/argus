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
        timeout=120,        # Aumentado para 2 minutos
        login_timeout=90,    # Aumentado para 1.5 minutos
        tds_version='7.1'    # Melhor compatibilidade com Azure
    )
