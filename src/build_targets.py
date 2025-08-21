import os
import json
import csv
from datetime import datetime

DATA_DIR = "data"
SNAPSHOT_DIR = os.path.join(DATA_DIR, "snapshots")
LATEST_FILE = os.path.join(DATA_DIR, "latest", "programs.json")
OUT_DIR = "out"

os.makedirs(SNAPSHOT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LATEST_FILE), exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def save_csv(path, rows, headers):
    """Save only selected headers, ignoring extra fields."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for r in rows:
            if not isinstance(r, dict):
                continue
            clean = {h: r.get(h, "") for h in headers}  # keep only required keys
            writer.writerow(clean)


def save_txt(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        for line in sorted(set(lines)):
            f.write(line.strip() + "\n")


def main():
    today = datetime.utcnow().strftime("%Y-%m-%d")

    # Load latest programs.json
    programs = load_json(LATEST_FILE)

    # Ensure only dicts
    programs = [p for p in programs if isinstance(p, dict)]

    # Save snapshot
    snapshot_file = os.path.join(SNAPSHOT_DIR, f"{today}.json")
    save_json(snapshot_file, programs)
    print(f"\n🎉 Saved snapshot {snapshot_file} ({len(programs)} programs)")

    # Compare with previous snapshot
    snapshots = sorted(os.listdir(SNAPSHOT_DIR))
    if len(snapshots) > 1:
        yesterday_file = os.path.join(SNAPSHOT_DIR, snapshots[-2])
        old_programs = load_json(yesterday_file)
        old_ids = {p.get("id") for p in old_programs if isinstance(p, dict)}

        new_programs = [p for p in programs if p.get("id") not in old_ids]

        # collect scopes
        old_scopes = {(p.get("id"), s) for p in old_programs if isinstance(p, dict) for s in p.get("targets", [])}
        new_scopes = []
        for p in programs:
            for s in p.get("targets", []):
                if (p.get("id"), s) not in old_scopes:
                    new_scopes.append({"program": p.get("id"), "scope": s})

        # Save filtered CSVs
        save_csv(
            os.path.join(OUT_DIR, "new_programs.csv"),
            new_programs,
            headers=["id", "name", "platform"]
        )

        save_csv(
            os.path.join(OUT_DIR, "new_scopes.csv"),
            new_scopes,
            headers=["program", "scope"]
        )

        # Extract all targets
        all_targets = []
        for p in programs:
            all_targets.extend(p.get("targets", []))
        save_txt(os.path.join(OUT_DIR, "targets.txt"), all_targets)

        print(f"✅ Saved {len(new_programs)} new programs")
        print(f"✅ Saved {len(new_scopes)} new scopes")
        print(f"✅ Saved {len(all_targets)} total targets")

    else:
        print("ℹ️ First snapshot — no previous data to diff.")


if __name__ == "__main__":
    main()
