#!/usr/bin/env python3
"""
Extract text from a PDF using LangChain's UnstructuredPDFLoader with a
fallback to the `unstructured` library's partition_pdf.

Usage:
  python scripts/extract_pdf.py path/to/file.pdf

Outputs a .txt file next to the PDF (same basename) and prints a preview.
"""
from __future__ import annotations

import os
import sys
from dotenv import load_dotenv

load_dotenv()


def extract_using_langchain(path: str) -> str:
    try:
        from langchain.document_loaders import UnstructuredPDFLoader

        loader = UnstructuredPDFLoader(path)
        docs = loader.load()
        texts = [getattr(d, "page_content", "") for d in docs]
        return "\n\n".join(t for t in texts if t)
    except Exception as exc:  # pragma: no cover - fallback path
        raise


def extract_using_unstructured(path: str) -> str:
    try:
        from unstructured.partition.pdf import partition_pdf

        elements = partition_pdf(filename=path)
        texts: list[str] = []
        for el in elements:
            # many elements expose get_text(); fall back to str()
            txt = getattr(el, "get_text", lambda: None)()
            if not txt:
                txt = str(el)
            if txt:
                texts.append(txt)
        return "\n\n".join(texts)
    except Exception:
        raise


def extract_text(path: str) -> str:
    # Try LangChain loader first, then unstructured directly
    try:
        return extract_using_langchain(path)
    except Exception:
        return extract_using_unstructured(path)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/extract_pdf.py <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print("File not found:", pdf_path)
        sys.exit(1)

    try:
        text = extract_text(pdf_path)
    except Exception as e:
        print("Extraction failed:", e)
        sys.exit(2)

    # Save output next to PDF
    out_path = os.path.splitext(pdf_path)[0] + ".txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)

    print("--- Preview ---")
    print(text[:1000])
    print(f"Saved extracted text to {out_path}")


if __name__ == "__main__":
    main()
