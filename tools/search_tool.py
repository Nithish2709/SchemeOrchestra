import requests
from config.settings import SERPER_API_KEY, SEARCH_DOMAINS


def search_tool(query: str) -> list[dict]:
    """Search government websites for scheme info using Serper API."""
    site_filter = " OR ".join(f"site:{d}" for d in SEARCH_DOMAINS)
    full_query = f"{query} ({site_filter})"

    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    payload = {"q": full_query, "num": 5}

    try:
        resp = requests.post("https://google.serper.dev/search", json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json().get("organic", [])
    except Exception as e:
        return [{"error": str(e)}]
