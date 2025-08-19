
# src/fetch_latest.py
import os, json, requests, datetime
from datetime import timezone

DATA_DIR = "data"
SNAP_DIR = os.path.join(DATA_DIR, "snapshots")
LATEST_DIR = os.path.join(DATA_DIR, "latest")
os.makedirs(SNAP_DIR, exist_ok=True)
os.makedirs(LATEST_DIR, exist_ok=True)

URL = "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/programs.json"

def today_utc_date():
    # Runner fires at 01:00 UTC which is 06:00 PKT; date is the same in both zones
    return datetime.datetime.now(timezone.utc).date().isoformat()

def main():
    r = requests.get(URL, timeout=60)
    r.raise_for_status()
    data = r.json()
    today = today_utc_date()

    # Save snapshot
    snap_path = os.path.join(SNAP_DIR, f"{today}.json")
    with open(snap_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Update latest symlink/copy
    latest_path = os.path.join(LATEST_DIR, "programs.json")
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved snapshot: {snap_path}")
    print(f"Updated: {latest_path}")
    print(f"Programs count: {len(data)}")

if __name__ == "__main__":
    main()
