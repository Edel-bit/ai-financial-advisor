"""Streamlit web app.  Run from the project root:  streamlit run src/app.py"""
import os

import streamlit as st
import streamlit.components.v1 as components

from advisor import format_sources, stream_advice
from config import DATA_DIR, S3_BUCKET
from ingest import ingest_bytes
from theme import CSS, header_html
from vectorstore import get_collection, get_embedder

st.set_page_config(page_title="AI Financial Advisor", page_icon="💼", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

USER_AVATAR = "🧑"
BOT_AVATAR = "💠"


def md(text: str) -> str:
    """Streamlit treats $...$ as math, which garbles money amounts. Escape the $ signs."""
    return text.replace("$", "\\$")


@st.cache_resource(show_spinner="Loading knowledge base...")
def warm_up():
    get_embedder()  # load the embedding model once per server, not per question
    return True


warm_up()

# --- SIDEBAR ---------------------------------------------------------------
with st.sidebar:
    st.header("📚 Knowledge base")
    st.metric("Passages indexed", f"{get_collection().count():,}")

    # When deployed publicly, only someone with the admin password can add documents.
    admin_pw = os.getenv("ADMIN_PASSWORD", "")
    can_upload = not admin_pw or st.text_input("Admin password to add documents", type="password") == admin_pw

    if can_upload:
        uploaded_files = st.file_uploader(
            "Add PDFs or text files (IRS pubs, textbook chapters, guides)",
            type=["pdf", "txt", "md"],
            accept_multiple_files=True,
        )
        for f in uploaded_files or []:
            key = f"processed_{f.name}_{f.size}"
            if key in st.session_state:
                continue
            with st.spinner(f"Ingesting {f.name}..."):
                data = f.getvalue()
                source = f"uploads/{f.name}"
                try:
                    n = ingest_bytes(data, source=source, category="uploads", force=True)
                except Exception as e:
                    st.error(f"Could not read {f.name}: {e}")
                    continue
                # keep a copy so the file survives a rebuild (and goes to S3 if configured)
                (DATA_DIR / "uploads").mkdir(parents=True, exist_ok=True)
                (DATA_DIR / source).write_bytes(data)
                if S3_BUCKET:
                    from s3_sync import upload_file

                    upload_file(DATA_DIR / source, f"data/raw/{source}")
            st.session_state[key] = True
            st.success(f"✅ {f.name}: {n} passages added")

    st.divider()
    if st.button("🧹 New conversation"):
        st.session_state.messages = []
        st.rerun()
    st.caption("Educational guidance only, not personalized financial, tax, or legal advice.")

# --- CHAT ------------------------------------------------------------------
components.html(header_html(get_collection().count()), height=210)

if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages and "pending" not in st.session_state:
    examples = [
        "I have $8k in credit card debt at 24% and $3k saved. What should I do first?",
        "Roth IRA or traditional 401(k) — which should I prioritize?",
        "What can I deduct as a freelancer?",
    ]
    cols = st.columns(len(examples))
    for col, ex in zip(cols, examples):
        if col.button(md(ex), use_container_width=True):
            st.session_state.pending = ex
            st.rerun()

for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar=USER_AVATAR if m["role"] == "user" else BOT_AVATAR):
        st.markdown(md(m["content"]))
        if m.get("sources"):
            with st.expander("Sources"):
                st.text(m["sources"])

user_query = st.chat_input("Ask a financial question...") or st.session_state.pop("pending", None)
if user_query:
    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(md(user_query))

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        try:
            with st.spinner("Searching knowledge base..."):
                stream, hits, web_sources = stream_advice(user_query, history)
            answer = st.write_stream(md(chunk) for chunk in stream) or ""
            if not isinstance(answer, str):
                answer = "".join(str(a) for a in answer)
            answer = answer.replace("\\$", "$")
            if not answer.strip():
                answer = (
                    "I can't help with that request. If you have a question about budgeting, "
                    "credit, saving, investing, or taxes, I'm happy to help."
                )
                st.markdown(answer)
            answer = answer.replace("\n\n*🔎 Checking trusted sources online...*\n\n", "\n\n").strip()
            sources = format_sources(hits, web_sources)
            if sources:
                with st.expander("Sources"):
                    st.text(sources)
            st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
        except Exception as e:
            st.session_state.messages.pop()  # don't keep a question with no answer
            st.error(f"Something went wrong: {e}")
