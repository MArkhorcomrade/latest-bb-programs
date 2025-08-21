import json
import os
from datetime import datetime
import csv

DATA_DIR = "data"
LATEST = os.path.join(DATA_DIR, "latest", "programs.json")
SNAPSHOT_DIR = os.path.join(DATA_DIR, "snapshots")
OUT_DIR = "out"

def find_yesterday_snapshot(today_str):
    """Find yesterday’s snapshot if available"""
    try:
        today = datetime.strptime(today_str, "%Y-%m-%d")
        yesterday = today.fromordinal(today.toordinal() - 1).strftime("%Y-%m-%d")
        candidate = os.path.join(SNAPSHOT_DIR, f"{yesterday}.json")
        return candidate if os.path.exists(candidate) else None
    except Exception:
        return None

def save_csv(path, rows, headers):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

def main():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    snapshot_file = os.path.join(SNAPSHOT_DIR, f"{today}.json")

    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)

    # Load latest merged programs
    with open(LATEST, "r", encoding="utf-8") as f:
        programs = json.load(f)

    # Ensure only dicts are processed
    clean_programs = []
    for p in programs:
        if isinstance(p, dict):
            clean_programs.append(p)
        else:
            print(f"⚠️ Skipping invalid entry: {p}")

    # Save today’s snapshot
    with open(snapshot_file, "w", encoding="utf-8") as f:
        json.dump(clean_programs, f, indent=2)

    print(f"\n🎉 Saved snapshot {snapshot_file} ({len(clean_programs)} programs)")

    # Load yesterday’s snapshot (if exists)
    yesterday_file = find_yesterday_snapshot(today)
    old_ids, old_scopes = set(), set()
    if yesterday_file:
        with open(yesterday_file, "r", encoding="utf-8") as f:
            old_programs = json.load(f)
            for p in old_programs:
                if isinstance(p, dict):
                    if "id" in p:
                        old_ids.add(p["id"])
                    for s in p.get("domains", []):
                        old_scopes.add(s)

    # Identify new programs
    new_programs = [p for p in clean_programs if p.get("id") not in old_ids]

    # Identify new scopes
    all_scopes = []
    for p in clean_programs:
        if isinstance(p, dict):
            for s in p.get("domains", []):
                all_scopes.append({"program": p.get("name", "unknown"), "scope": s})

    new_scopes = [s for s in all_scopes if s["scope"] not in old_scopes]

    # Separate targets into wildcards vs domains
    wildcards, domains = [], []
    for s in all_scopes:
        scope = s["scope"]
        if scope.startswith("*."):
            wildcards.append(scope)
        else:
            domains.append(scope)

    # Save outputs
    save_csv(os.path.join(OUT_DIR, "new_programs.csv"), new_programs, headers=["id", "name", "platform"])
    save_csv(os.path.join(OUT_DIR, "new_scopes.csv"), new_scopes, headers=["program", "scope"])

    with open(os.path.join(OUT_DIR, "targets.txt"), "w", encoding="utf-8") as f:
        f.write("# Wildcards\n")
        f.write("\n".join(sorted(set(wildcards))))
        f.write("\n\n# Domains\n")
        f.write("\n".join(sorted(set(domains))))

    print(f"✅ Found {len(new_programs)} new programs")
    print(f"✅ Found {len(new_scopes)} new scopes")
    print(f"✅ Extracted {len(domains)} domains and {len(wildcards)} wildcards")

if __name__ == "__main__":
    main()
