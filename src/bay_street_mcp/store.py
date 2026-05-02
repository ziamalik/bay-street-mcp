"""Vector store wrapper around Chroma.

The store keeps regulation passages with citation metadata so callers can
return source-attributed answers.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings

DEFAULT_DB_PATH = Path(os.environ.get("BAY_STREET_DB", ".chroma"))
COLLECTION_NAME = "compliance"


class ComplianceStore:
    def __init__(self, db_path: Path = DEFAULT_DB_PATH) -> None:
        db_path.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=str(db_path),
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    @classmethod
    def load_default(cls) -> ComplianceStore:
        return cls()

    def count(self) -> int:
        return self.collection.count()

    def add(
        self,
        documents: list[str],
        ids: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None:
        self.collection.add(documents=documents, ids=ids, metadatas=metadatas)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        result = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        documents = result["documents"][0] if result["documents"] else []
        metadatas = result["metadatas"][0] if result["metadatas"] else []
        distances = result["distances"][0] if result["distances"] else []
        return [
            {
                "passage": doc,
                "citation": meta,
                "distance": dist,
            }
            for doc, meta, dist in zip(documents, metadatas, distances, strict=False)
        ]
