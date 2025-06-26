import sys
import os
import csv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from psycopg2.extras import execute_values
from psycopg2.pool import ThreadedConnectionPool
from urllib.parse import urlparse

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
os.environ['FLASK_CONTEXT'] = 'development'

from app import create_app, db
from app.models.alumnos import Alumnos


CSV_FILE ='alumnos.csv'
BATCH_SIZE = 100_000  # cantidad de registros por lote, aumentar a 200_000 si se tiene suficiente memoria
MAX_WORKERS = 6       # numero de hilos para inserción paralela, aumentar a 8/16 segun cpu
POOL_MINCONN = MAX_WORKERS
POOL_MAXCONN = MAX_WORKERS

def parse_dsn(sqlalchemy_uri):
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
        dsn_params = parse_dsn(app.config['SQLALCHEMY_DATABASE_URI'])
        pool = ThreadedConnectionPool(
            minconn=POOL_MINCONN,
            maxconn=POOL_MAXCONN,
            **dsn_params
        )
        conn_main = db.engine.raw_connection()
        cur_main = conn_main.cursor()
        table.create(db.engine, checkfirst=True)
        cur_main.execute(f"ALTER TABLE {table_name} DISABLE TRIGGER ALL;")
        cur_main.execute(f"ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {table_name}_pkey;")
        cur_main.execute(f"DROP INDEX IF EXISTS idx_{table_name}_nro_documento;")
        cur_main.execute(f"ALTER TABLE {table_name} SET UNLOGGED;")
        cur_main.execute(f"ALTER TABLE {table_name} SET (autovacuum_enabled = false);")
        conn_main.commit()
        def insertar_lote(batch_rows):
   
            conn = pool.getconn()
            cur = conn.cursor()
            insert_sql = f"INSERT INTO {table_name} ({cols_sql}) VALUES %s"
            execute_values(cur, insert_sql, batch_rows, page_size=len(batch_rows))
            conn.commit()
            cur.close()
            pool.putconn(conn)
        start = time.time()
        total = 0
        futures = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor, \
             open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  
            batch = []
            for row in reader:
                if len(row) < len(cols):
                    continue
                batch.append(tuple(row[i] for i in range(len(cols))))
                total += 1
                if len(batch) >= BATCH_SIZE:
                    futures.append(executor.submit(insertar_lote, batch.copy()))
                    batch.clear()
            if batch:
                futures.append(executor.submit(insertar_lote, batch.copy()))
            for fut in as_completed(futures):
                fut.result()
        elapsed = time.time() - start
        cur_main.execute(f"ALTER TABLE {table_name} SET LOGGED;")
        cur_main.execute(f"ALTER TABLE {table_name} ADD CONSTRAINT {table_name}_pkey PRIMARY KEY (nro_legajo);")
        cur_main.execute(f"CREATE INDEX idx_{table_name}_nro_documento ON {table_name}(nro_documento);")
        cur_main.execute(f"ALTER TABLE {table_name} ENABLE TRIGGER ALL;")
        conn_main.commit()
        cur_main.close()
        conn_main.close()
        pool.closeall()
        print(f"Carga finalizada. total registros: {total}. tiempo: {elapsed:.2f}s.")

if __name__ == '__main__':
    print("Iniciando importación de alumnos")
    importar_alumnos()
