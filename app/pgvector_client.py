# Uses psycopg2 + pgvector or SQLAlchemy to store vectors in Postgres
from curses import meta
from typing import List
import os
import json
import psycopg2

PG_CONN = os.getenv("POSTGRES_URI") # e.g. postgres://user:pass@host:5432/dbname
PG_TABLE = os.getenv("PGVECTOR_TABLE", "vectors")


class PGVectorClient:
    def __init__(self):
        self.conn = psycopg2.connect(PG_CONN)
        self._ensure_table()

    def _ensure_table(self):
        cur = self.conn.cursor()
        cur.execute(f"CREATE TABLE IF NOT EXISTS {PG_TABLE} (id TEXT PRIMARY KEY, embedding vector, payload TEXT, metadata JSONB)")
        self.conn.commit()
        cur.close()

    def upsert(self, vectors: List[tuple]):
        cur = self.conn.cursor()
        for id_, emb, payload, meta in vectors:
            item_id = id_ or os.urandom(8).hex()
# emb should be a python list; convert to array literal accepted by pgvector: '[' || ...
        cur.execute(f"INSERT INTO {PG_TABLE} (id, embedding, payload, metadata) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO UPDATE SET embedding = EXCLUDED.embedding, payload = EXCLUDED.payload, metadata = EXCLUDED.metadata", (item_id, emb, payload, json.dumps(meta) if meta else None))
        self.conn.commit()
        cur.close()
        return {"upserted": len(vectors)}


    def query(self, embedding, top_k=5):
    # Uses <=> operator from pgvector for cosine/inner product depending on setup
        cur = self.conn.cursor()
        cur.execute(f"SELECT id, payload, metadata, embedding <=> %s as distance FROM {PG_TABLE} ORDER BY distance LIMIT %s", (embedding, top_k))
        rows = cur.fetchall()
        cur.close()
        results = []
        for r in rows:
            results.append({
            'id': r[0],
            'payload': r[1],
            'metadata': r[2],
            'score': r[3]
            })
        return results