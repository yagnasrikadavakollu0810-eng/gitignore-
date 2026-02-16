#!/usr/bin/env python3
"""
Load .txt files using LangChain's `TextLoader`.

Usage:
  python scripts/load_texts.py path/to/file_or_directory

If a directory is provided the script will load all `*.txt` files inside it.
"""
from __future__ import annotations

import os
import sys
from dotenv import load_dotenv

load_dotenv()


def load_text_file(path: str):
    """Load a single .txt file and return LangChain Document(s)."""
    try:
        from langchain.document_loaders import TextLoader
    except Exception as exc:
        raise RuntimeError("langchain is required: pip install langchain") from exc

    loader = TextLoader(path, encoding="utf-8")
    docs = loader.load()
    # ensure source metadata
    for d in docs:
        d.metadata.setdefault("source", path)
    return docs


def load_texts_in_dir(directory: str, pattern: str = "*.txt"):
    import glob

    files = sorted(glob.glob(os.path.join(directory, pattern)))
    all_docs = []
    for f in files:
        try:
            docs = load_text_file(f)
            all_docs.extend(docs)
        except Exception as e:
            print(f"Failed to load {f}: {e}")
    return all_docs


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/load_texts.py <file_or_directory>")
        sys.exit(1)

    target = sys.argv[1]
    if os.path.isdir(target):
        docs = load_texts_in_dir(target)
    elif os.path.isfile(target) and target.lower().endswith(".txt"):
        docs = load_text_file(target)
    else:
        print("Provide a .txt file or a directory containing .txt files")
        sys.exit(1)

    print(f"Loaded {len(docs)} document(s).")
    for i, d in enumerate(docs[:5], start=1):
        src = d.metadata.get("source", "<unknown>")
        print(f"--- Document {i} (source: {src}) ---")
        print(d.page_content[:500])


if __name__ == "__main__":
    main()
