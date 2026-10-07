"""Central settings so every script uses the SAME database, collection and models.

The original bug: ingest.py wrote to a collection called "financial_docs" while
retriever.py read from "financial_knowledge", so anything uploaded through the
app was never searched. Everything now imports its names from here.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Project root = the folder that contains src/. Paths no longer depend on
# which directory you launch the app from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

DATA_DIR = PROJECT_ROOT / "data" / "raw"
CHROMA_DIR = Path(os.getenv("CHROMA_DIR", PROJECT_ROOT / "chroma_db"))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "financial_knowledge")

# Claude model used to write answers. Override in .env without touching code.
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2048"))

# Chunking: ~1000 characters keeps a full tax rule or worked example together.
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
N_RESULTS = int(os.getenv("N_RESULTS", "6"))

# Optional AWS settings (only used by s3_sync.py / Docker startup)
S3_BUCKET = os.getenv("S3_BUCKET", "")
S3_PREFIX = os.getenv("S3_PREFIX", "ai-financial-advisor")

# Web search: lets Claude look up current figures (contribution limits, savings rates,
# new rules) on trusted sites. Turn off with WEB_SEARCH=false in .env.
WEB_SEARCH_ENABLED = os.getenv("WEB_SEARCH", "true").lower() == "true"
WEB_SEARCH_TOOL = os.getenv("WEB_SEARCH_TOOL", "web_search_20250305")
WEB_SEARCH_MAX_USES = int(os.getenv("WEB_SEARCH_MAX_USES", "3"))  # caps searches (and cost) per question
WEB_SEARCH_DOMAINS = [
    # Government: tax, banking, investing, retirement, student loans
    "irs.gov", "consumerfinance.gov", "fdic.gov", "ncua.gov", "investor.gov", "sec.gov",
    "finra.org", "ssa.gov", "studentaid.gov", "treasurydirect.gov", "federalreserve.gov",
    "healthcare.gov", "medicare.gov", "usa.gov",
    # Widely used rate comparison sites (for current savings/CD rates)
    "bankrate.com", "nerdwallet.com", "depositaccounts.com",
]