import json
from postgres_engine.database_config import DatabaseConfig
from postgres_engine.connection      import db_connection
from postgres_engine.search_engine   import SearchEngine as PgEngine
from whoosh_engine.IRmodel           import search_weighted as whoosh_search, search_by_field as whoosh_search_by_field

with open("benchmark/Query_per_golden_list.json", "r", encoding="utf-8") as f:
    queries = list(json.load(f).values())  # ogni elemento: {"query": ..., "field": ...}

# 1) PostgreSQL
db_cfg = DatabaseConfig()
conn = db_connection(db_cfg)
if conn is None:
    raise RuntimeError("Impossibile connettersi al database PostgreSQL")
pg = PgEngine(db_cfg, conn)

bench_postgres = []
for q in queries:
    if q["field"]:
        results = [title for title, _ in pg.search_by_field(q["query"], q["field"])]
    else:
        results = [title for title, _ in pg.tfidf_search(q["query"])]
    bench_postgres.append(results)

conn.close()

# 2) Whoosh
bench_whoosh = []
for q in queries:
    if q["field"]:
        bench_whoosh.append([t for t, _ in whoosh_search_by_field(q["query"], q["field"])])
    else:
        bench_whoosh.append([t for t, _ in whoosh_search(q["query"])])

with open("benchmark/bench_save.json", "w", encoding="utf-8") as f:
    json.dump({
        "bench_postgres": bench_postgres,
        "bench_whoosh": bench_whoosh
    }, f, indent=4, ensure_ascii=False)

print("Benchmark completato (PostgreSQL + Whoosh) e salvato in benchmark/bench_save.json")