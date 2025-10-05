from typing import List, Optional
from .embeddings import get_embedding
from .pinecone_client import PineconeClient
from .pgvector_client import PGVectorClient
from .llm import call_llm
import os

VECTOR_BACKEND = os.getenv("VECTOR_BACKEND", "pinecone")
pine = None
pgv = None

def _get_clients():
    global pine, pgv
    if VECTOR_BACKEND == "pinecone":
        if pine is None:
            pine = PineconeClient()
        return pine
    else:
        if pgv is None:
            pgv = PGVectorClient()
        return pgv

def ingest_documents(docs: List[str], ids: Optional[List[str]] = None, metadata: Optional[List[dict]] = None):
    client = _get_clients()
    embeddings = [get_embedding(d) for d in docs]
    ids = ids or [None] * len(docs)
    metadata = metadata or [None] * len(docs)
    return client.upsert(vectors=list(zip(ids, embeddings, docs, metadata)))

def query_semantic_search(query: str, top_k: int = 5):
    client = _get_clients()
    q_emb = get_embedding(query)
    results = client.query(q_emb, top_k=top_k)
    context = "\n\n".join([r["payload"] for r in results if r.get("payload")])
    prompt = f"""You are a helpful assistant. Use the following context to answer the question.

CONTEXT:
{context}

QUESTION:
{query}

Answer concisely."""
    llm_resp = call_llm(prompt)
    return {"answers": llm_resp, "matches": results}

def get_health():
    return {"vector_backend": VECTOR_BACKEND}
