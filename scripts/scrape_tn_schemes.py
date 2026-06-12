"""
Scraper for tn.gov.in/scheme/data_view pages.
Run: python scripts/scrape_tn_schemes.py
"""
import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path

BASE_URL = "https://www.tn.gov.in/scheme/data_view/"
OUTPUT = Path(__file__).parent.parent / "data" / "schemes" / "scraped_tn_schemes.json"

SCHEME_IDS = list(range(11890, 11910))  # Adjust range as needed


def scrape_scheme(scheme_id: int) -> dict | None:
    url = f"{BASE_URL}{scheme_id}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, "html.parser")
        name = soup.find("h1") or soup.find("h2")
        return {
            "scheme_id": f"TN_SCH_SCRAPED_{scheme_id}",
            "name_en": name.get_text(strip=True) if name else f"Scheme {scheme_id}",
            "type": "state",
            "official_source": url,
            "active": True,
        }
    except Exception as e:
        print(f"Error scraping {scheme_id}: {e}")
        return None


def main():
    results = []
    for sid in SCHEME_IDS:
        data = scrape_scheme(sid)
        if data:
            results.append(data)
            print(f"Scraped: {data['name_en']}")

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Saved {len(results)} schemes to {OUTPUT}")


if __name__ == "__main__":
    main()
