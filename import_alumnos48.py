import sys
import os
import csv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import psycopg2
from psycopg2.extras import execute_values
from psycopg2.pool import ThreadedConnectionPool
from urllib.parse import urlparse

"""
autor: nicolás andino
fecha: 2025-06-25
versión: 7.7

descripción:
    Script optimizado para importar alumnos desde un CSV usando el modelo Alumnos.
    Reduce paralelización y tamaño de lote para aliviar CPU.
"""

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
os.environ['FLASK_CONTEXT'] = 'development'

from app import create_app, db
from app.models.alumnos import Alumnos

CSV_FILE = 'alumnos_limpio.csv'  # Asegúrate de que este archivo exista en el directorio base
BATCH_SIZE = 50_000  # Reducido para menos overhead
MAX_WORKERS = 2  # Reducido para aliviar CPU
POOL_MINCONN = MAX_WORKERS
POOL_MAXCONN = MAX_WORKERS
COMMIT_INTERVAL = 5  # Commit cada 5 lotes

def parse_dsn(sqlalchemy_uri):
    """Convierte URI SQLAlchemy a parámetros para psycopg2.connect."""
    result = urlparse(sqlalchemy_uri)
    return {
        'dbname': result.path.lstrip('/'),
        'user': result.username,
        'password': result.password,
        'host': result.hostname,
        'port': result.port,
    }

def importar_alumnos():
    app = create_app()
    with app.app_context():
        table = Alumnos.__table__
        table_name = table.name
        cols = [c.name for c in table.columns]
        cols_sql = ', '.join(cols)

        # Parseamos los parámetros de conexión para psycopg2
        dsn_params = parse_dsn(app.config['SQLALCHEMY_DATABASE_URI'])

        # Pool de conexiones
        pool = ThreadedConnectionPool(
            minconn=POOL_MINCONN,
            maxconn=POOL_MAXCONN,
            **dsn_params
        )

        # Conexión principal para preparar la tabla
        conn_main = db.engine.raw_connection()
        cur_main = conn_main.cursor()
        table.create(db.engine, checkfirst=True)
        cur_main.execute(f"ALTER TABLE {table_name} DISABLE TRIGGER ALL;")
        cur_main.execute(f"ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {table_name}_pkey;")
        cur_main.execute(f"DROP INDEX IF EXISTS idx_{table_name}_nro_documento;")
        cur_main.execute(f"ALTER TABLE {table_name} SET UNLOGGED;")
        cur_main.execute("SET synchronous_commit = 'off';")  # Reducir carga en CPU
        conn_main.commit()

        # Función de inserción
        def insertar_lote(batch_rows, conn):
            cur = conn.cursor()
            insert_sql = f"INSERT INTO {table_name} ({cols_sql}) VALUES %s"
            execute_values(cur, insert_sql, batch_rows, page_size=len(batch_rows))
            cur.close()

        # Procesamiento con CSV
        start = time.time()
        total = 0
        commit_counter = 0
        futures = []

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor, \
             open(CSV_FILE, 'r', encoding='utf-8', buffering=8192) as f:  # Buffer más grande
            reader = csv.reader(f)
            next(reader, None)  # Saltar encabezado
            batch = []
            conn = pool.getconn()

            for row in reader:
                if len(row) < len(cols):
                    continue
                batch.append(tuple(row))  # Asume orden correcto
                total += 1
                if len(batch) >= BATCH_SIZE:
                    futures.append(executor.submit(insertar_lote, batch.copy(), conn))
                    batch.clear()
                    commit_counter += 1
                    if commit_counter >= COMMIT_INTERVAL:
                        conn.commit()
                        commit_counter = 0

            if batch:
                futures.append(executor.submit(insertar_lote, batch.copy(), conn))
            conn.commit()  # Commit final
            pool.putconn(conn)

        # Esperar a que todas las inserciones terminen
        for fut in as_completed(futures):
            fut.result()

        elapsed = time.time() - start

        # Restauramos constraints e índices
        cur_main.execute(f"ALTER TABLE {table_name} SET LOGGED;")
        cur_main.execute(f"ALTER TABLE {table_name} ADD CONSTRAINT {table_name}_pkey PRIMARY KEY (nro_legajo);")
        cur_main.execute(f"CREATE INDEX idx_{table_name}_nro_documento ON {table_name}(nro_documento);")
        cur_main.execute(f"ALTER TABLE {table_name} ENABLE TRIGGER ALL;")
        conn_main.commit()

        # Cerramos
        cur_main.close()
        conn_main.close()
        pool.closeall()

        print(f"Carga desde CSV finalizada. Total registros: {total}. Tiempo: {elapsed:.2f}s.")

if __name__ == '__main__':
    print("Iniciando importación de alumnos desde CSV usando modelo Alumnos…")
    importar_alumnos()