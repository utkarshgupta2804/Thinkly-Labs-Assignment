from flask import Flask, request, jsonify
from flask_cors import CORS
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import os
from pypdf import PdfReader
from config import GEMINI_API_KEY, MODEL_NAME, EMBEDDING_MODEL

app = Flask(__name__)
CORS(app)

# 50MB max upload size
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Configure Gemini client
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel(MODEL_NAME)

DATA_PATH = "data"
os.makedirs(DATA_PATH, exist_ok=True)

# Load FAISS index and data on startup
print("📦 Loading index...")
if not os.path.exists("faiss_index.bin"):
    raise FileNotFoundError("faiss_index.bin not found. Run build_index.py first.")

index = faiss.read_index("faiss_index.bin")

with open("chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

with open("metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

print("📦 Loading embedding model...")
embed_model = SentenceTransformer(EMBEDDING_MODEL)
print("✅ Flask RAG backend ready!")


# ── Helpers ────────────────────────────────────────────────────────────────────

def extract_text_from_pdf(pdf_path):
    """Extract text from every page of a PDF file."""
    reader = PdfReader(pdf_path)
    pages = []
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            pages.append({"text": text, "page": page_num})
    return pages


def chunk_text(text, chunk_size=500, overlap=200):
    """Split text into overlapping chunks."""
    chunks = []
    for j in range(0, len(text), chunk_size - overlap):
        chunk = text[j:j + chunk_size]
        if chunk.strip():
            chunks.append(chunk)
    return chunks


def retrieve(query, k=5):
    query_embedding = embed_model.encode(query)
    distances, indices = index.search(np.array([query_embedding]), k)
    results = []
    for i in indices[0]:
        if i < len(chunks):
            results.append(chunks[i])
    return results


def generate_answer(query, contexts):
    context_text = "\n\n".join(contexts[:3])
    prompt = f"""You are a helpful AI assistant.
Answer the question clearly and accurately using ONLY the context below.
If the answer is not in the context, say "I don't know".

Context:
{context_text}

Question: {query}
Answer:"""
    response = gemini_model.generate_content(prompt)
    return response.text.strip()


@app.route("/ask", methods=["POST"])
def ask():
    """
    POST /ask
    Body: { "query": "your question here", "k": 5 (optional) }
    Returns: { "query": "...", "answer": "...", "contexts": [...] }
    """
    data = request.get_json()

    if not data or "query" not in data:
        return jsonify({"error": "Missing 'query' field in request body"}), 400

    query = data["query"].strip()
    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400

    k = data.get("k", 5)

    try:
        contexts = retrieve(query, k=k)
        answer = generate_answer(query, contexts)
        return jsonify({
            "query": query,
            "answer": answer,
            "contexts": contexts
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "model": MODEL_NAME,
        "chunks_loaded": len(chunks),
        "index_ready": index.ntotal > 0
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)