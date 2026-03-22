from flask import Flask, request, jsonify
from flask_cors import CORS
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from google import genai
from google.genai import types
import os
from pypdf import PdfReader
from config import GEMINI_API_KEY, MODEL_NAME, EMBEDDING_MODEL

app = Flask(__name__)
CORS(app)

# 50MB max upload size
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

DATA_PATH = "data"
os.makedirs(DATA_PATH, exist_ok=True)

# Configure Gemini client (new SDK)
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# ── Lazy globals (loaded once on first request, not at startup) ────────────────
_embed_model = None
_index = None
_chunks = []
_metadata = []
_initialized = False

def get_embed_model():
    global _embed_model
    if _embed_model is None:
        print("📦 Loading embedding model...")
        _embed_model = SentenceTransformer(EMBEDDING_MODEL)
        print("✅ Embedding model loaded.")
    return _embed_model

def get_index():
    global _index, _chunks, _metadata, _initialized
    if not _initialized:
        _initialized = True
        if (os.path.exists("faiss_index.bin")
                and os.path.exists("chunks.pkl")
                and os.path.exists("metadata.pkl")):
            print("📦 Loading FAISS index...")
            _index = faiss.read_index("faiss_index.bin")
            with open("chunks.pkl", "rb") as f:
                _chunks = pickle.load(f)
            with open("metadata.pkl", "rb") as f:
                _metadata = pickle.load(f)
            print(f"✅ Loaded index with {len(_chunks)} chunks.")
        else:
            print("⚠️  No index found. Starting with empty index.")
            dim = get_embed_model().get_sentence_embedding_dimension()
            _index = faiss.IndexFlatL2(dim)
    return _index


# ── Helpers ────────────────────────────────────────────────────────────────────

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    pages = []
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            pages.append({"text": text, "page": page_num})
    return pages


def chunk_text(text, chunk_size=500, overlap=200):
    result = []
    for j in range(0, len(text), chunk_size - overlap):
        chunk = text[j:j + chunk_size]
        if chunk.strip():
            result.append(chunk)
    return result


def retrieve(query, k=5):
    index = get_index()
    if index.ntotal == 0:
        return []
    k = min(k, index.ntotal)
    embed_model = get_embed_model()
    query_embedding = embed_model.encode(query)
    distances, indices = index.search(np.array([query_embedding]), k)
    results = []
    for i in indices[0]:
        if i < len(_chunks):
            results.append(_chunks[i])
    return results


def generate_answer(query, contexts):
    if not contexts:
        return "No documents have been indexed yet. Please upload a PDF first."

    context_text = "\n\n".join(contexts[:3])
    prompt = f"""You are a helpful AI assistant.
Answer the question clearly and accurately using ONLY the context below.
If the answer is not in the context, say "I don't know".

Context:
{context_text}

Question: {query}
Answer:"""

    response = gemini_client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )
    return response.text.strip()


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    """Health check — does NOT load the model, always responds instantly."""
    return jsonify({
        "status": "ok",
        "model": MODEL_NAME,
        "chunks_loaded": len(_chunks),
        "index_ready": _index.ntotal > 0 if _index else False,
    })


@app.route("/upload", methods=["POST"])
def upload_pdf():
    global _index, _chunks, _metadata

    if "file" not in request.files:
        return jsonify({"error": "No file provided. Use key 'file' in form-data."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported."}), 400

    save_path = os.path.join(DATA_PATH, file.filename)
    file.save(save_path)
    print(f"📄 Saved PDF: {save_path}")

    pages = extract_text_from_pdf(save_path)
    if not pages:
        return jsonify({"error": "Could not extract any text from the PDF."}), 422

    new_chunks = []
    new_metadata = []
    for page in pages:
        for chunk in chunk_text(page["text"]):
            new_chunks.append(chunk)
            new_metadata.append({"source": file.filename, "page": page["page"]})

    if not new_chunks:
        return jsonify({"error": "No usable text chunks found in the PDF."}), 422

    embed_model = get_embed_model()
    index = get_index()

    print(f"🔢 Creating embeddings for {len(new_chunks)} chunks...")
    new_embeddings = np.array(embed_model.encode(new_chunks, show_progress_bar=False))

    index.add(new_embeddings)
    _chunks.extend(new_chunks)
    _metadata.extend(new_metadata)

    faiss.write_index(index, "faiss_index.bin")
    with open("chunks.pkl", "wb") as f:
        pickle.dump(_chunks, f)
    with open("metadata.pkl", "wb") as f:
        pickle.dump(_metadata, f)

    print(f"✅ Added {len(new_chunks)} chunks from '{file.filename}'.")
    return jsonify({
        "message": f"PDF '{file.filename}' uploaded and indexed successfully.",
        "chunks_added": len(new_chunks),
        "filename": file.filename,
        "total_chunks": len(_chunks),
    })


@app.route("/ask", methods=["POST"])
def ask():
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
        return jsonify({"query": query, "answer": answer, "contexts": contexts})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)