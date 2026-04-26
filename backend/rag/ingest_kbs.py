"""
KB ingestion using BM25 — no vector DB or ML model required.
Markdown files are chunked by word count and indexed in memory.
Indexes are rebuilt on each process start (fast: <1s for typical KB sizes).
"""
import re
from pathlib import Path
from rank_bm25 import BM25Okapi
from ..config import KB_NAMESPACES, CHUNK_WORDS, CHUNK_OVERLAP_WORDS

# Module-level store: namespace -> {bm25, chunks}
_indexes: dict = {}


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _chunk_text(text: str, source_file: str) -> list[dict]:
    words = text.split()
    chunks = []
    i = 0
    idx = 0
    while i < len(words):
        window = words[i : i + CHUNK_WORDS]
        chunks.append({
            "chunk_id": f"{Path(source_file).stem}_c{idx}",
            "content": " ".join(window),
            "source_file": Path(source_file).name,
        })
        i += CHUNK_WORDS - CHUNK_OVERLAP_WORDS
        idx += 1
    return chunks


def _build_namespace(namespace: str, kb_dir: str) -> int:
    path = Path(kb_dir)
    if not path.exists():
        print(f"[RAG] Warning: KB directory not found: {kb_dir}")
        return 0

    all_chunks: list[dict] = []
    for md_file in sorted(path.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        all_chunks.extend(_chunk_text(text, str(md_file)))

    if not all_chunks:
        return 0

    tokenized = [_tokenize(c["content"]) for c in all_chunks]
    _indexes[namespace] = {"bm25": BM25Okapi(tokenized), "chunks": all_chunks}
    return len(all_chunks)


def ingest_all_kbs() -> dict[str, int]:
    summary = {}
    for namespace, kb_dir in KB_NAMESPACES.items():
        n = _build_namespace(namespace, kb_dir)
        summary[namespace] = n
        print(f"[RAG] Indexed '{namespace}': {n} chunks")
    return summary
