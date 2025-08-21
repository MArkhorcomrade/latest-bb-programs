import os
import requests
import json
from pathlib import Path

OUT = Path("data/dorking.json")

# Example with Bing Search API (you can also use Google Custom Search API)
API_KEY = os.getenv("BING_API_KEY")
ENDPOINT = "https://api.bing.microsoft.com/v7.0/search"

# Dorks to discover self-hosted programs
QUERIES = [
    '"responsible disclosure" inurl:security',
    '"bug bounty" site:.com',
    '"report vulnerability" "security.txt"',
    'inurl:/.well-known/security.txt'
]

def fetch_results(query):
    headers = {"Ocp-Apim-Subscription-Key": API_KEY}
    params = {"q": query, "count": 20}
    r = requests.get(ENDPOINT, headers=headers, params=params)
    r.raise_for_status()
    return r.json().get("webPages", {}).get("value", [])

def main():
    all_programs = []
    for q in QUERIES:
        print(f"🔍 Running dork: {q}")
        results = fetch_results(q)
        for item in results:
            url = item.get("url")
            title = item.get("name", "")
            desc = item.get("snippet", "")
            if url:
                all_programs.append({
                    "id": url,
                    "name": title,
                    "url": url,
                    "description": desc,
                    "platform": "self-hosted"
                })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(all_programs, f, indent=2)

    print(f"✅ Saved {len(all_programs)} self-hosted programs to {OUT}")

if __name__ == "__main__":
    main()
