import pytest
from agent.tools import web_search, web_fetch, write_section


# ── web_search tests ──────────────────────────────────────────────────────────

def test_web_search_returns_list():
    results = web_search("HSBC bank London")
    assert isinstance(results, list)

def test_web_search_returns_dicts_with_correct_keys():
    results = web_search("Barclays financial results")
    assert len(results) > 0
    for r in results:
        assert "title" in r
        assert "url" in r
        assert "content" in r

def test_web_search_returns_non_empty_content():
    results = web_search("JPMorgan earnings 2025")
    assert any(len(r["content"]) > 0 for r in results)

def test_web_search_bad_query_does_not_crash():
    # Even a nonsense query should return a list, never raise
    results = web_search("xkqzwpqzwpqzw")
    assert isinstance(results, list)


# ── web_fetch tests ───────────────────────────────────────────────────────────

def test_web_fetch_returns_string():
    result = web_fetch("https://www.bbc.com/news")
    assert isinstance(result, str)

def test_web_fetch_truncates_long_pages():
    result = web_fetch("https://www.bbc.com/news", max_chars=500)
    assert len(result) <= 600  # small buffer for truncation message

def test_web_fetch_bad_url_does_not_crash():
    result = web_fetch("https://this-url-does-not-exist-xkqzwp.com")
    assert isinstance(result, str)
    assert "error" in result.lower()

def test_web_fetch_invalid_url_does_not_crash():
    result = web_fetch("not-a-url-at-all")
    assert isinstance(result, str)


# ── write_section tests ───────────────────────────────────────────────────────

def test_write_section_adds_to_dict():
    sections = {}
    updated = write_section(sections, "financials", "Revenue was £10bn in 2025.")
    assert "financials" in updated
    assert updated["financials"] == "Revenue was £10bn in 2025."

def test_write_section_overwrites_existing():
    sections = {"financials": "old content"}
    updated = write_section(sections, "financials", "new content")
    assert updated["financials"] == "new content"

def test_write_section_handles_multiple_sections():
    sections = {}
    write_section(sections, "financials", "Revenue data")
    write_section(sections, "news", "Recent news")
    write_section(sections, "ai_initiatives", "AI strategy")
    assert len(sections) == 3