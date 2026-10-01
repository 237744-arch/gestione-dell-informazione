import json
import psycopg2
from whoosh import index
from whoosh.qparser import QueryParser
from whoosh import scoring

# ==========================================
# 1. CONFIGURAZIONE INIZIALE
# ==========================================
DB_NAME = "smartsearch"
DB_USER = "postgres"
DB_PASS = "admin" 
DB_HOST = "localhost"

WHOOSH_INDEX_DIR = "whoosh_engine/index" 

# Il dizionario con le tue 10 query del Gold Standard
queries = {
  "UIN1": {"query": "schermo oled", "field": "content"},
  "UIN2": {"query": "snapdragon 8", "field": "content"},
  "UIN3": {"query": "pieghevole", "field": "content"},
  "UIN4": {"query": "Iphone 16 fotocamera frontale", "field": None},
  "UIN5": {"query": "display 120Hz", "field": "content"},
  "UIN6": {"query": "5G ricarica ultra rapida", "field": "content"},
  "UIN7": {"query": "foto intelligenza artificiale", "field": "content"},
  "UIN8": {"query": "Oneplus one", "field": None},
  "UIN9": {"query": "Iphone pro", "field": None},
  "UIN10": {"query": "Xiaomi", "field": "title"}
}
# ==========================================
# 2. FUNZIONI DI RICERCA
# ==========================================

def search_postgresql(cursor, query_text, search_field):
    if search_field is None:
        search_field = "content"
    
    sql = f"""
        SELECT title 
        FROM docs, plainto_tsquery('italian', %s) query
        WHERE to_tsvector('italian', {search_field}) @@ query
        ORDER BY ts_rank_cd(to_tsvector('italian', {search_field}), query) DESC
        LIMIT 10;
    """
    cursor.execute(sql, (query_text,))
    results = cursor.fetchall()
    return [row[0] for row in results]

def search_whoosh(searcher_tfidf, searcher_bm25, schema, query_text, search_field):
    if search_field is None:
        search_field = "content"
        
    parser = QueryParser(search_field, schema)
    parsed_query = parser.parse(query_text)
    
    # Ricerca con TF-IDF (usa il searcher dedicato)
    results_tfidf = searcher_tfidf.search(parsed_query, limit=10)
    lista_tfidf = [hit["title"] for hit in results_tfidf]
    
    # Ricerca con BM25 (usa il searcher dedicato)
    results_bm25 = searcher_bm25.search(parsed_query, limit=10)
    lista_bm25 = [hit["title"] for hit in results_bm25]
    
    return lista_tfidf, lista_bm25

# ==========================================
# 3. ESECUZIONE DEL BENCHMARK
# ==========================================

def main():
    bench_save_data = {}
    
    try:
        print("Connessione al database PostgreSQL...")
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
        cursor = conn.cursor()
        
        print("Apertura indice Whoosh...")
        ix = index.open_dir(WHOOSH_INDEX_DIR)
        
        # Apriamo DUE searcher, uno per ogni tipo di ranking
        with ix.searcher(weighting=scoring.TF_IDF()) as searcher_tfidf, \
             ix.searcher(weighting=scoring.BM25F()) as searcher_bm25:
             
            print("\nInizio estrazione risultati per le UIN...")
            
            for uin, info in queries.items():
                q_text = info["query"]
                q_field = info["field"]
                
                print(f"Elaborazione {uin}: '{q_text}' (Campo: {q_field or 'content'})")
                
                # PostgreSQL
                pg_results = search_postgresql(cursor, q_text, q_field)
                
                # Whoosh (passiamo entrambi i searcher)
                tfidf_results, bm25_results = search_whoosh(searcher_tfidf, searcher_bm25, ix.schema, q_text, q_field)
                
                bench_save_data[uin] = {
                    "PostgreSQL": pg_results,
                    "Whoosh_TFIDF": tfidf_results,
                    "Whoosh_Weighted": bm25_results
                }
                
        with open("bench_save.json", "w", encoding="utf-8") as f:
            json.dump(bench_save_data, f, indent=4, ensure_ascii=False)
            
        print("\nFinito! Il file 'bench_save.json' è stato generato con successo.")

    except Exception as e:
        print(f"Si è verificato un errore: {e}")
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()