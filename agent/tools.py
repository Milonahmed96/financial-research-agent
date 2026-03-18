import os
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

# Initialise Tavily client once at module level
_tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def web_search(query: str, max_results: int = 5) -> list[dict]:
    """
    Search the web using Tavily and return structured results.
    
    Returns a list of dicts with keys: title, url, content
    Never raises — returns empty list on failure.
    """
    try:
        response = _tavily.search(query=query, max_results=max_results)
        results = []
        for r in response.get("results", []):
            results.append({
                "title":   r.get("title", ""),
                "url":     r.get("url", ""),
                "content": r.get("content", ""),
            })
        return results
    except Exception as e:
        print(f"[web_search error] {e}")
        return []


def web_fetch(url: str, max_chars: int = 2000) -> str:
    """
    Fetch the full text content of a webpage.
    
    Strips HTML tags and truncates to max_chars.
    Never raises — returns error message string on failure.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        # Remove script and style tags
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        # Truncate to max_chars
        if len(text) > max_chars:
            text = text[:max_chars] + "... [truncated]"
        return text
    except Exception as e:
        return f"[web_fetch error] Could not fetch {url}: {e}"


def write_section(sections: dict, name: str, content: str) -> dict:
    """
    Write a section to the memo sections dict.
    
    Returns the updated sections dict.
    """
    sections[name] = content
    print(f"[write_section] Wrote section: '{name}' ({len(content)} chars)")
    return sections