
# src/diff_latest.py
import os, json, glob, re, urllib.parse
import pandas as pd

SNAP_DIR = "data/snapshots"
OUT_DIR = "out"
LATEST = "data/latest/programs.json"
os.makedirs(OUT_DIR, exist_ok=True)

def list_snapshots():
    files = sorted(glob.glob(os.path.join(SNAP_DIR, "*.json")))
    return files

def program_key(p):
    # A robust key across platforms – name + platform (URL is sometimes unique too)
    return f"{p.get('name','').strip()}||{p.get('platform','').strip()}"

def scope_entries(p):
    rows = []
    in_scope = (p.get("targets") or {}).get("in_scope") or p.get("in_scope") or []
    for t in in_scope:
        asset_type = (t.get("type") or t.get("asset_type") or "").upper()
        target = (t.get("target") or t.get("asset_identifier") or "").strip()
        if asset_type and target:
            rows.append((asset_type, target))
    return set(rows)

def main():
    snaps = list_snapshots()
    if len(snaps) < 2:
        print("Only one snapshot exists; skipping diff.")
        # create empty CSVs so later steps don't fail
        pd.DataFrame(columns=["program","platform","url"]).to_csv(os.path.join(OUT_DIR,"new_programs.csv"), index=False)
        pd.DataFrame(columns=["program","platform","asset_type","target"]).to_csv(os.path.join(OUT_DIR,"new_scopes.csv"), index=False)
        return

    latest_path = snaps[-1]
    prev_path = snaps[-2]

    latest = json.load(open(latest_path, "r", encoding="utf-8"))
    prev = json.load(open(prev_path, "r", encoding="utf-8"))

    # Index by key
    prev_map = {program_key(p): p for p in prev}
    latest_map = {program_key(p): p for p in latest}

    # New programs
    new_keys = set(latest_map.keys()) - set(prev_map.keys())
    new_programs = []
    for k in sorted(new_keys):
        p = latest_map[k]
        new_programs.append({
            "program": p.get("name"),
            "platform": p.get("platform"),
            "url": p.get("url"),
        })
    df_new = pd.DataFrame(new_programs)
    df_new.to_csv(os.path.join(OUT_DIR, "new_programs.csv"), index=False)

    # New scope entries (for programs that existed before)
    rows = []
    for k, p in latest_map.items():
        if k not in prev_map:
            # all scope is "new" but we already mark the program above; skip to avoid duplication
            continue
        old_scope = scope_entries(prev_map[k])
        new_scope = scope_entries(p)
        added = sorted(new_scope - old_scope)
        for asset_type, target in added:
            rows.append({
                "program": p.get("name"),
                "platform": p.get("platform"),
                "asset_type": asset_type,
                "target": target,
            })
    df_scopes = pd.DataFrame(rows)
    df_scopes.to_csv(os.path.join(OUT_DIR, "new_scopes.csv"), index=False)

    print(f"New programs: {len(df_new)}")
    print(f"New scope entries: {len(df_scopes)}")

if __name__ == "__main__":
    main()
