# AI Financial Advisor

RAG chatbot for U.S. personal finance and tax questions. Streamlit UI → retrieves passages from a ChromaDB knowledge base (IRS publications, finance guides) → Claude answers with citations, optionally searching an allowlist of trusted sites. Deploys to AWS with Docker; the knowledge base syncs through S3.

## Layout
- `src/app.py` – Streamlit UI (chat, sidebar uploads behind ADMIN_PASSWORD)
- `src/advisor.py` – builds the prompt, calls the Claude API (streaming + web search)
- `src/prompts.py` – system prompt and guardrails
- `src/retriever.py`, `src/vectorstore.py` – ChromaDB search and embeddings
- `src/ingest.py` – loads PDFs/text from `data/raw/` into ChromaDB
- `src/config.py` – ALL settings and env vars live here; import from it, never hardcode names
- `src/theme.py` – CSS and animated HTML header (Newsreader + Public Sans, navy/light-blue theme)
- `eval/` – accuracy and safety test results

## Commands
- Run app: `streamlit run src/app.py`
- Rebuild knowledge base: `python src/ingest.py --reset`
- Check retrieval: `python src/retriever.py "question"`
- Tests: `pytest`
- Lint/format: `ruff check . --fix && ruff format .`

## Rules
- Never put secrets in code. They come from `.env` (local) or environment variables (server). Never print or log the API key.
- Never commit `.env`, `chroma_db/`, `venv/`, or `data/raw/**/*.pdf`.
- Keep the guardrails in `prompts.py` intact (no tax evasion help, no stock picks, the disclaimer line).
- Escape `$` in text shown with st.markdown (see `md()` in app.py) so money amounts don't render as math.
- Don't show raw exception text to users; log it and show a friendly message.
- Run `pytest` and `ruff check .` before saying a change is done.
