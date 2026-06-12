"""
Fetches central schemes from myscheme.gov.in API.
Run: python scripts/scrape_central_schemes.py
"""
import json
import requests
from pathlib import Path

API_URL = "https://api.myscheme.gov.in/search/v4/schemes"
OUTPUT = Path(__file__).parent.parent / "data" / "schemes" / "scraped_central_schemes.json"

PARAMS = {
    "lang": "en",
    "q": "Tamil Nadu students scholarship",
    "from": 0,
    "size": 20,
}


def main():
    try:
        resp = requests.get(API_URL, params=PARAMS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        schemes = data.get("data", {}).get("hits", [])

        results = []
        for s in schemes:
            src = s.get("_source", {})
            results.append({
                "scheme_id": f"CN_SCH_API_{src.get('schemeId', '')}",
                "name_en": src.get("schemeName", ""),
                "type": "central",
                "category": src.get("schemeCategory", ""),
                "description_en": src.get("briefDescription", ""),
                "apply_url": src.get("applicationProcess", {}).get("applyOnline", ""),
                "official_source": f"https://www.myscheme.gov.in/schemes/{src.get('schemeId', '')}",
                "active": True,
            })

        with open(OUTPUT, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"✅ Saved {len(results)} central schemes to {OUTPUT}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
