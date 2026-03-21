import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from config import OPENAI_API_KEY, MODEL_NAME

client = OpenAI(api_key=OPENAI_API_KEY)

# Load everything
print("📦 Loading index...")
index = faiss.read_index("faiss_index.bin")

with open("chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

with open("metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

print("📦 Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve(query, k=5):
    query_embedding = model.encode(query)

    distances, indices = index.search(
        np.array([query_embedding]), k
    )

    results = []
    for i in indices[0]:
        if i < len(chunks):
            results.append(chunks[i])

    return results



def generate_answer(query, contexts):
    context_text = "\n\n".join(contexts[:3])

    prompt = f"""
You are a helpful AI assistant.

Answer the question clearly and accurately using ONLY the context below.

If the answer is not in the context, say "I don't know".

Context:
{context_text}

Question: {query}

Answer:
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,  # e.g. gpt-4o-mini
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()


# CLI loop
print("\n🤖 RAG Ready! Ask your questions (type 'exit' to quit)\n")

while True:
    query = input("❓ Question: ")

    if query.lower() == "exit":
        break

    contexts = retrieve(query)
    answer = generate_answer(query, contexts)

    print("\n💡 Answer:\n", answer)
    print("\n" + "="*50 + "\n")