import json, os
from jinja2 import Template

LATEST = "data/latest/programs.json"
REPORT = "data/report.html"

def main():
    if not os.path.exists(LATEST):
        raise FileNotFoundError(f"{LATEST} not found, run build_targets.py first")

    with open(LATEST, "r", encoding="utf-8") as f:
        programs = json.load(f)

    # Simple HTML template
    html_tmpl = Template("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Bug Bounty Programs Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
            th { background: #f4f4f4; }
        </style>
    </head>
    <body>
        <h1>Bug Bounty Programs ({{ programs|length }})</h1>
        <table>
            <tr>
                <th>Name</th>
                <th>URL</th>
                <th>Platform</th>
            </tr>
            {% for p in programs %}
            <tr>
                <td>{{ p.get("name", "N/A") }}</td>
                <td><a href="{{ p.get("url", "#") }}">{{ p.get("url", "N/A") }}</a></td>
                <td>{{ p.get("platform", "N/A") }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """)

    html = html_tmpl.render(programs=programs)

    with open(REPORT, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Report saved to {REPORT}")

if __name__ == "__main__":
    main()
