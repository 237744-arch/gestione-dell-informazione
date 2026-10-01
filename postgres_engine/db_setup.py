import pg8000
from postgres_engine.database_config import DatabaseConfig

def create_db(cfg):
    conn = pg8000.connect(database='postgres',
                            user=cfg.DB_USER,
                            password=cfg.DB_PASSWORD,
                            host=cfg.IP_ADDRESS,
                            port=cfg.PORT_NUMBER)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f'CREATE DATABASE "{cfg.DB_NAME}";')
    cur.close(); conn.close()
    print(f"Database {cfg.DB_NAME} creato.")

def create_table(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS docs (
          id SERIAL PRIMARY KEY,
          title TEXT,
          content TEXT,
          documento TSVECTOR
        );
    """)
    conn.commit()
    cur.close()
    print("Tabella docs creata.")

if __name__ == '__main__':
    cfg = DatabaseConfig()
    try:
        create_db(cfg)
    except Exception as e:
        print(f"Nota: il database potrebbe esistere già ({e})")

    conn = pg8000.connect(
        database=cfg.DB_NAME,
        user=cfg.DB_USER,
        password=cfg.DB_PASSWORD,
        host=cfg.IP_ADDRESS,
        port=cfg.PORT_NUMBER
    )
    create_table(conn)
    conn.close()