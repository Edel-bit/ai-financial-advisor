"""Core logic: retrieve relevant knowledge, optionally search trusted websites, then ask Claude."""
import os
import re
from datetime import date

import anthropic

from config import (
    CLAUDE_MODEL,
    MAX_TOKENS,
    WEB_SEARCH_DOMAINS,
    WEB_SEARCH_ENABLED,
    WEB_SEARCH_MAX_USES,
    WEB_SEARCH_TOOL,
)
from prompts import SYSTEM_PROMPT, WEB_SEARCH_PROMPT
from retriever import format_context, retrieve

_client = None
MAX_CONTINUATIONS = 3  # how many times to resume if the API pauses a long web-search turn


def get_client():
    global _client
    if _client is None:
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise RuntimeError("ANTHROPIC_API_KEY is not set. Add it to your .env file.")
        _client = anthropic.Anthropic()
    return _client


def _tools():
    if not WEB_SEARCH_ENABLED:
        return []
    tool = {"type": WEB_SEARCH_TOOL, "name": "web_search", "max_uses": WEB_SEARCH_MAX_USES}
    if WEB_SEARCH_DOMAINS:
        tool["allowed_domains"] = WEB_SEARCH_DOMAINS
    return [tool]


def _build_request(user_message, conversation_history):
    hits = retrieve(user_message)
    augmented = (
        f"Reference passages from the knowledge base:\n\n{format_context(hits)}\n\n"
        f"=====\n\nUser question: {user_message}"
    )
    # Only the latest turn gets the retrieved passages; earlier turns stay as the plain
    # conversation. Citation numbers like [2] in earlier answers pointed at THAT turn's
    # passages, so strip them to avoid confusing them with this turn's numbering.
    history = [
        {"role": m["role"], "content": re.sub(r"\s?\[\d+\]", "", m["content"])}
        for m in (conversation_history or [])
    ]
    messages = history + [{"role": "user", "content": augmented}]
    system = SYSTEM_PROMPT.format(today=date.today().strftime("%B %d, %Y"))
    if WEB_SEARCH_ENABLED:
        system += WEB_SEARCH_PROMPT
    return system, messages, hits


def _collect_web_sources(content, web_sources):
    """Pull the web pages Claude actually cited out of the response blocks."""
    for block in content:
        for c in getattr(block, "citations", None) or []:
            if getattr(c, "type", "") == "web_search_result_location":
                entry = {"url": c.url, "title": c.title or c.url}
                if entry not in web_sources:
                    web_sources.append(entry)


def _is_web_search_setup_error(e):
    return isinstance(e, anthropic.BadRequestError) and "web_search" in str(e).lower()


def get_advice(user_message, conversation_history=None):
    """Return (answer_text, kb_hits, web_sources)."""
    system, messages, hits = _build_request(user_message, conversation_history)
    tools = _tools()
    web_sources, text = [], ""
    for _ in range(MAX_CONTINUATIONS + 1):
        kwargs = dict(model=CLAUDE_MODEL, max_tokens=MAX_TOKENS, system=system, messages=messages)
        if tools:
            kwargs["tools"] = tools
        try:
            response = get_client().messages.create(**kwargs)
        except Exception as e:
            if tools and _is_web_search_setup_error(e):
                tools = []  # web search not available on this account -> answer without it
                continue
            raise
        text += "".join(b.text for b in response.content if b.type == "text")
        _collect_web_sources(response.content, web_sources)
        if response.stop_reason != "pause_turn":
            break
        messages = messages + [{"role": "assistant", "content": response.content}]
    return text, hits, web_sources


def stream_advice(user_message, conversation_history=None):
    """Like get_advice, but yields text as it is generated (used by the web app).

    Returns (generator, kb_hits, web_sources). web_sources is filled in as the
    generator runs, so read it after the stream has finished.
    """
    system, messages, hits = _build_request(user_message, conversation_history)
    web_sources = []

    def gen():
        nonlocal messages
        tools = _tools()
        for _ in range(MAX_CONTINUATIONS + 1):
            kwargs = dict(model=CLAUDE_MODEL, max_tokens=MAX_TOKENS, system=system, messages=messages)
            if tools:
                kwargs["tools"] = tools
            try:
                with get_client().messages.stream(**kwargs) as stream:
                    for event in stream:
                        if event.type == "content_block_start" and event.content_block.type == "server_tool_use":
                            yield "\n\n*🔎 Checking trusted sources online...*\n\n"
                        elif event.type == "content_block_delta" and event.delta.type == "text_delta":
                            yield event.delta.text
                    final = stream.get_final_message()
            except Exception as e:
                if tools and _is_web_search_setup_error(e):
                    tools = []
                    continue
                raise
            _collect_web_sources(final.content, web_sources)
            if final.stop_reason != "pause_turn":
                break
            messages = messages + [{"role": "assistant", "content": final.content}]

    return gen(), hits, web_sources


def format_sources(hits, web_sources=None) -> str:
    seen, lines = set(), []
    for i, h in enumerate(hits, start=1):
        where = h["source"] + (f", page {h['page']}" if h["page"] else "")
        if where not in seen:
            seen.add(where)
            lines.append(f"[{i}] {where}")
    if web_sources:
        lines.append("\nWeb:")
        lines += [f"• {w['title']} — {w['url']}" for w in web_sources]
    return "\n".join(lines)


if __name__ == "__main__":
    print("=" * 52)
    print("💼 AI Financial Advisor - terminal chat")
    print("Ask a money or tax question. Type 'quit' to exit.")
    print("=" * 52 + "\n")

    history = []
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"quit", "exit"}:
            break
        if not user_input:
            continue
        print("\nSearching and thinking...")
        try:
            answer, hits, web = get_advice(user_input, history)
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            continue
        print(f"\nAdvisor:\n{answer}\n")
        sources = format_sources(hits, web)
        if sources:
            print("Sources:\n" + sources)
        print("-" * 52)
        history += [{"role": "user", "content": user_input}, {"role": "assistant", "content": answer}]