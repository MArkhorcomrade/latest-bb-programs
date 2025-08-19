
# src/report.py
import os, json, pandas as pd
from jinja2 import Template
from datetime import datetime, timezone

OUT_DIR = "out"
DATA_LATEST = "data/latest/programs.json"
SNAP_DIR = "data/snapshots"
os.makedirs(OUT_DIR, exist_ok=True)

def load_csv(path):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return pd.read_csv(path)
    return pd.DataFrame()

def main():
    with open(DATA_LATEST, "r", encoding="utf-8") as f:
        programs = json.load(f)
    total_programs = len(programs)

    new_programs = load_csv(os.path.join(OUT_DIR, "new_programs.csv"))
    new_scopes = load_csv(os.path.join(OUT_DIR, "new_scopes.csv"))
    targets_count = 0
    targets_path = os.path.join(OUT_DIR, "targets.txt")
    if os.path.exists(targets_path):
        with open(targets_path, "r", encoding="utf-8") as f:
            targets_count = len([x for x in f.read().splitlines() if x.strip()])

    html_tmpl = Template(\"\"\"\
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Latest Bug Bounty Programs — Report</title>
  <style>
    body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Arial,sans-serif;margin:32px;line-height:1.5}
    h1{margin:0 0 4px}
    .muted{color:#666}
    .pill{display:inline-block;padding:4px 10px;border-radius:999px;background:#eee;margin-right:6px}
    table{border-collapse:collapse;width:100%;margin-top:12px}
    th,td{border:1px solid #eee;padding:8px;text-align:left}
    th{background:#fafafa}
    pre{background:#fafafa;border:1px solid #eee;padding:10px;border-radius:8px;white-space:pre-wrap}
  </style>
</head>
<body>
  <h1>Latest Bug Bounty Programs</h1>
  <div class="muted">Generated at {{ generated_at }}</div>
  <div style="margin-top:10px;">
    <span class="pill">Total programs: {{ total_programs }}</span>
    <span class="pill">New programs today: {{ new_programs_count }}</span>
    <span class="pill">New scope entries: {{ new_scopes_count }}</span>
    <span class="pill">Targets extracted: {{ targets_count }}</span>
  </div>

  <h2>New Programs</h2>
  {% if new_programs_count == 0 %}
    <p class="muted">No new programs added today.</p>
  {% else %}
    <table>
      <thead><tr><th>Program</th><th>Platform</th><th>URL</th></tr></thead>
      <tbody>
      {% for _, row in new_programs.iterrows() %}
        <tr><td>{{ row["program"] }}</td><td>{{ row["platform"] }}</td><td><a href="{{ row["url"] }}">{{ row["url"] }}</a></td></tr>
      {% endfor %}
      </tbody>
    </table>
  {% endif %}

  <h2>New Scope Entries</h2>
  {% if new_scopes_count == 0 %}
    <p class="muted">No new scope entries today.</p>
  {% else %}
    <table>
      <thead><tr><th>Program</th><th>Platform</th><th>Type</th><th>Target</th></tr></thead>
      <tbody>
      {% for _, row in new_scopes.iterrows() %}
        <tr><td>{{ row["program"] }}</td><td>{{ row["platform"] }}</td><td>{{ row["asset_type"] }}</td><td>{{ row["target"] }}</td></tr>
      {% endfor %}
      </tbody>
    </table>
  {% endif %}

  <h2>Targets (first 200)</h2>
  <pre>{{ targets_sample }}</pre>
</body>
</html>
\"\"\")
    targets_sample = ""
    if os.path.exists(targets_path):
        with open(targets_path, "r", encoding="utf-8") as f:
            lines = [x for x in f.read().splitlines() if x.strip()]
            targets_sample = "\\n".join(lines[:200])

    html = html_tmpl.render(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        total_programs=total_programs,
        new_programs=new_programs,
        new_scopes=new_scopes,
        new_programs_count=len(new_programs.index),
        new_scopes_count=len(new_scopes.index),
        targets_count=targets_count,
        targets_sample=targets_sample
    )
    out_path = os.path.join(OUT_DIR, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {out_path}")

if __name__ == "__main__":
    main()
