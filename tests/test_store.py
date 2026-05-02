"""Smoke tests for the compliance store."""

from pathlib import Path

from bay_street_mcp.store import ComplianceStore


def test_store_roundtrip(tmp_path: Path) -> None:
    store = ComplianceStore(db_path=tmp_path / "chroma")
    store.add(
        documents=[
            "Federally regulated financial institutions must maintain robust operational risk management.",
            "AI systems used in credit decisions require ongoing model validation.",
        ],
        ids=["e21-1", "e21-2"],
        metadatas=[
            {"regulation": "OSFI E-21", "jurisdiction": "CA", "page": 1, "source_url": ""},
            {"regulation": "OSFI E-21", "jurisdiction": "CA", "page": 2, "source_url": ""},
        ],
    )
    assert store.count() == 2

    results = store.search("model validation for AI", top_k=1)
    assert len(results) == 1
    assert "model validation" in results[0]["passage"].lower()
    assert results[0]["citation"]["regulation"] == "OSFI E-21"


def test_empty_store_returns_no_results(tmp_path: Path) -> None:
    store = ComplianceStore(db_path=tmp_path / "chroma-empty")
    assert store.count() == 0
    assert store.search("anything", top_k=3) == []
