import numpy as np
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from utils import load_pdfs_from_folder, chunk_text
from tqdm import tqdm
from config import EMBEDDING_MODEL

DATA_PATH = "data"

print("📄 Loading PDFs...")
texts, metadata = load_pdfs_from_folder(DATA_PATH)

print("✂️ Chunking text...")
chunks, chunk_metadata = chunk_text(texts)

print("🔢 Creating embeddings...")
model = SentenceTransformer(EMBEDDING_MODEL)

embeddings = []
for chunk in tqdm(chunks):
    embeddings.append(model.encode(chunk))

embeddings = np.array(embeddings)

print("🧱 Building FAISS index...")
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

print("💾 Saving index and data...")
faiss.write_index(index, "faiss_index.bin")

with open("chunks.pkl", "wb") as f:
    pickle.dump(chunks, f)

with open("metadata.pkl", "wb") as f:
    pickle.dump(metadata, f)

print("✅ Index built successfully!")