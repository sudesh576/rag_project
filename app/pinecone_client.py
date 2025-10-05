# Minimal Pinecone client wrapper
import os
from typing import List
import pinecone

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "rag-index")


class PineconeClient:
    def __init__(self):
        pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
        self.index = pinecone.Index(PINECONE_INDEX)


    def upsert(self, vectors: List[tuple]):
    # vectors: list of tuples (id, embedding, payload_text, metadata)
        upsert_items = []
        for i, (id_, emb, payload, meta) in enumerate(vectors):
            item_id = id_ or f"doc-{os.urandom(6).hex()}"
            upsert_items.append({"id": item_id, "values": emb, "metadata": meta or {"text": payload}})
            res = self.index.upsert(upsert_items)
        return res


    def query(self, embedding, top_k=5):
        res = self.index.query(vector=embedding, top_k=top_k, include_metadata=True, include_values=False)
        matches = []
        for m in res['matches']:
            matches.append({
            'id': m['id'],
            'score': m.get('score'),
            'payload': m['metadata'].get('text') if m.get('metadata') else None,
            'metadata': m.get('metadata')
            })
        return matches