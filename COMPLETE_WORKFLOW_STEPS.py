"""
COMPLETE WORKFLOW: PDF to Embeddings Pipeline
step-by-step guide for the entire process
=====================================================
"""

# ============================================================================
# STEP 1: EXTRACT TEXT FROM PDF FILES
# ============================================================================
"""
This step reads PDF files and extracts text content
Output: .txt files containing extracted text
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def step_1_extract_pdf(pdf_path: str) -> str:
    """Extract text from PDF file"""
    
    # Try LangChain UnstructuredPDFLoader first
    try:
        from langchain.document_loaders import UnstructuredPDFLoader
        loader = UnstructuredPDFLoader(pdf_path)
        docs = loader.load()
        texts = [getattr(d, "page_content", "") for d in docs]
        return "\n\n".join(t for t in texts if t)
    except Exception:
        pass
    
    # Fallback: Use unstructured library directly
    try:
        from unstructured.partition.pdf import partition_pdf
        elements = partition_pdf(filename=pdf_path)
        texts = []
        for el in elements:
            txt = getattr(el, "get_text", lambda: None)()
            if not txt:
                txt = str(el)
            if txt:
                texts.append(txt)
        return "\n\n".join(texts)
    except Exception as e:
        print(f"ERROR extracting {pdf_path}: {e}")
        raise

def step_1_main(pdf_path: str) -> None:
    """Main function for Step 1"""
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return
    
    print(f"[STEP 1] Extracting text from: {pdf_path}")
    text = step_1_extract_pdf(pdf_path)
    
    # Save output next to PDF
    out_path = os.path.splitext(pdf_path)[0] + ".txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    
    print(f"✓ Extracted text saved to: {out_path}")
    print(f"  Characters: {len(text)}")
    print(f"  Preview: {text[:200]}...")


# ============================================================================
# STEP 2: LOAD TEXT FILES FROM DIRECTORY
# ============================================================================
"""
This step loads all .txt and .pdf files from a directory
Output: LangChain Document objects with content and metadata
"""

from langchain.document_loaders import TextLoader, UnstructuredPDFLoader
from langchain.schema import Document
from typing import List

def step_2_load_txt(path: str) -> List[Document]:
    """Load a .txt file"""
    loader = TextLoader(path, encoding="utf-8")
    docs = loader.load()
    for d in docs:
        d.metadata.setdefault("source", path)
    return docs

def step_2_load_pdf(path: str) -> List[Document]:
    """Load a .pdf file"""
    try:
        loader = UnstructuredPDFLoader(path)
        docs = loader.load()
        for d in docs:
            d.metadata.setdefault("source", path)
        return docs
    except Exception:
        from unstructured.partition.pdf import partition_pdf
        elems = partition_pdf(filename=path)
        texts = []
        for el in elems:
            txt = getattr(el, "get_text", lambda: None)()
            if not txt:
                txt = str(el)
            if txt:
                texts.append(Document(page_content=txt, metadata={"source": path}))
        return texts

def step_2_load_file(path: str) -> List[Document]:
    """Load a single file (txt or pdf)"""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".txt":
        return step_2_load_txt(path)
    elif ext == ".pdf":
        return step_2_load_pdf(path)
    return []

def step_2_load_directory(directory: str) -> List[Document]:
    """Load all supported files from directory"""
    all_docs = []
    for root, _, files in os.walk(directory):
        for name in sorted(files):
            path = os.path.join(root, name)
            docs = step_2_load_file(path)
            if docs:
                print(f"  ✓ Loaded {len(docs)} doc(s) from {path}")
                all_docs.extend(docs)
    return all_docs

def step_2_main(directory: str = "data") -> List[Document]:
    """Main function for Step 2"""
    print(f"\n[STEP 2] Loading documents from directory: {directory}")
    if not os.path.isdir(directory):
        print(f"ERROR: Directory not found: {directory}")
        return []
    
    docs = step_2_load_directory(directory)
    print(f"✓ Total documents loaded: {len(docs)}")
    
    for i, d in enumerate(docs[:3], start=1):
        src = d.metadata.get("source", "<unknown>")
        content_preview = d.page_content[:100].replace("\n", " ")
        print(f"  Doc {i} ({src}): {content_preview}...")
    
    return docs


# ============================================================================
# STEP 3: SPLIT TEXT INTO CHUNKS
# ============================================================================
"""
This step splits long documents into smaller chunks with overlap
Output: List of document chunks
Purpose: Embeddings work better with reasonably sized chunks
"""

from typing import List as ListType

def step_3_split_text(text: str, chunk_size: int = 3000, overlap: int = 200) -> ListType[str]:
    """Split text into overlapping chunks"""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0:
        raise ValueError("overlap must be >= 0")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")
    
    chunks = []
    start = 0
    n = len(text)
    
    while start < n:
        end = start + chunk_size
        chunks.append(text[start:end])
        if end >= n:
            break
        # Move start forward but keep overlap
        start = end - overlap
    
    return chunks

def step_3_chunk_documents(docs: List[Document], chunk_size: int = 3000, overlap: int = 200) -> List[Document]:
    """Split all documents into chunks"""
    chunked_docs = []
    chunk_id = 0
    
    for doc in docs:
        text = doc.page_content
        metadata = doc.metadata.copy() if doc.metadata else {}
        
        chunks = step_3_split_text(text, chunk_size=chunk_size, overlap=overlap)
        
        for i, chunk in enumerate(chunks):
            chunk_id += 1
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_id"] = i
            chunk_metadata["chunk_total"] = len(chunks)
            
            chunked_doc = Document(page_content=chunk, metadata=chunk_metadata)
            chunked_docs.append(chunked_doc)
    
    return chunked_docs

def step_3_main(docs: List[Document], chunk_size: int = 3000, overlap: int = 200) -> List[Document]:
    """Main function for Step 3"""
    print(f"\n[STEP 3] Splitting documents into chunks")
    print(f"  Chunk size: {chunk_size} characters")
    print(f"  Overlap: {overlap} characters")
    
    chunked_docs = step_3_chunk_documents(docs, chunk_size=chunk_size, overlap=overlap)
    
    print(f"✓ Total chunks created: {len(chunked_docs)}")
    for i, doc in enumerate(chunked_docs[:3], start=1):
        print(f"  Chunk {i}: {len(doc.page_content)} chars - {doc.page_content[:80]}...")
    
    return chunked_docs


# ============================================================================
# STEP 4: CREATE EMBEDDINGS
# ============================================================================
"""
This step converts text into vector embeddings using sentence-transformers
Output: Numpy arrays with embedding vectors
Purpose: Enable semantic similarity search
"""

from langchain.embeddings import HuggingFaceEmbeddings
import numpy as np

def step_4_create_embeddings(texts: ListType[str], model_name: str = "sentence-transformers/all-MiniLM-L6-v2", device: str = "cpu") -> ListType:
    """Create embeddings for list of texts"""
    print(f"  Loading model: {model_name}")
    
    emb = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": device}
    )
    
    print(f"  Computing embeddings for {len(texts)} texts...")
    embeddings = emb.embed_documents(texts)
    
    return embeddings

def step_4_main(docs: List[Document], model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> tuple:
    """Main function for Step 4"""
    print(f"\n[STEP 4] Creating embeddings")
    
    texts = [doc.page_content for doc in docs]
    embeddings = step_4_create_embeddings(texts, model_name=model_name)
    
    # Convert to numpy array
    embeddings_array = np.array(embeddings)
    
    print(f"✓ Embeddings created!")
    print(f"  Shape: {embeddings_array.shape}")
    print(f"  Embedding dimension: {embeddings_array.shape[1]}")
    
    return embeddings_array, docs


# ============================================================================
# STEP 5: SAVE EMBEDDINGS TO FILES
# ============================================================================
"""
This step saves embeddings and metadata for later use
Output: .npz file (embeddings) + .jsonl file (metadata)
Purpose: Persistent storage for semantic search
"""

import json

def step_5_save_embeddings_npz(out_prefix: str, embeddings: np.ndarray, ids: ListType[str]) -> str:
    """Save embeddings as compressed numpy file"""
    out_path = out_prefix + ".npz"
    np.savez_compressed(out_path, embeddings=embeddings, ids=np.array(ids, dtype=object))
    return out_path

def step_5_save_metadata_jsonl(out_prefix: str, ids: ListType[str], metadatas: ListType[dict], texts: ListType[str]) -> str:
    """Save metadata as JSONL file"""
    out_meta = out_prefix + "_meta.jsonl"
    with open(out_meta, "w", encoding="utf-8") as fh:
        for i, md, txt in zip(ids, metadatas, texts):
            item = {
                "id": i,
                "metadata": md or {},
                "text_snippet": txt[:300]
            }
            fh.write(json.dumps(item, ensure_ascii=False) + "\n")
    return out_meta

def step_5_main(embeddings_array: np.ndarray, docs: List[Document], out_prefix: str = "embeddings/data_embeddings") -> None:
    """Main function for Step 5"""
    print(f"\n[STEP 5] Saving embeddings to files")
    
    # Prepare IDs and metadata
    ids = [md.get("source", f"doc_{i}") for i, md in enumerate([d.metadata for d in docs])]
    metadatas = [d.metadata for d in docs]
    texts = [d.page_content for d in docs]
    
    # Create output directory
    os.makedirs(os.path.dirname(out_prefix) or ".", exist_ok=True)
    
    # Save files
    out_npz = step_5_save_embeddings_npz(out_prefix, embeddings_array, ids)
    out_meta = step_5_save_metadata_jsonl(out_prefix, ids, metadatas, texts)
    
    print(f"✓ Embeddings saved!")
    print(f"  Embeddings file: {out_npz}")
    print(f"  Metadata file: {out_meta}")


# ============================================================================
# STEP 6: SAVE TO CHROMA DB (ALTERNATIVE TO STEP 5)
# ============================================================================
"""
This step persists documents with embeddings to Chroma Vector Database
Output: Chroma database on disk
Purpose: Ready-to-use vector database for semantic search
"""

from langchain.vectorstores import Chroma

def step_6_sanitize_metadata(md: dict) -> dict:
    """Sanitize metadata for Chroma indexing"""
    allowed = (str, int, float, bool, type(None))
    out = {}
    for k, v in (md or {}).items():
        if isinstance(v, allowed):
            out[k] = v
        else:
            try:
                s = json.dumps(v, default=str)
            except Exception:
                s = str(v)
            # Truncate overly large metadata strings
            if len(s) > 1000:
                s = s[:1000] + "..."
            out[k] = s
    return out

def step_6_persist_to_chroma(docs: List[Document], persist_dir: str = "./chroma_db", collection_name: str = "documents", model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
    """Persist documents to Chroma database"""
    
    # Sanitize metadata
    for d in docs:
        if hasattr(d, "metadata") and isinstance(d.metadata, dict):
            d.metadata = step_6_sanitize_metadata(d.metadata)
    
    # Create embedding function
    emb = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cpu"}
    )
    
    # Create and persist Chroma database
    db = Chroma.from_documents(
        documents=docs,
        embedding=emb,
        persist_directory=persist_dir,
        collection_name=collection_name
    )
    
    try:
        db.persist()
    except Exception:
        pass
    
    return db

def step_6_main(docs: List[Document], persist_dir: str = "./chroma_db", collection_name: str = "documents") -> None:
    """Main function for Step 6"""
    print(f"\n[STEP 6] Persisting to Chroma Vector Database")
    print(f"  Persist directory: {persist_dir}")
    print(f"  Collection name: {collection_name}")
    
    db = step_6_persist_to_chroma(docs, persist_dir=persist_dir, collection_name=collection_name)
    
    print(f"✓ Documents persisted to Chroma!")
    print(f"  Total documents: {len(docs)}")


# ============================================================================
# COMPLETE PIPELINE - RUN ALL STEPS
# ============================================================================

def run_complete_pipeline(
    pdf_path: str = None,
    data_dir: str = "data",
    chunk_size: int = 3000,
    overlap: int = 200,
    output_prefix: str = "embeddings/data_embeddings",
    use_chroma: bool = True,
    chroma_dir: str = "./chroma_db"
) -> None:
    """
    Run the complete pipeline from PDF to embeddings
    
    Args:
        pdf_path: Path to single PDF to extract (optional)
        data_dir: Directory containing documents to process
        chunk_size: Character size for text chunks
        overlap: Overlap between chunks
        output_prefix: Output file prefix for embeddings
        use_chroma: Whether to save to Chroma DB
        chroma_dir: Chroma database directory
    """
    
    print("=" * 70)
    print("STARTING COMPLETE PDF-TO-EMBEDDINGS PIPELINE")
    print("=" * 70)
    
    # STEP 1: Extract PDF if provided
    if pdf_path and os.path.exists(pdf_path):
        step_1_main(pdf_path)
    
    # STEP 2: Load documents from directory
    docs = step_2_main(data_dir)
    if not docs:
        print("ERROR: No documents found!")
        return
    
    # STEP 3: Split into chunks
    chunked_docs = step_3_main(docs, chunk_size=chunk_size, overlap=overlap)
    
    # STEP 4: Create embeddings
    embeddings_array, chunked_docs = step_4_main(chunked_docs)
    
    # STEP 5 & 6: Save to files OR Chroma DB
    if use_chroma:
        step_6_main(chunked_docs, persist_dir=chroma_dir)
    else:
        step_5_main(embeddings_array, chunked_docs, out_prefix=output_prefix)
    
    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE!")
    print("=" * 70)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example 1: Run complete pipeline with Chroma
    run_complete_pipeline(
        data_dir="data",
        use_chroma=True,
        chroma_dir="./chroma_db"
    )
    
    # Example 2: Extract single PDF then process
    # run_complete_pipeline(
    #     pdf_path="path/to/document.pdf",
    #     data_dir="data",
    #     use_chroma=False,
    #     output_prefix="embeddings/my_embeddings"
    # )
