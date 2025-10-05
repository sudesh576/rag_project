from flask import Flask, request, jsonify
from app.services import ingest_documents, query_semantic_search, get_health

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", **get_health()})

@app.route("/ingest", methods=["POST"])
def ingest():
    data = request.get_json()
    if not data or "docs" not in data:
        return jsonify({"error": "No documents provided"}), 400
    result = ingest_documents(
        docs=data["docs"],
        ids=data.get("ids"),
        metadata=data.get("metadata")
    )
    return jsonify({"indexed": result})

@app.route("/query", methods=["POST"])
def query():
    data = request.get_json()
    if not data or "query" not in data:
        return jsonify({"error": "Missing 'query'"}), 400
    res = query_semantic_search(
        query=data["query"],
        top_k=data.get("top_k", 5)
    )
    return jsonify(res)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
