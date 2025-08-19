
# src/build_targets.py
import os, json, re, urllib.parse

LATEST = "data/latest/programs.json"
OUT_DIR = "out"
os.makedirs(OUT_DIR, exist_ok=True)

def host_from_url(u: str):
    try:
        return urllib.parse.urlparse(u).hostname
    except Exception:
        return None

def main():
    with open(LATEST, "r", encoding="utf-8") as f:
        programs = json.load(f)

    domains = set()
    for p in programs:
        in_scope = (p.get("targets") or {}).get("in_scope") or p.get("in_scope") or []
        for t in in_scope:
            asset_type = (t.get("type") or t.get("asset_type") or "").upper()
            target = (t.get("target") or t.get("asset_identifier") or "").strip()
            if not target:
                continue

            if asset_type in {"DOMAIN", "WILDCARD"}:
                # strip leading *.
                target = re.sub(r"^\*\.", "", target)
                domains.add(target.lower())
            elif asset_type == "URL":
                h = host_from_url(target)
                if h:
                    domains.add(h.lower())

    targets_path = os.path.join(OUT_DIR, "targets.txt")
    with open(targets_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(domains)))
    print(f"Wrote {targets_path} with {len(domains)} hosts")

if __name__ == "__main__":
    main()
