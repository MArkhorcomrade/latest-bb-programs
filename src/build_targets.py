import os
import json
import csv
from datetime import datetime, timezone

DATA_DIR = "data"
OUT_DIR = "data"
SNAPSHOT_DIR = os.path.join(OUT_DIR, "snapshots")

os.makedirs(SNAPSHOT_DIR, exist_ok=True)


def load_json(path):
    """Load JSON and return only a list of dicts."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    elif isinstance(data, dict):
        return [data]
    return []


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_csv(path, rows, headers):
    """Save selected fields only, ignore extra keys."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            if not isinstance(row, dict):
                continue
            clean_row = {h: row.get(h, "") for h in headers}
            writer.writerow(clean_row)


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    platforms = ["hackerone", "bugcrowd", "intigriti", "federacy", "yeswehack", "chaos"]

    programs = []
    for platform in platforms:
        data = load_json(os.path.join(DATA_DIR, f"{platform}.json"))
        count_before = len(programs)
        for p in data:
            if not isinstance(p, dict):
                print(f"⚠️ Skipping invalid entry in {platform}: {p}")
                continue
            p["platform"] = platform

            # Ensure targets is a list of dicts
            targets = p.get("targets", [])
            if not isinstance(targets, list):
                p["targets"] = []
            else:
                p["targets"] = [t for t in targets if isinstance(t, dict)]

            programs.append(p)
        print(f"✅ Added {len(programs) - count_before} from {platform}.json")

    # Save snapshot
    snapshot_path = os.path.join(SNAPSHOT_DIR, f"{today}.json")
    save_json(snapshot_path, programs)
    print(f"\n🎉 Saved snapshot {snapshot_path} ({len(programs)} programs)")

    # Load yesterday’s snapshot if exists
    old_ids = set()
    snapshots = sorted(os.listdir(SNAPSHOT_DIR))
    if len(snapshots) > 1:
        prev_snapshot = os.path.join(SNAPSHOT_DIR, snapshots[-2])
        prev_data = load_json(prev_snapshot)
        old_ids = {p.get("id") for p in prev_data if isinstance(p, dict)}

    # New programs detection
    new_programs = [p for p in programs if p.get("id") not in old_ids]

    if new_programs:
        save_csv(
            os.path.join(OUT_DIR, "new_programs.csv"),
            new_programs,
            headers=["id", "name", "platform"],
        )
        print(f"🆕 Found {len(new_programs)} new programs!")
    else:
        print("No new programs today ✅")

    # Full CSV export
    save_csv(
        os.path.join(OUT_DIR, "all_programs.csv"),
        programs,
        headers=["id", "name", "platform"],
    )
    print("📑 Saved all_programs.csv")


if __name__ == "__main__":
    main()
