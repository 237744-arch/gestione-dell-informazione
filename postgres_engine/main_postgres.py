from postgres_engine.database_config import DatabaseConfig
from postgres_engine.connection import db_connection
from postgres_engine.db_setup import create_db, create_table
from postgres_engine.indexing import create_indexes
from postgres_engine.search_engine import SearchEngine

def main_postgres():
    """Setup e interfaccia di ricerca per PostgreSQL."""
    cfg  = DatabaseConfig()
    conn = db_connection(cfg)
    if not conn:
        create_db(cfg)
        conn = db_connection(cfg)
        if not conn:
            raise RuntimeError("Impossibile connettersi al database PostgreSQL dopo la creazione")

    create_table(conn)
    create_indexes(conn)

    engine = SearchEngine(cfg, conn)
    print("Scegli ranking: 1) TF-IDF   2) BM25   (invio per uscire)")
    while True:
        choice = input(">> ").strip()
        if choice not in ('1', '2'):
            break
        query = input("Query: ").strip()
        if choice == '1':
            results = engine.tfidf_search(query)
        else:
            results = engine.bm25_search(query)
        for title, score in results:
            print(f"{score:.3f}  {title}")

    conn.close()

if __name__ == '__main__':
    main_postgres()