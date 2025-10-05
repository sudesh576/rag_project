import os, requests

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_embedding(text: str):
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set")
    url = "https://api.openai.com/v1/embeddings"
    payload = {"input": text, "model": "text-embedding-3-small"}
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    r = requests.post(url, json=payload, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data["data"][0]["embedding"]
