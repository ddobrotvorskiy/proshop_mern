"""
FastMCP server wrapping M3-rag semantic search.

Provides one tool: search_project_docs(query, top_k) — searches
documentation chunks stored in PostgreSQL (rag_chunks table) using
pgvector cosine similarity with Ollama BGE-M3 embeddings.

Usage:
    python3.10 mcp_server.py                    # stdio mode (default for MCP)
    python3.10 mcp_server.py --transport sse    # SSE mode for dev testing

Requires:
    - Ollama running on localhost:11434 with bge-m3 model
    - PostgreSQL with pgvector on port 35432
    - .env with DATABASE_URL
    - pip install mcp psycopg2-binary
"""
from __future__ import annotations

from pathlib import Path

from query import search as _search

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Install FastMCP: pip install mcp")
    raise

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent

mcp = FastMCP(
    "M3-rag Docs Search",
    instructions="Semantic search over project documentation (ADRs, features, runbooks, incidents, glossary, dev history).",
)


# ---------------------------------------------------------------------------
# Tool
# ---------------------------------------------------------------------------

SEARCH_WHEN = (
    "поиск информации о продукте proshop_mern — архитектура, фичи, "
    "ADR, runbooks, incidents, glossary, dev history. "
    "You MUST use this FIRST when user asks about product functionality."
)

SEARCH_WHEN_NOT = (
    "текущее состояние feature flags — для этого есть feature-flags MCP "
    "get_feature_info."
)

SNIPPET_LEN = 200


@mcp.tool(
    description=(
        f"{SEARCH_WHEN}\n"
        f"When NOT to call: {SEARCH_WHEN_NOT}"
    ),
)
def search_project_docs(query: str, top_k: int = 5) -> list[dict]:
    """Search project documentation semantically using pgvector embeddings.

    Args:
        query: Natural-language search query (in English or Russian).
        top_k:  Maximum number of results to return (default 5).
    """
    raw_results = _search(query, top_k)

    results: list[dict] = []
    for r in raw_results:
        parent_headings = _build_breadcrumbs(r.get("section_heading", ""), r)
        text = r.get("text", "") or ""
        snippet = _make_snippet(text)

        results.append(
            _normalize(r, parent_headings, snippet)
        )

    return results


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_breadcrumbs(heading: str, chunk: dict) -> list[str]:
    """Return parent_headings (breadcrumbs) from chunk data."""
    headings = chunk.get("parent_headings")
    if isinstance(headings, list) and headings:
        return [h for h in headings if h]
    # Fallback: construct from title + section_heading
    parts: list[str] = []
    title = chunk.get("title", "")
    if title and title != heading:
        parts.append(title)
    if heading:
        parts.append(heading)
    return parts


def _make_snippet(text: str, max_len: int = SNIPPET_LEN) -> str:
    """Return a ~max_len character snippet from the full text."""
    if not text:
        return ""
    clean = " ".join(text.split())
    if len(clean) <= max_len:
        return clean
    return clean[:max_len].rsplit(" ", 1)[0] + "..."


def _normalize(raw: dict, parent_headings: list[str], snippet: str) -> dict:
    """Map internal search result → Chunk schema expected by MCP clients."""
    return {
        "source_file": raw.get("source_file", ""),
        "file_path": raw.get("file_path", ""),
        "title": raw.get("title", ""),
        "parent_headings": parent_headings,
        "score": raw.get("score", 0.0),
        "snippet": snippet,
        "doc_type": raw.get("doc_type", ""),
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
