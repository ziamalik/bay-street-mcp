"""Ingest a regulation PDF into the compliance store.

Usage:
    bay-street-ingest data/osfi-e21.pdf \\
        --regulation "OSFI Guideline E-21" \\
        --jurisdiction CA \\
        --source-url "https://www.osfi-bsif.gc.ca/..."
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import pypdf

from bay_street_mcp.store import ComplianceStore

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
MIN_CHUNK_WORDS = 50


def extract_pages(pdf_path: Path) -> list[tuple[int, str]]:
    reader = pypdf.PdfReader(str(pdf_path))
    return [(i + 1, page.extract_text() or "") for i, page in enumerate(reader.pages)]


def chunk_pages(pages: list[tuple[int, str]]) -> list[tuple[int, str]]:
    chunks: list[tuple[int, str]] = []
    step = CHUNK_SIZE - CHUNK_OVERLAP
    for page_num, text in pages:
        words = text.split()
        if not words:
            continue
        for start in range(0, len(words), step):
            chunk_words = words[start : start + CHUNK_SIZE]
            if len(chunk_words) < MIN_CHUNK_WORDS:
                continue
            chunks.append((page_num, " ".join(chunk_words)))
    return chunks


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest a regulation PDF into Bay Street MCP.")
    parser.add_argument("pdf", type=Path, help="Path to the regulation PDF.")
    parser.add_argument("--regulation", required=True, help="Regulation name, e.g. 'OSFI Guideline E-21'.")
    parser.add_argument("--jurisdiction", default="CA", help="Jurisdiction code (default: CA).")
    parser.add_argument("--source-url", default="", help="Source URL for citation.")
    args = parser.parse_args()

    if not args.pdf.exists():
        raise SystemExit(f"PDF not found: {args.pdf}")

    print(f"Reading {args.pdf}...")
    pages = extract_pages(args.pdf)
    chunks = chunk_pages(pages)
    print(f"Extracted {len(chunks)} chunks across {len(pages)} pages.")

    store = ComplianceStore.load_default()

    documents: list[str] = []
    ids: list[str] = []
    metadatas: list[dict] = []
    for page_num, chunk in chunks:
        seed = f"{args.regulation}:{page_num}:{chunk[:120]}"
        chunk_id = hashlib.sha1(seed.encode()).hexdigest()
        documents.append(chunk)
        ids.append(chunk_id)
        metadatas.append(
            {
                "regulation": args.regulation,
                "jurisdiction": args.jurisdiction,
                "page": page_num,
                "source_url": args.source_url,
            }
        )

    store.add(documents=documents, ids=ids, metadatas=metadatas)
    print(f"Stored {len(documents)} chunks. Store now contains {store.count()} total passages.")


if __name__ == "__main__":
    main()
