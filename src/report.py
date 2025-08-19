import json
import os
from jinja2 import Template
from datetime import datetime

INPUT_FILE = "data/latest/programs.json"
OUTPUT_FILE = "data/report.html"

def main():
    # 1. Load programs
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        programs = json.load(f)

    # 2. Keep only valid dict entries
    programs = [p for p in programs if isinstance(p, dict)]

    # 3. Sort by name (if available)
    programs.sort(key=lambda x: x.get("name", "").lower())

    # 4. HTML template
    html_tmpl = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Bug Bounty Programs</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; background: #f9f9f9; }
    h1 { color: #222; }
    .meta { font-size: 0.9em; color: #555; margin-bottom: 20px; }
    ul { list-style: none; padding: 0; }
    li { background: white; margin: 8px 0; padding: 10px 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    a { color: #0077cc; text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <h1>🌍 Bug Bounty Programs ({{ programs|length }})</h1>
  <div class="meta">Last updated: {{ timestamp }}</div>
  <ul>
  {% for program in programs %}
    <li>
      <strong>{{ program.get("name", "Unknown") }}</strong><br>
      {% if program.get("url") %}
        🔗 <a href="{{ program.get("url") }}" target="_blank">{{ program.get("url") }}</a>
      {% else %}
        ⚠️ No URL
      {% endif %}
    </li>
  {% endfor %}
  </ul>
</body>
</html>
""")

    # 5. Render HTML
    html = html_tmpl.render(
        programs=programs,
        timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    )

    # 6. Save file
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Report saved to {OUTPUT_FILE} with {len(programs)} programs.")

if __name__ == "__main__":
    main()
