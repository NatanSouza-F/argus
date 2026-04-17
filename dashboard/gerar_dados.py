"""
Camada 1 - Ingestão
Gera a base simulada de clientes e contratos no SQL Server.
"""
import random
import logging
import time
import os

from config import conectar_banco, configurar_logging

configurar_logging()
log = logging.getLogger(__name__)

TOTAL_CLIENTES = int(os.getenv('TOTAL_CLIENTES', 5_000_000))
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 50_000))

PRODUTOS = [
    ('Atlas Proteção Auto', 150.00),
    ('Atlas Proteção Vida', 80.00),
    ('Atlas Club', 120.00),
    ('NomadPass', 200.00),
]

UFS = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
       'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
       'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']

NOMES = [
    "Ana Silva", "Carlos Souza", "Maria Oliveira", "João Santos", "Fernanda Lima",
    "Pedro Costa", "Juliana Ferreira", "Lucas Alves", "Beatriz Pereira", "Rafael Gomes",
    "Camila Ribeiro", "Thiago Carvalho", "Larissa Martins", "Rodrigo Araújo", "Amanda Rocha",
    "Bruno Mendes", "Patrícia Nunes", "Felipe Barbosa", "Gabriela Correia", "Eduardo Moreira",
    "Isabela Dias", "Marcelo Vieira", "Letícia Monteiro", "Gustavo Cardoso", "Tatiane Pinto",
]


def gerar_cpf_aleatorio():
    return f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}"


def gerar_data_aleatoria():
    ano = random.randint(2020, 2024)
    mes = random.randint(1, 12)
    dia = random.randint(1, 28)
    return f"{ano:04d}-{mes:02d}-{dia:02d}"


def mostrar_progresso(atual, total, inicio):
    pct = atual / total
    preenchido = int(40 * pct)
    barra = '█' * preenchido + '░' * (40 - preenchido)
    decorrido = time.time() - inicio
    eta = (decorrido / pct - decorrido) if pct > 0 else 0
    print(f'\r  [{barra}] {atual:,}/{total:,} ({pct:.1%}) | {decorrido:.0f}s | ETA {eta:.0f}s',
          end='', flush=True)


def inserir_clientes(cursor, conexao):
    log.info(f"Inserindo {TOTAL_CLIENTES:,} clientes")
    inicio = time.time()
    inseridos = 0
    sql = "INSERT INTO Dim_Clientes (Nome, CPF, UF, Renda_Mensal, Data_Cadastro) VALUES (?,?,?,?,?)"

    while inseridos < TOTAL_CLIENTES:
        tamanho = min(CHUNK_SIZE, TOTAL_CLIENTES - inseridos)
        batch = []
        for _ in range(tamanho):
            batch.append((
                random.choice(NOMES),
                gerar_cpf_aleatorio(),
                random.choice(UFS),
                round(random.uniform(2500, 20000), 2),
                gerar_data_aleatoria(),
            ))

        cursor.executemany(sql, batch)
        conexao.commit()
        inseridos += tamanho
        mostrar_progresso(inseridos, TOTAL_CLIENTES, inicio)

    print()
    log.info(f"Clientes inseridos em {time.time() - inicio:.0f}s")


def distribuir_contratos(cursor, conexao):
    log.info("Buscando IDs dos clientes")
    cursor.execute("SELECT ID_Cliente FROM Dim_Clientes")
    ids_clientes = [linha[0] for linha in cursor.fetchall()]

    log.info(f"Distribuindo contratos para {len(ids_clientes):,} clientes")
    inicio = time.time()
    total_contratos = 0
    sql = "INSERT INTO Fato_Contratos (ID_Cliente, Produto, Valor_Mensalidade, Status_Contrato) VALUES (?,?,?,?)"

    batch = []
    for i, id_cliente in enumerate(ids_clientes):
        quantidade = random.randint(1, 2)
        produtos_selecionados = random.sample(PRODUTOS, quantidade)

        for nome_produto, valor in produtos_selecionados:
            batch.append((id_cliente, nome_produto, valor, 'Ativo'))
            total_contratos += 1

        if len(batch) >= CHUNK_SIZE:
            cursor.executemany(sql, batch)
            conexao.commit()
            batch = []

        if (i + 1) % CHUNK_SIZE == 0:
            mostrar_progresso(i + 1, len(ids_clientes), inicio)

    # Commit do que sobrou
    if batch:
        cursor.executemany(sql, batch)
        conexao.commit()

    print()
    log.info(f"{total_contratos:,} contratos inseridos em {time.time() - inicio:.0f}s")


def main():
    conexao = None
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()
        inserir_clientes(cursor, conexao)
        distribuir_contratos(cursor, conexao)
        log.info("Ingestão concluída")

    except Exception as erro:
        log.error(f"Erro na ingestão: {erro}")
        if conexao:
            conexao.rollback()
        raise

    finally:
        if conexao:
            conexao.close()


if __name__ == "__main__":
    main()
