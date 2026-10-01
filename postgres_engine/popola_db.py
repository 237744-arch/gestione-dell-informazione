import pg8000
import json
from postgres_engine.database_config import DatabaseConfig

cfg = DatabaseConfig()

conn = pg8000.connect(
    user=cfg.DB_USER,
    password=cfg.DB_PASSWORD,
    database=cfg.DB_NAME,
    host=cfg.IP_ADDRESS,
    port=cfg.PORT_NUMBER
)
cur = conn.cursor()
cur.execute("TRUNCATE TABLE docs RESTART IDENTITY;")

seen = set()
inseriti = 0
with open("data/wiki_phones_dataset.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        doc = json.loads(line)
        title = doc["title"].strip()
        content = doc["text"].strip()
        key = (title, content)
        if key in seen:
            continue
        seen.add(key)

        full_text = f"{title} {content}"
        cur.execute("""
            INSERT INTO docs (title, content, documento)
            VALUES (%s, %s, to_tsvector('italian', %s))
        """, (title, content, full_text))
        inseriti += 1

conn.commit()
cur.close()
conn.close()

print(f"Dati inseriti nel database PostgreSQL con successo! ({inseriti} documenti unici)")