#!/usr/bin/env python3
"""
Load all supported files from a directory (`data/` by default), optionally
clear the Chroma DB, and persist loaded documents to Chroma.

Usage:
  python scripts/load_directory.py --dir data --persist --clear-db
"""
from __future__ import annotations

import argparse
import os
import shutil
from dotenv import load_dotenv

load_dotenv()


def load_txt(path: str):
    from langchain.document_loaders import TextLoader

    loader = TextLoader(path, encoding="utf-8")
    docs = loader.load()
    for d in docs:
        d.metadata.setdefault("source", path)
    return docs


def load_pdf(path: str):
    # Prefer LangChain's UnstructuredPDFLoader, fall back to unstructured.partition_pdf
    try:
        from langchain.document_loaders import UnstructuredPDFLoader

        loader = UnstructuredPDFLoader(path)
        docs = loader.load()
        for d in docs:
            d.metadata.setdefault("source", path)
        return docs
    except Exception:
        from unstructured.partition.pdf import partition_pdf
        from langchain.schema import Document

        elems = partition_pdf(filename=path)
        texts: list[Document] = []
        for el in elems:
            txt = getattr(el, "get_text", lambda: None)()
            if not txt:
                txt = str(el)
            if txt:
                texts.append(Document(page_content=txt, metadata={"source": path}))
        return texts


def load_file(path: str):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".txt":
        return load_txt(path)
    if ext == ".pdf":
        return load_pdf(path)
    # skip unsupported files but return empty
    return []


def load_directory(directory: str):
    all_docs = []
    for root, _, files in os.walk(directory):
        for name in sorted(files):
            path = os.path.join(root, name)
            docs = load_file(path)
            if docs:
                print(f"Loaded {len(docs)} doc(s) from {path}")
                all_docs.extend(docs)
            else:
                print(f"Skipping {path} (unsupported or empty)")
    return all_docs


def persist_to_chroma(docs, persist_dir: str = "./chroma_db", collection_name: str = "documents"):
    # clear directory if present
    if os.path.exists(persist_dir):
        print(f"Persist directory {persist_dir} exists. Use --clear-db to remove it before persisting.")

    # sanitize metadata: remove or stringify complex values to avoid indexing errors
    import json

    def sanitize_metadata(md: dict) -> dict:
        allowed = (str, int, float, bool, type(None))
        out: dict = {}
        for k, v in (md or {}).items():
            if isinstance(v, allowed):
                out[k] = v
            else:
                try:
                    s = json.dumps(v, default=str)
                except Exception:
                    s = str(v)
                # truncate overly large metadata strings
                if len(s) > 1000:
                    s = s[:1000] + "..."
                out[k] = s
        return out

    # Apply sanitization in-place on LangChain Document metadata
    for d in docs:
        try:
            if hasattr(d, "metadata") and isinstance(d.metadata, dict):
                d.metadata = sanitize_metadata(d.metadata)
        except Exception:
            # non-fatal: continue with other documents
            continue

    from langchain.vectorstores import Chroma
    from langchain.embeddings import HuggingFaceEmbeddings

    # Use the sentence-transformers MiniLM model on CPU
    model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    # force CPU to avoid GPU device selection; model_kwargs forwarded to transformers/sentence-transformers
    emb = HuggingFaceEmbeddings(model_name=model_name, model_kwargs={"device": "cpu"})

    db = Chroma.from_documents(documents=docs, embedding=emb, persist_directory=persist_dir, collection_name=collection_name)
    try:
        db.persist()
    except Exception:
        pass
    print(f"Persisted {len(docs)} documents to Chroma at {persist_dir} (collection={collection_name}).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="data", help="Directory to load files from")
    ap.add_argument("--persist", action="store_true", help="Persist documents to Chroma")
    ap.add_argument("--persist-dir", default="./chroma_db", help="Chroma persist directory")
    ap.add_argument("--collection", default="documents", help="Chroma collection name")
    ap.add_argument("--clear-db", action="store_true", help="Remove Chroma persist directory before persisting")
    args = ap.parse_args()

    if not os.path.isdir(args.dir):
        print(f"Directory not found: {args.dir}")
        raise SystemExit(1)

    if args.clear_db and os.path.exists(args.persist_dir):
        print(f"Removing existing persist directory: {args.persist_dir}")
        shutil.rmtree(args.persist_dir)

    docs = load_directory(args.dir)
    print(f"Total documents loaded: {len(docs)}")

    if args.persist and docs:
        persist_to_chroma(docs, persist_dir=args.persist_dir, collection_name=args.collection)


if __name__ == "__main__":
    main()
