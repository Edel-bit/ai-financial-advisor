"""Load documents into the knowledge base (ChromaDB).

Usage (run from the project root):
    python src/ingest.py              # add any NEW files under data/raw/ (all subfolders)
    python src/ingest.py --reset      # wipe the database and rebuild from scratch
    python src/ingest.py --force      # re-ingest files even if already loaded

Supports .pdf, .txt and .md. The first folder under data/raw/ becomes the
document's "category" (e.g. tax_optimization, personal_finance), and PDF chunks
keep their page number so answers can cite "p17.pdf, page 42".
"""
import argparse
import hashlib
import io
import re
import sys
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from config import CHUNK_OVERLAP, CHUNK_SIZE, DATA_DIR
from vectorstore import embed, get_collection, reset_collection

import logging
logging.getLogger("pypdf").setLevel(logging.ERROR)  # hide harmless font warnings

SUPPORTED = {".pdf", ".txt", ".md"}
BATCH = 128

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def clean_text(text: str) -> str:
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)  # re-join words hyphenated across lines
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def read_pages(data: bytes, filename: str):
    """Yield (page_number or None, text) for a file's raw bytes."""
    if filename.lower().endswith(".pdf"):
        reader = PdfReader(io.BytesIO(data))
        for i, page in enumerate(reader.pages, start=1):
            yield i, page.extract_text() or ""
    else:
        yield None, data.decode("utf-8", errors="ignore")


def already_ingested(source: str) -> bool:
    found = get_collection().get(where={"source": source}, limit=1)
    return bool(found["ids"])


def delete_source(source: str):
    get_collection().delete(where={"source": source})


def ingest_bytes(data: bytes, source: str, category: str = "uploaded", force: bool = False) -> int:
    """Chunk, embed and store one document. Returns number of chunks added.

    Used both by the command line below and by the Streamlit upload sidebar.
    """
    if already_ingested(source):
        if not force:
            return 0
        delete_source(source)  # replace old chunks instead of duplicating

    ids, docs, metas = [], [], []
    for page, raw in read_pages(data, source):
        text = clean_text(raw)
        if len(text) < 50:  # skip blank/cover pages
            continue
        for j, chunk in enumerate(splitter.split_text(text)):
            uid = hashlib.sha1(f"{source}|{page}|{j}".encode()).hexdigest()
            ids.append(uid)
            docs.append(chunk)
            meta = {"source": source, "category": category}
            if page is not None:
                meta["page"] = page
            metas.append(meta)

    collection = get_collection()
    for start in range(0, len(docs), BATCH):
        end = start + BATCH
        collection.upsert(
            ids=ids[start:end],
            documents=docs[start:end],
            embeddings=embed(docs[start:end]),
            metadatas=metas[start:end],
        )
    return len(docs)


def ingest_path(path: Path, force: bool = False) -> int:
    rel = path.relative_to(DATA_DIR)
    category = rel.parts[0] if len(rel.parts) > 1 else "general"
    return ingest_bytes(path.read_bytes(), source=rel.as_posix(), category=category, force=force)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--reset", action="store_true", help="delete the database and rebuild")
    parser.add_argument("--force", action="store_true", help="re-ingest files already loaded")
    args = parser.parse_args()

    if not DATA_DIR.exists():
        sys.exit(f"No data folder found at {DATA_DIR}")

    if args.reset:
        print("Resetting knowledge base...")
        reset_collection()

    files = sorted(p for p in DATA_DIR.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED)
    print(f"Found {len(files)} documents under {DATA_DIR}\n")

    total = 0
    for path in files:
        try:
            n = ingest_path(path, force=args.force)
        except Exception as e:  # one bad PDF shouldn't stop the whole run
            print(f"  ✗ {path.relative_to(DATA_DIR)}: {e}")
            continue
        status = f"+{n} chunks" if n else "already loaded, skipped"
        print(f"  • {path.relative_to(DATA_DIR)}: {status}")
        total += n

    print(f"\nDone. Added {total} chunks. Knowledge base now holds {get_collection().count()} chunks.")


if __name__ == "__main__":
    main()
