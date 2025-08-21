import os
import json
import csv
from datetime import datetime

DATA_DIR = "data"
SNAPSHOT_DIR = os.path.join(DATA_DIR, "snapshots")
LATEST_FILE = os.path.join(DATA_DIR, "latest", "programs.json")
OUT_DIR = "out"

def save_csv(path, rows, headers):
    """Save rows as CSV with only selected headers (ignore extra fields)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            if not isinstance(row, dict):
                continue
            clean = {h: row.get(h, "") for h in headers}
            writer.writerow(clean)

def save_txt(path, lines):
    """Save plain text file with one entry per line."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(set(lines))))

def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)

    # load today's programs
    programs = load_json(LATEST_FILE)
    today = datetime.utcnow().strftime("%Y-%m-%d")

    snapshot_file = os.path.join(SNAPSHOT_DIR, f"{today}.json")
    with open(snapshot_file, "w", encoding="utf-8") as f:
        json.dump(programs, f, indent=2)

    print(f"🎉 Saved snapshot {snapshot_file} ({len(programs)} programs)")

    # load yesterday snapshot if exists
    snapshots = sorted(os.listdir(SNAPSHOT_DIR))
    old_programs = []
    if len(snapshots) > 1:
        yesterday = os.path.join(SNAPSHOT_DIR, snapshots[-2])
        old_programs = load_json(yesterday)

    old_ids = {p.get("id") for p in old_programs if isinstance(p, dict)}
    new_programs = [p for p in programs if isinstance(p, dict) and p.get("id") not in old_ids]

    # extract new scopes
    old_scopes = {
        (s.get("program"), s.get("scope"))
        for p in old_programs if isinstance(p, dict)
        for s in p.get("targets", [])
        if isinstance(s, dict)
    }
    new_scopes = []
    for p in new_programs:
        for s in p.get("targets", []):
            if isinstance(s, dict):
                key = (s.get("program"), s.get("scope"))
                if key not in old_scopes:
                    new_scopes.append(s)

    # save outputs
    save_csv(os.path.join(OUT_DIR, "new_programs.csv"), new_programs, headers=["id", "name", "platform"])
    save_csv(os.path.join(OUT_DIR, "new_scopes.csv"), new_scopes, headers=["program", "scope"])

    # targets.txt: collect all domains/hosts
    targets = []
    for p in programs:
        for s in p.get("targets", []):
            if isinstance(s, dict):
                scope = s.get("scope", "")
                if scope:
                    targets.append(scope)
    save_txt(os.path.join(OUT_DIR, "targets.txt"), targets)

    # HTML report
    html_file = os.path.join(OUT_DIR, "index.html")
    with open(html_file, "w", encoding="utf-8") as f:
        f.write("<html><head><title>Bug Bounty Report</title></head><body>")
        f.write(f"<h1>Bug Bounty Programs ({today})</h1>")
        f.write(f"<p>Total programs: {len(programs)}</p>")
        f.write("<h2>New Programs</h2><ul>")
        for p in new_programs:
            f.write(f"<li>{p.get('name')} ({p.get('platform')})</li>")
        f.write("</ul>")
        f.write("<h2>New Scopes</h2><ul>")
        for s in new_scopes:
            f.write(f"<li>{s.get('scope')}</li>")
        f.write("</ul>")
        f.write("</body></html>")

    print(f"✅ Outputs saved to {OUT_DIR}")

if __name__ == "__main__":
    main()
