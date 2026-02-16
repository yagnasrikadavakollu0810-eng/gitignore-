"""
QUICK REFERENCE: Code Snippets for Each Step
=============================================
Use these snippets to understand what each step does
"""

# =============================================================================
# STEP 1: EXTRACT TEXT FROM PDF
# =============================================================================
# What it does: Reads a PDF file and extracts all text into a .txt file

print("=" * 70)
print("STEP 1: EXTRACT TEXT FROM PDF")
print("=" * 70)

# Code:
"""
from langchain.document_loaders import UnstructuredPDFLoader

pdf_path = "documents/report.pdf"
loader = UnstructuredPDFLoader(pdf_path)
docs = loader.load()

# Save text to file
with open("documents/report.txt", "w") as f:
    for doc in docs:
        f.write(doc.page_content)

# INPUT:  documents/report.pdf (50 MB, 200 pages)
# OUTPUT: documents/report.txt (extracted text)
"""

print("\nStep 1 Example:")
print("  Input:  📄 report.pdf (200 pages, binary data)")
print("  Output: 📝 report.txt (1.5 MB text)")
print("  Uses:   LangChain UnstructuredPDFLoader")


# =============================================================================
# STEP 2: LOAD DOCUMENTS FROM DIRECTORY
# =============================================================================
# What it does: Loads all .txt and .pdf files from a folder

print("\n" + "=" * 70)
print("STEP 2: LOAD DOCUMENTS FROM DIRECTORY")
print("=" * 70)

# Code:
"""
from langchain.document_loaders import TextLoader
from langchain.schema import Document
import os

data_dir = "data"
all_docs = []

for filename in os.listdir(data_dir):
    if filename.endswith(".txt"):
        path = os.path.join(data_dir, filename)
        loader = TextLoader(path, encoding="utf-8")
        docs = loader.load()
        
        # Add metadata
        for doc in docs:
            doc.metadata["source"] = path
        
        all_docs.extend(docs)

print(f"Loaded {len(all_docs)} documents")
# INPUT:  Directory with .txt and .pdf files
# OUTPUT: List of LangChain Document objects
#         Each document has:
#         - page_content: the text
#         - metadata: {"source": "path/to/file"}
"""

print("\nStep 2 Example:")
print("  Input:  📁 data/ (contains: README.txt, guide.pdf, tutorial.txt)")
print("  Output: 3 Document objects")
print("          ┌─ Document 1: README.txt content")
print("          ├─ Document 2: guide.pdf content") 
print("          └─ Document 3: tutorial.txt content")
print("  Each has metadata with source file path")


# =============================================================================
# STEP 3: SPLIT TEXT INTO CHUNKS
# =============================================================================
# What it does: Breaks large documents into smaller pieces with overlap

print("\n" + "=" * 70)
print("STEP 3: SPLIT TEXT INTO CHUNKS")
print("=" * 70)

# Code:
"""
def split_text(text, chunk_size=3000, overlap=200):
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        
        # Move forward but keep overlap
        start = end - overlap
    
    return chunks

# Example:
long_text = "This is a very long document..." * 100  # 5000+ chars
chunks = split_text(long_text, chunk_size=3000, overlap=200)

# INPUT:  1 Large Document (5000 characters)
# OUTPUT: 2 Chunks:
#         - Chunk 1: chars 0-3000
#         - Chunk 2: chars 2800-5000 (200 char overlap)
"""

print("\nStep 3 Example:")
print("  Input:  1 Document (50,000 characters)")
print("  ")
print("  Original:     [========== LONG TEXT ==========]")
print("                 50,000 chars")
print("  ")
print("  Split:        [==== CHUNK 1 ====]  (chars 0-3000)")
print("                       └──── CHUNK 2 ====]  (chars 2800-5000, 200 overlap)")
print("                ")
print("  Output: ~17 chunks (3000 chars each with 200 char overlap)")


# =============================================================================
# STEP 4: CREATE EMBEDDINGS
# =============================================================================
# What it does: Converts text into vector numbers (embeddings)

print("\n" + "=" * 70)
print("STEP 4: CREATE EMBEDDINGS")
print("=" * 70)

# Code:
"""
from langchain.embeddings import HuggingFaceEmbeddings

# Initialize embedding model
embedder = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}
)

# Texts to embed
texts = [
    "Python is a programming language",
    "The cat is on the mat",
    "Machine learning is awesome"
]

# Create embeddings
embeddings = embedder.embed_documents(texts)

# INPUT:  List of 3 text strings
# OUTPUT: List of 3 embedding vectors (384 dimensions each)
#         embeddings[0] = [0.234, -0.123, 0.456, ..., 0.789]  (384 numbers)
#         embeddings[1] = [0.156, 0.234, -0.123, ..., 0.345]  (384 numbers)
#         embeddings[2] = [0.890, 0.123, 0.456, ..., -0.234] (384 numbers)
"""

print("\nStep 4 Example:")
print("  Input: 3 Text documents")
print("  ")
print("    Text 1: 'Python is a programming language'")
print("    Text 2: 'The cat is on the mat'")
print("    Text 3: 'Machine learning is awesome'")
print("  ")
print("  Embedding Process:")
print("    model: sentence-transformers/all-MiniLM-L6-v2")
print("    output dimension: 384 numbers per text")
print("  ")
print("  Output: Numpy array (3 x 384)")
print("    [[0.234, -0.123, 0.456, ..., 0.789],")
print("     [0.156,  0.234, -0.123, ..., 0.345],")
print("     [0.890,  0.123, 0.456, ..., -0.234]]")


# =============================================================================
# STEP 5: SAVE EMBEDDINGS TO FILES
# =============================================================================
# What it does: Saves embeddings and metadata to disk

print("\n" + "=" * 70)
print("STEP 5: SAVE EMBEDDINGS TO FILES")
print("=" * 70)

# Code:
"""
import numpy as np
import json

# Save embeddings as compressed numpy file
embeddings_array = np.array(embeddings)  # Shape: (1000, 384)
np.savez_compressed("embeddings.npz", embeddings=embeddings_array)

# Save metadata as JSONL (one JSON object per line)
with open("embeddings_meta.jsonl", "w") as f:
    for i, text in enumerate(texts):
        metadata = {
            "id": f"doc_{i}",
            "text_snippet": text[:300],
            "source": "documents/file.txt"
        }
        f.write(json.dumps(metadata) + "\\n")

# INPUT:  Embedding vectors + metadata
# OUTPUT: 2 Files:
#         - embeddings.npz (compressed binary, ~4 MB for 1000 docs)
#         - embeddings_meta.jsonl (human-readable metadata)
"""

print("\nStep 5 Example:")
print("  Creates 2 output files:")
print("  ")
print("  1️⃣ embeddings.npz (binary, compressed)")
print("     └─ Contains: embedding vectors (1000 x 384)")
print("        Size: ~1.5 MB (compressed)")
print("  ")
print("  2️⃣ embeddings_meta.jsonl (human readable)")
print("     Line 1: {\"id\": \"doc_0\", \"text_snippet\": \"...\", \"source\": \"...\"}")
print("     Line 2: {\"id\": \"doc_1\", \"text_snippet\": \"...\", \"source\": \"...\"}")
print("     Line 3: {\"id\": \"doc_2\", \"text_snippet\": \"...\", \"source\": \"...\"}")


# =============================================================================
# STEP 6: SAVE TO CHROMA DATABASE
# =============================================================================
# What it does: Stores documents with embeddings in a vector database

print("\n" + "=" * 70)
print("STEP 6: SAVE TO CHROMA DATABASE")
print("=" * 70)

# Code:
"""
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

# Initialize embedder
embedder = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Create Chroma database from documents
db = Chroma.from_documents(
    documents=docs,  # LangChain Document objects
    embedding=embedder,
    persist_directory="./chroma_db",
    collection_name="documents"
)

# Persist to disk
db.persist()

# Now you can search:
query = "Python programming"
results = db.similarity_search(query, k=3)
# Returns top 3 most similar documents

# INPUT:  List of LangChain Documents
# OUTPUT: Chroma database directory (./chroma_db)
#         Ready for similarity search queries
"""

print("\nStep 6 Example:")
print("  Input: 1000 document chunks")
print("  ")
print("  Process:")
print("    1. Create embeddings for all documents")
print("    2. Store in Chroma vector database")
print("    3. Build indexes for fast search")
print("  ")
print("  Output: Directory structure")
print("    ./chroma_db/")
print("    ├── index/                              (search indexes)")
print("    ├── chroma-collections.parquet          (metadata)")
print("    └── chroma-embeddings.parquet           (embeddings)")
print("  ")
print("  Ready for queries:")
print("    query = 'What is machine learning?'")
print("    results = db.similarity_search(query, k=5)")
print("    # Returns 5 most relevant documents")


# =============================================================================
# COMPLETE PIPELINE COMPARISON
# =============================================================================

print("\n" + "=" * 70)
print("COMPARISON: STEP 5 vs STEP 6")
print("=" * 70)

comparison_table = """
┌─────────────────────┬────────────────────────┬──────────────────────────┐
│ Feature             │ STEP 5: Files          │ STEP 6: Chroma DB        │
├─────────────────────┼────────────────────────┼──────────────────────────┤
│ Output Format       │ .npz + .jsonl          │ Database directory       │
│ File Size           │ Smaller (~1.5MB)       │ Larger (~3MB)            │
│ Search Speed        │ Manual numpy search    │ Built-in similarity      │
│ Setup Complexity    │ Simple                 │ Simple                   │
│ Production Ready    │ No (manual work)       │ Yes (built-in)           │
│ Metadata Handling   │ JSON lines per doc     │ Structured metadata      │
│ Scaling             │ Okay for small sets    │ Good for larger sets     │
│ Use Case            │ Research/prototyping   │ Production apps          │
└─────────────────────┴────────────────────────┴──────────────────────────┘
"""

print(comparison_table)


# =============================================================================
# COMPLETE WORKFLOW TIMELINE
# =============================================================================

print("\n" + "=" * 70)
print("COMPLETE WORKFLOW TIMELINE")
print("=" * 70)

timeline = """
START
  ↓
[1. Extract PDF] ─────────→ report.pdf (200 pages) → report.txt
  ↓
[2. Load Documents] ──────→ report.txt, guide.txt, manual.txt
  ↓                         ↓
  ├─────────────────────[3 Documents loaded]
  ↓
[3. Split into Chunks] ───→ 1000 chunks (3000 chars each, 200 overlap)
  ↓
[4. Create Embeddings] ───→ 1000 embeddings (384 dimensions each)
  ↓
  ├─→ [5. SAVE TO FILES]
  │   ├─ embeddings.npz (1.5 MB)
  │   └─ embeddings_meta.jsonl (2 MB)
  │
  └─→ [6. SAVE TO CHROMA]
      └─ ./chroma_db/ (ready for queries)
        ↓
    READY FOR SIMILARITY SEARCH
    
Example query:
  "What is Python?" 
  → Converts to embedding
  → Searches similar embeddings in DB
  → Returns top-k most relevant documents
  
END
"""

print(timeline)


print("\n" + "=" * 70)
print("KEY PARAMETERS TO ADJUST")
print("=" * 70)

params_guide = """
PARAMETER               DEFAULT    RANGE         DESCRIPTION
──────────────────────────────────────────────────────────────────
chunk_size              3000       1000-5000     How many characters per chunk
overlap                 200        0-1000        Overlap between chunks
embedding_model         MiniLM     varies        Which model to use for embeddings
embedding_device        cpu        cpu/cuda      Run embeddings on CPU or GPU
chroma_directory        chroma_db  any path      Where to save Chroma database
persist_directory       ./         any path      Where to save files
batch_size              32         1-128         Process embeddings in batches

ADJUSTMENTS FOR DIFFERENT USE CASES:
────────────────────────────────────

Speed Priority (Fast embedding):
  - chunk_size: 1000
  - overlap: 0
  - embedding_model: MiniLM (most lightweight)

Quality Priority (Better accuracy):
  - chunk_size: 4000
  - overlap: 500
  - embedding_model: large-L12-v2 or better

Memory Limited:
  - chunk_size: 500
  - embedding_device: cpu
  - batch_size: 8

GPU Available (Much faster):
  - embedding_device: cuda
  - batch_size: 128
"""

print(params_guide)


print("\n" + "=" * 70)
print("FINAL SUMMARY")
print("=" * 70)

summary = """
6-STEP JOURNEY: PDF → EMBEDDINGS

Step 1: 📄 PDF Extraction
        Convert binary PDF into readable text
        
Step 2: 📁 Document Loading
        Load all text from multiple files
        
Step 3: ✂️ Text Chunking
        Split large texts into manageable pieces
        with overlapping context
        
Step 4: 🧠 Embedding Creation
        Convert text chunks into vector numbers
        (384-dimensional vectors)
        
Step 5: 💾 File Storage
        Save embeddings as binary files
        (good for research)
        
Step 6: 🗄️ Database Storage
        Save embeddings in vector database
        (good for production)

NEXT STEPS: Use the embeddings for:
  → Semantic similarity search
  → Recommendation systems
  → Question-answering systems
  → Document clustering
  → Anomaly detection
"""

print(summary)
