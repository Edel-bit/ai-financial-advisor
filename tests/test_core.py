"""Tests for the parts of the app that don't need the API or the database."""

import advisor
from ingest import clean_text, read_pages


def test_clean_text_joins_hyphenated_words_and_spaces():
    assert clean_text("retire-\nment   account\n\n\n\nnext") == "retirement account\n\nnext"


def test_read_pages_text_file():
    pages = list(read_pages(b"hello world", "notes.txt"))
    assert pages == [(None, "hello world")]


def test_format_sources_dedupes_and_adds_web():
    hits = [
        {"source": "p17.pdf", "page": 42},
        {"source": "p17.pdf", "page": 42},
        {"source": "guide.txt", "page": None},
    ]
    web = [{"title": "IRS limits", "url": "https://irs.gov/x"}]
    out = advisor.format_sources(hits, web)
    assert out.count("p17.pdf, page 42") == 1
    assert "guide.txt" in out
    assert "IRS limits — https://irs.gov/x" in out


def test_build_request_strips_old_citations_and_adds_passages(monkeypatch):
    monkeypatch.setattr(advisor, "retrieve", lambda q: [])
    monkeypatch.setattr(advisor, "format_context", lambda hits: "PASSAGES")
    history = [{"role": "assistant", "content": "Max out your Roth [2] first [10]."}]
    system, messages, hits = advisor._build_request("What next?", history)

    assert messages[0]["content"] == "Max out your Roth first."
    assert "PASSAGES" in messages[-1]["content"]
    assert messages[-1]["content"].endswith("User question: What next?")
    assert "Educational guidance only" in system  # guardrail disclaimer stays in the prompt


def test_web_search_restricted_to_allowlist(monkeypatch):
    monkeypatch.setattr(advisor, "WEB_SEARCH_ENABLED", True)
    tools = advisor._tools()
    assert tools and "irs.gov" in tools[0]["allowed_domains"]
