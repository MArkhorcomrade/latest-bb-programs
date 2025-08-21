import json, os, datetime, csv
from pathlib import Path
from jinja2 import Template

DATA_DIR = Path("data")
SNAPSHOT_DIR = DATA_DIR / "snapshots"
LATEST_FILE = DATA_DIR / "latest" / "programs.json"
OUT_DIR = Path("out")

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Could not parse {path}: {e}")
        return []

def main():
    # make dirs
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    LATEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    today = datetime.date.today().strftime("%Y-%m-%d")
    snapshot_file = SNAPSHOT_DIR / f"{today}.json"

    # merge all platform files
    programs = []
    for file in DATA_DIR.glob("*.json"):
        if file.name not in ["latest", "snapshots"]:
            data = load_json(file)
            programs.extend(data)
            print(f"✅ Added {len(data)} from {file.name}")

    # save snapshot + latest
    with open(snapshot_file, "w", encoding="utf-8") as f:
        json.dump(programs, f, indent=2)
    with open(LATEST_FILE, "w", encoding="utf-8") as f:
        json.dump(programs, f, indent=2)

    print(f"\n🎉 Saved snapshot {snapshot_file} ({len(programs)} programs)")

    # detect yesterday file
    yesterday_file = SNAPSHOT_DIR / f"{(datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')}.json"
    old_programs = load_json(yesterday_file) if yesterday_file.exists() else []

    old_ids = {p["id"] for p in old_programs if "id" in p}
    new_programs = [p for p in programs if p.get("id") not in old_ids]

    # save new programs
    with open(OUT_DIR / "new_programs.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "url", "platform"])
        writer.writeheader()
        writer.writerows(new_programs)

    print(f"🆕 Found {len(new_programs)} new programs")

    # collect scopes
    old_scopes = {s for p in old_programs for s in p.get("targets", [])}
    new_scopes = []
    all_targets = []
    wildcards = []
    domains = []

    for p in programs:
        for s in p.get("targets", []):
            all_targets.append(s)
            if s.startswith("*."):
                wildcards.append(s)
            else:
                domains.append(s)
            if s not in old_scopes:
                new_scopes.append({"program": p.get("name"), "scope": s})

    # save new scopes
    with open(OUT_DIR / "new_scopes.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["program", "scope"])
        writer.writeheader()
        writer.writerows(new_scopes)

    # save targets
    with open(OUT_DIR / "targets.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(all_targets)))
    with open(OUT_DIR / "targets-wildcards.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(set(wildcards))))
    with open(OUT_DIR / "targets-domains.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(set(domains))))

    print(f"🆕 Found {len(new_scopes)} new scopes, total {len(all_targets)} targets")
    print(f"📂 Wildcards saved to targets-wildcards.txt ({len(wildcards)})")
    print(f"📂 Domains saved to targets-domains.txt ({len(domains)})")

    # generate HTML report
    template = Template("""
    <html>
    <head><title>Bug Bounty Programs Report</title></head>
    <body>
    <h1>Bug Bounty Programs - {{ today }}</h1>
    <p>Total Programs: {{ total }}</p>
    <p>New Programs Today: {{ new_count }}</p>
    <p>New Scopes Today: {{ scope_count }}</p>
    <h2>New Programs</h2>
    <ul>
      {% for p in new_programs %}
        <li><a href="{{ p.url }}">{{ p.name }}</a> ({{ p.platform }})</li>
      {% endfor %}
    </ul>
    <h2>New Scopes</h2>
    <ul>
      {% for s in new_scopes %}
        <li>{{ s.program }} → {{ s.scope }}</li>
      {% endfor %}
    </ul>
    </body>
    </html>
    """)
    html = template.render(
        today=today,
        total=len(programs),
        new_count=len(new_programs),
        scope_count=len(new_scopes),
        new_programs=new_programs,
        new_scopes=new_scopes,
    )
    with open(OUT_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("📊 Report generated at out/index.html")

if __name__ == "__main__":
    main()
