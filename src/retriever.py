"""Find the knowledge-base passages most relevant to a question."""
import os

from config import N_RESULTS
from vectorstore import embed, get_collection

# Cosine distance above this means "not really related" and the chunk is dropped,
# so Claude isn't handed irrelevant text and told it's relevant.
MAX_DISTANCE = float(os.getenv("MAX_DISTANCE", "0.8"))


def retrieve(query: str, n_results: int = N_RESULTS):
    """Return a list of {"text", "source", "page", "distance"} dicts, best first."""
    collection = get_collection()
    if collection.count() == 0:
        return []

    results = collection.query(
        query_embeddings=embed([query]),
        n_results=min(n_results, collection.count()),
    )
    hits = []
    for text, meta, dist in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        if dist > MAX_DISTANCE:
            continue
        hits.append(
            {"text": text, "source": meta.get("source", "unknown"), "page": meta.get("page"), "distance": dist}
        )
    return hits


def format_context(hits) -> str:
    """Number each passage so Claude can cite it as [1], [2], ..."""
    if not hits:
        return "(No relevant passages were found in the knowledge base.)"
    blocks = []
    for i, h in enumerate(hits, start=1):
        where = h["source"] + (f", page {h['page']}" if h["page"] else "")
        blocks.append(f"[{i}] Source: {where}\n{h['text']}")
    return "\n\n---\n\n".join(blocks)


def retrieve_context(query: str, n_results: int = N_RESULTS) -> str:
    """Backwards-compatible helper: returns one text block."""
    return format_context(retrieve(query, n_results))


if __name__ == "__main__":
    import sys

    q = " ".join(sys.argv[1:]) or "What is the debt avalanche method?"
    print(f"Searching for: {q!r}  (knowledge base: {get_collection().count()} chunks)\n")
    for i, h in enumerate(retrieve(q), start=1):
        where = h["source"] + (f" p.{h['page']}" if h["page"] else "")
        print(f"[{i}] {where}  (distance {h['distance']:.2f})\n{h['text'][:300]}...\n")
