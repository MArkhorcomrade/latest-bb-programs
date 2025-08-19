import requests, os

# Current data sources in arkadiyt/bounty-targets-data
DATA_URLS = {
    "hackerone": "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/hackerone_data.json",
    "bugcrowd": "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/bugcrowd_data.json",
    "intigriti": "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/intigriti_data.json",
    "federacy": "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/federacy_data.json",
    "yeswehack": "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/yeswehack_data.json"
}

def main():
    os.makedirs("data", exist_ok=True)
    for name, url in DATA_URLS.items():
        print(f"Fetching {name} data...")
        r = requests.get(url)
        r.raise_for_status()
        with open(f"data/{name}.json", "w", encoding="utf-8") as f:
            f.write(r.text)
        print(f"✅ Saved {name}.json")

if __name__ == "__main__":
    main()
