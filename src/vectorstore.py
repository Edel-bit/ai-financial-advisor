"""Shared ChromaDB connection + embedding model (ONNX version of all-MiniLM-L6-v2, no PyTorch)."""
from functools import lru_cache

import chromadb

from config import CHROMA_DIR, COLLECTION_NAME


@lru_cache(maxsize=1)
def get_embedder():
    from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

    return ONNXMiniLM_L6_V2()


@lru_cache(maxsize=1)
def get_collection():
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"})


def embed(texts):
    vectors = get_embedder()(list(texts))
    return [[float(x) for x in v] for v in vectors]


def reset_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    get_collection.cache_clear()
    return get_collection()