#!/usr/bin/env python3
"""
Split text into fixed-size character chunks with overlap.

Default chunk size: 3000 characters
Default overlap: 200 characters

Usage:
  python scripts/split_text.py --file path/to/text.txt
  python scripts/split_text.py --file path/to/text.txt --chunk 3000 --overlap 200 --outdir chunks

Saves chunks to `<outdir>/<basename>_chunk_<i>.txt`.
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import List


def split_text(text: str, chunk_size: int = 3000, overlap: int = 200) -> List[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0:
        raise ValueError("overlap must be >= 0")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks: List[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = start + chunk_size
        chunks.append(text[start:end])
        if end >= n:
            break
        # move start forward but keep overlap
        start = end - overlap
    return chunks


def save_chunks(chunks: List[str], outdir: str, base: str) -> None:
    os.makedirs(outdir, exist_ok=True)
    for i, c in enumerate(chunks, start=1):
        path = os.path.join(outdir, f"{base}_chunk_{i:03}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(c)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="Path to input text file")
    ap.add_argument("--chunk", type=int, default=3000, help="Chunk size in chars")
    ap.add_argument("--overlap", type=int, default=200, help="Overlap size in chars")
    ap.add_argument("--outdir", default="./chunks", help="Output directory for chunks")
    args = ap.parse_args()

    if not args.file:
        print("Provide --file <path>")
        raise SystemExit(2)
    if not os.path.isfile(args.file):
        print(f"File not found: {args.file}")
        raise SystemExit(3)

    with open(args.file, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = split_text(text, chunk_size=args.chunk, overlap=args.overlap)
    base = os.path.splitext(os.path.basename(args.file))[0]
    save_chunks(chunks, args.outdir, base)
    print(f"Wrote {len(chunks)} chunks to {os.path.abspath(args.outdir)}")


if __name__ == "__main__":
    main()
