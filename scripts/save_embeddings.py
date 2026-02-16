#!/usr/bin/env python3
"""
Compute embeddings for documents in a directory and save locally.

Saves:
 - compressed NumPy file with embeddings: `<out>.npz` (array under key `embeddings`)
 - JSONL metadata file: `<out>_meta.jsonl` (one JSON object per line: {"id":..., "metadata":..., "text_snippet":...})

Usage:
  python scripts/save_embeddings.py --dir data --out embeddings/data_embeddings
"""
from __future__ import annotations

import os
import sys
import json
import argparse
from typing import List

def ensure_path_in_syspath():
    root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    if root not in sys.path:
        sys.path.insert(0, root)

ensure_path_in_syspath()


def load_documents_from_dir(directory: str):
    # reuse loader from scripts/load_directory.py if available
    try:
        from scripts.load_directory import load_directory
        docs = load_directory(directory)
        return docs
    except Exception:
        # fallback: load only .txt files
        from glob import glob
        from langchain.schema import Document

        files = sorted(glob(os.path.join(directory, "**", "*.txt"), recursive=True))
        docs: List[Document] = []
        for f in files:
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    txt = fh.read()
                docs.append(Document(page_content=txt, metadata={"source": f}))
            except Exception:
                continue
        return docs


def compute_embeddings(texts: List[str], model_name: str, device: str = "cpu"):
    try:
        from langchain.embeddings import HuggingFaceEmbeddings
    except Exception as exc:
        raise RuntimeError("langchain is required: pip install langchain") from exc

    emb = HuggingFaceEmbeddings(model_name=model_name, model_kwargs={"device": device})
    return emb.embed_documents(texts)


def save_embeddings_npz(out_prefix: str, embeddings, ids: List[str]):
    import numpy as np

    out_path = out_prefix + ".npz"
    np.savez_compressed(out_path, embeddings=embeddings, ids=np.array(ids, dtype=object))
    return out_path


def save_metadata_jsonl(out_prefix: str, ids: List[str], metadatas: List[dict], texts: List[str]):
    out_meta = out_prefix + "_meta.jsonl"
    with open(out_meta, "w", encoding="utf-8") as fh:
        for i, md, txt in zip(ids, metadatas, texts):
            item = {"id": i, "metadata": md or {}, "text_snippet": txt[:300]}
            fh.write(json.dumps(item, ensure_ascii=False) + "\n")
    return out_meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="data", help="Directory containing documents")
    ap.add_argument("--out", default="embeddings/data_embeddings", help="Output prefix (no extension)")
    ap.add_argument("--model", default=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"), help="Embedding model name")
    ap.add_argument("--device", default=os.getenv("EMBEDDING_DEVICE", "cpu"), help="Device to run embeddings on (cpu)")
    ap.add_argument("--to-chroma", action="store_true", help="Persist documents and embeddings directly to Chroma instead of saving local files")
    ap.add_argument("--persist-dir", default="./chroma_db", help="Chroma persist directory")
    ap.add_argument("--collection", default="documents", help="Chroma collection name")
    ap.add_argument("--clear-db", action="store_true", help="Remove Chroma persist directory before writing to it")
    args = ap.parse_args()

    if not os.path.isdir(args.dir):
        print(f"Directory not found: {args.dir}")
        raise SystemExit(1)

    docs = load_documents_from_dir(args.dir)
    if not docs:
        print("No documents found to embed.")
        raise SystemExit(0)

    texts = [getattr(d, "page_content", "") for d in docs]
    metadatas = [getattr(d, "metadata", {}) for d in docs]
    ids = [md.get("source") or f"doc_{i}" for i, md in enumerate(metadatas)]

    if args.to_chroma:
        # sanitize metadata before indexing
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
                    if len(s) > 1000:
                        s = s[:1000] + "..."
                    out[k] = s
            return out

        for d in docs:
            try:
                if hasattr(d, "metadata") and isinstance(d.metadata, dict):
                    d.metadata = sanitize_metadata(d.metadata)
            except Exception:
                continue

        if args.clear_db and os.path.exists(args.persist_dir):
            import shutil

            print(f"Removing existing persist directory: {args.persist_dir}")
            shutil.rmtree(args.persist_dir)

        from langchain.vectorstores import Chroma
        from langchain.embeddings import HuggingFaceEmbeddings

        emb = HuggingFaceEmbeddings(model_name=args.model, model_kwargs={"device": args.device})
        db = Chroma.from_documents(documents=docs, embedding=emb, persist_directory=args.persist_dir, collection_name=args.collection)
        try:
            db.persist()
        except Exception:
            pass
        print(f"Persisted {len(docs)} documents to Chroma at {args.persist_dir} (collection={args.collection}).")
    else:
        print(f"Computing embeddings for {len(texts)} documents using {args.model} on {args.device}...")
        embeddings = compute_embeddings(texts, model_name=args.model, device=args.device)

        out_npz = save_embeddings_npz(args.out, embeddings, ids)
        out_meta = save_metadata_jsonl(args.out, ids, metadatas, texts)

        print(f"Saved embeddings -> {out_npz}")
        print(f"Saved metadata -> {out_meta}")


if __name__ == "__main__":
    main()
