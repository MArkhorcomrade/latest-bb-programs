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
    """Save only selected headers, ignore extra fields"""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for r in rows:
            clean = {h: r.get(h, "") for h in headers}
            writer.writerow(clean)


def save_txt(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        for line in sorted(set(lines)):
            f.write(line.strip() + "\n")


def main():
    today = datetime.utcnow().strftime("%Y-%m-%d")

    # Load latest programs.json
    programs = load_json_
