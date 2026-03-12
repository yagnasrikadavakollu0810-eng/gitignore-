#app.py

from dotenv import load_dotenv
import os
from groq import Groq
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env file. Check your .env!")

print("Loaded Key:", api_key)  # Debug to confirm key loaded

# -----------------------------
# Initialize Groq client
# -----------------------------
client = Groq(api_key=api_key)

# -----------------------------
# Load embedding model
# -----------------------------
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# Load documents from file
# -----------------------------
# Make sure you have data.txt in project root with text data
with open("data.txt", "r", encoding="utf-8") as f:
    documents = f.readlines()

# -----------------------------
# Create embeddings
# -----------------------------
doc_embeddings = embedding_model.encode(documents)
doc_embeddings = np.array(doc_embeddings).astype("float32")

# -----------------------------
# Create FAISS index
# -----------------------------
dimension = doc_embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(doc_embeddings)

# -----------------------------
# Retrieval function
# -----------------------------
def retrieve(query, top_k=3):
    query_embedding = embedding_model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")
    distances, indices = index.search(query_embedding, top_k)
    return [documents[i] for i in indices[0]]

# -----------------------------
# Generate answer function
# -----------------------------
def generate_answer(query):
    retrieved_docs = retrieve(query)
    context = "\n".join(retrieved_docs)

    prompt = f"""
Answer the question based only on the context below.

Context:
{context}

Question:
{query}

Answer:
"""

    # -----------------------------
    # Groq chat completion
    # -----------------------------
    response = client.chat.completions.create(
        model="groq/compound-mini",  # <-- use a model your key can access
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content, retrieved_docs

# -----------------------------
# Main execution
# -----------------------------
if __name__ == "__main__":
    query = input("Enter your question: ")
    answer, sources = generate_answer(query)

    print("\nAnswer:\n", answer)
    print("\nSources:")
    for src in sources:
        print("-", src.strip())
