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

# Load embedding model first (needed to know dimension for empty index)
print("📦 Loading embedding model...")
embed_model = SentenceTransformer(EMBEDDING_MODEL)
EMBEDDING_DIM = embed_model.get_sentence_embedding_dimension()

# Load or initialize FAISS index and data
print("📦 Loading index...")
if os.path.exists("faiss_index.bin") and os.path.exists("chunks.pkl") and os.path.exists("metadata.pkl"):
    index = faiss.read_index("faiss_index.bin")
    with open("chunks.pkl", "rb") as f:
        chunks = pickle.load(f)
    with open("metadata.pkl", "rb") as f:
        metadata = pickle.load(f)
    print(f"✅ Loaded existing index with {len(chunks)} chunks.")
else:
    # No index found — start with an empty one (uploads will populate it)
    print("⚠️  No index found. Starting with empty index — upload PDFs to populate.")
    index = faiss.IndexFlatL2(EMBEDDING_DIM)
    chunks = []
    metadata = []

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
    result = []
    for j in range(0, len(text), chunk_size - overlap):
        chunk = text[j:j + chunk_size]
        if chunk.strip():
            result.append(chunk)
    return result


def retrieve(query, k=5):
    if index.ntotal == 0:
        return []
    k = min(k, index.ntotal)
    query_embedding = embed_model.encode(query)
    distances, indices = index.search(np.array([query_embedding]), k)
    results = []
    for i in indices[0]:
        if i < len(chunks):
            results.append(chunks[i])
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
    response = gemini_model.generate_content(prompt)
    return response.text.strip()


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/upload", methods=["POST"])
def upload_pdf():
    """
    POST /upload
    Form-data: { "file": <pdf file> }
    Saves PDF to /data, extracts text, builds embeddings,
    and adds them to the live FAISS index.
    Returns: { "message": "...", "chunks_added": N, "filename": "..." }
    """
    global index, chunks, metadata

    if "file" not in request.files:
        return jsonify({"error": "No file provided. Use key 'file' in form-data."}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported."}), 400

    # Save to /data folder
    save_path = os.path.join(DATA_PATH, file.filename)
    file.save(save_path)
    print(f"📄 Saved PDF: {save_path}")

    # Extract text
    pages = extract_text_from_pdf(save_path)
    if not pages:
        return jsonify({"error": "Could not extract any text from the PDF."}), 422

    # Chunk text
    new_chunks = []
    new_metadata = []
    for page in pages:
        page_chunks = chunk_text(page["text"])
        for chunk in page_chunks:
            new_chunks.append(chunk)
            new_metadata.append({"source": file.filename, "page": page["page"]})

    if not new_chunks:
        return jsonify({"error": "No usable text chunks found in the PDF."}), 422

    # Create embeddings
    print(f"🔢 Creating embeddings for {len(new_chunks)} chunks...")
    new_embeddings = embed_model.encode(new_chunks, show_progress_bar=False)
    new_embeddings = np.array(new_embeddings)

    # Add to live FAISS index
    index.add(new_embeddings)
    chunks.extend(new_chunks)
    metadata.extend(new_metadata)

    # Persist updated index and chunks to disk
    faiss.write_index(index, "faiss_index.bin")
    with open("chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)
    with open("metadata.pkl", "wb") as f:
        pickle.dump(metadata, f)

    print(f"✅ Added {len(new_chunks)} chunks from '{file.filename}' to index.")
    return jsonify({
        "message": f"PDF '{file.filename}' uploaded and indexed successfully.",
        "chunks_added": len(new_chunks),
        "filename": file.filename,
        "total_chunks": len(chunks)
    })


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