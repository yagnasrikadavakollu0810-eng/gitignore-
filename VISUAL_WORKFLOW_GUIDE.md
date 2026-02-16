# VISUAL WORKFLOW GUIDE: From PDFs to Embeddings

## Overview

```
Input Documents              Processing Pipeline                   Output
─────────────────            ──────────────────────                ──────

📄 PDF Files    ──[1]─→  Extract Text  ──→  📝 Text Files
📝 Text Files   ──[2]─→  Load Documents ──→  📚 LangChain Docs
                        (with metadata)
                ──[3]─→  Split Chunks  ──→  ✂️ 1000+ Chunks
                        (3000 chars each)
                ──[4]─→  Embeddings    ──→  🧠 Vector Array
                        (ML Model)          (1000 x 384)
                        
                ┌───────────────────────────────────────┐
                │                                       │
                ├─[5]─→ Save to Files  ──→  📦 .npz + .jsonl
                │                              (binary + text)
                │
                └─[6]─→ Save to Chroma ──→  🗄️ Vector DB
                                              (ready to query)
```

---

## ⭐ Step-by-Step Breakdown

### **STEP 1️⃣: Extract Text from PDF**

```
Input:  [document.pdf]  (50 MB, binary data)
        ├─ Page 1 (image + text)
        ├─ Page 2 (image + text)
        └─ Page 3 (image + text)

Process: Use LangChain's UnstructuredPDFLoader
         → Extract all text content
         → Remove formatting/images
         → Combine into single text

Output: [document.txt]  (2 MB, plain text)
        "Chapter 1: Introduction...
         Chapter 2: Methods...
         Chapter 3: Results..."

Code:
  from langchain.document_loaders import UnstructuredPDFLoader
  loader = UnstructuredPDFLoader("document.pdf")
  docs = loader.load()
```

---

### **STEP 2️⃣: Load Documents from Directory**

```
Input:  Directory Structure
        data/
        ├─ README.txt (10 KB)
        ├─ guide.pdf (15 MB)
        ├─ tutorial.txt (25 KB)
        └─ manual.pdf (5 MB)

Process: Walk through directory
         → Identify supported files (.txt, .pdf)
         → Load each file
         → Create metadata (source path, etc.)

Output: List of 4 Documents
        ┌─ Document 1
        │  ├─ content: "README text content..."
        │  └─ metadata: {"source": "data/README.txt"}
        │
        ├─ Document 2
        │  ├─ content: "guide content..."
        │  └─ metadata: {"source": "data/guide.pdf"}
        │
        └─ ... (3 more documents)

Code:
  from langchain.document_loaders import TextLoader
  docs = []
  for file in os.listdir("data"):
      if file.endswith(".txt"):
          loader = TextLoader(file)
          docs.extend(loader.load())
```

---

### **STEP 3️⃣: Split Text into Chunks**

```
Problem: Long documents (50,000+ chars) are too big for embeddings

Solution: Split into smaller, overlapping chunks

Example:

Original Document (50,000 chars)
┌─────────────────────────────────────────────┐
│ Introduction... Methods... Results...  │
│ Discussion... References... Appendix... │
│ (50,000 characters)                     │
└─────────────────────────────────────────────┘

Split with chunk_size=3000, overlap=200:

Chunk 1 (chars 0-3000)
┌──────────────┐
│ Introduction...
│ Methods...
│ (3000 chars)
└──────────────┘

Chunk 2 (chars 2800-5800)  ← 200 char overlap with Chunk 1
┌──────────────┐
│ ethods...
│ Results...
│ (3000 chars)
└──────────────┘

Chunk 3 (chars 5600-8600)  ← 200 char overlap with Chunk 2
┌──────────────┐
│ Discussion...
│ References...
│ (3000 chars)
└──────────────┘

... (continue until end of document)

Output: ~17 chunks from 1 document

Code:
  def split_text(text, chunk_size=3000, overlap=200):
      chunks = []
      start = 0
      while start < len(text):
          chunks.append(text[start:start+chunk_size])
          start += (chunk_size - overlap)
      return chunks
```

---

### **STEP 4️⃣: Create Embeddings**

```
What are embeddings?
→ Numerical representations of text
→ Similar texts → Similar vectors
→ Enable semantic search

Process:

Text Input:
  ["Python is a programming language",
   "Java is also a programming language",
   "The cat sat on the mat"]

Embedding Model (all-MiniLM-L6-v2):
  Downloads pre-trained neural network
  Processes each text
  Outputs 384 numbers per text

Output: Vectors in 384-dimensional space
  
  Python text:     [0.234, -0.123, 0.456, ..., 0.789]     (384 dims)
                    ↑ related to programming concepts
  
  Java text:       [0.245, -0.115, 0.462, ..., 0.792]     (384 dims)
                    ↑ very similar (both programming languages)
  
  Cat text:        [0.890, 0.234, -0.123, ..., 0.345]     (384 dims)
                    ↑ very different (about animals, not programming)

Similarity Measure (cosine similarity):
  similarity(Python, Java) = 0.95  (very similar)
  similarity(Python, Cat) = 0.12   (not similar)

Code:
  from langchain.embeddings import HuggingFaceEmbeddings
  
  embedder = HuggingFaceEmbeddings(
      model_name="sentence-transformers/all-MiniLM-L6-v2"
  )
  
  embeddings = embedder.embed_documents(texts)
  # Output: List of 384-dimensional vectors
```

---

### **STEP 5️⃣: Save Embeddings to Files**

```
Save embeddings and metadata for later use

Output Files:

1️⃣ embeddings.npz (Binary Format)
   ├─ File size: ~1.5 MB (for 1000 documents)
   ├─ Format: NumPy compressed array
   ├─ Content: 
   │   ├─ embeddings: (1000, 384) array
   │   └─ ids: document identifiers
   └─ Usage: numpy.load("embeddings.npz")

2️⃣ embeddings_meta.jsonl (Text Format)
   Line 1: {"id": "doc_0", "text_snippet": "Python is...", "source": "data/1.txt"}
   Line 2: {"id": "doc_1", "text_snippet": "Java is...", "source": "data/2.txt"}
   Line 3: {"id": "doc_2", "text_snippet": "The cat...", "source": "data/3.txt"}
   ...
   (one JSON object per line)

Structure:
  embeddings/
  ├─ data_embeddings.npz           (binary, small)
  └─ data_embeddings_meta.jsonl    (human-readable)

Code:
  import numpy as np
  import json
  
  # Save embeddings
  np.savez_compressed("embeddings.npz", 
                      embeddings=embedding_array)
  
  # Save metadata
  with open("embeddings_meta.jsonl", "w") as f:
      for id, snippet, source in data:
          f.write(json.dumps({
              "id": id,
              "text_snippet": snippet,
              "source": source
          }) + "\n")
```

---

### **STEP 6️⃣: Save to Chroma Database**

```
Production-ready vector database

Process:

1. Create Chroma database
   └─ Initialize vector store

2. Add all documents with embeddings
   └─ Chroma computes embeddings automatically
   └─ Indexes them for fast search

3. Persist to disk
   └─ Create directory: ./chroma_db/

Database Directory Structure:
  ./chroma_db/
  ├─ index/                           (search indexes)
  │  ├─ index.pkl                     (pickle file)
  │  └─ uuid_to_data_uuid.pkl
  ├─ chroma-collections.parquet       (collection metadata)
  ├─ chroma-embeddings.parquet        (embedding vectors)
  └─ .parquet files                   (data storage)

Ready-to-Use Features:
  ✓ Automatic embeddings
  ✓ Fast similarity search
  ✓ Metadata filtering
  ✓ Persistent storage

Code:
  from langchain.vectorstores import Chroma
  from langchain.embeddings import HuggingFaceEmbeddings
  
  embedder = HuggingFaceEmbeddings()
  
  db = Chroma.from_documents(
      documents=docs,
      embedding=embedder,
      persist_directory="./chroma_db"
  )
  
  db.persist()
  
  # Query:
  results = db.similarity_search("Python programming", k=3)
```

---

## 📊 Data Flow Summary

```
Stage 1: Raw Input
  PDF/Text Files → 100 MB total

Stage 2: After Loading
  LangChain Documents → 4 documents with metadata

Stage 3: After Chunking
  Chunks → 1000 chunks (3000 chars each)

Stage 4: After Embeddings
  Vectors → 1000 × 384 dimensional vectors

Stage 5a: Save to Files
  • embeddings.npz: 1.5 MB (compressed)
  • embeddings_meta.jsonl: 2 MB

Stage 5b: Save to Chroma
  • chroma_db folder: 3-5 MB total
  • Ready for production queries
```

---

## 🚀 Quick Execution Guide

### Option A: Complete Pipeline (Recommended)
```python
from COMPLETE_WORKFLOW_STEPS import run_complete_pipeline

run_complete_pipeline(
    data_dir="data",
    use_chroma=True,  # Use Chroma DB
    chroma_dir="./chroma_db"
)
```

### Option B: Step by Step
```python
from COMPLETE_WORKFLOW_STEPS import *

# 1. Extract PDF
step_1_main("documents/report.pdf")

# 2. Load documents
docs = step_2_main("data")

# 3. Split into chunks
chunks = step_3_main(docs, chunk_size=3000)

# 4. Create embeddings
embeddings, chunks = step_4_main(chunks)

# 5. Save (choose one):
# Option A: Files
step_5_main(embeddings, chunks)

# Option B: Chroma DB
step_6_main(chunks, persist_dir="./chroma_db")
```

### Option C: Use Existing Chroma DB
```python
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

embedder = HuggingFaceEmbeddings()

# Load existing database
db = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embedder
)

# Query
results = db.similarity_search("What is Python?", k=5)

for result in results:
    print(f"Score: {result.metadata.get('source', 'N/A')}")
    print(f"Content: {result.page_content[:200]}...")
```

---

## ⚙️ Key Parameters

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `chunk_size` | 3000 | Characters per chunk |
| `overlap` | 200 | Overlap between chunks |
| `embedding_model` | all-MiniLM-L6-v2 | Model for embeddings |
| `device` | cpu | CPU or GPU |
| `k` (in search) | 5 | Number of results to return |

---

## 📈 Performance Expectations

| Task | Time | Memory | Output Size |
|------|------|--------|-------------|
| Extract 100-page PDF | 5-10 sec | 100 MB | 5-10 MB |
| Load 10 documents | < 1 sec | 50 MB | - |
| Split to chunks | 1 sec | 100 MB | - |
| Embed 1000 chunks | 30-60 sec | 500 MB | 1-2 MB |
| Save to Chroma | 5 sec | 100 MB | 3-5 MB |
| Single query | 0.1 sec | 50 MB | - |

---

## 🔧 Troubleshooting

### Issue: "Module not found"
```bash
pip install -r requirements.txt
```

### Issue: Out of memory
```python
# Reduce chunk size
run_complete_pipeline(chunk_size=1000)

# Or use GPU
step_4_main(docs, device="cuda")
```

### Issue: Slow embeddings
```python
# Use device="cuda" for GPU
# Or use faster model:
# "sentence-transformers/all-MiniLM-L6-v2" (fast, default)
# "sentence-transformers/paraphrase-MiniLM-L6-v2" (faster)
```

---

## ✅ Verification Checklist

- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] Data directory exists: `data/` with test files
- [ ] Output directories created: `embeddings/`, `chroma_db/`
- [ ] First run completes without errors
- [ ] Output files created:
  - [ ] embeddings.npz (or chroma_db directory)
  - [ ] embeddings_meta.jsonl (if using files)
- [ ] Can query results successfully
- [ ] Results make semantic sense

---

**Your workflow is now ready to process PDFs and create embeddings! Start with the Complete Pipeline option for best results.**
