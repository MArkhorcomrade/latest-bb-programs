
# src/notify_slack.py
import os, json, requests, pandas as pd

WEBHOOK = os.getenv("SLACK_WEBHOOK")
OUT_DIR = "out"

def maybe_load_csv(path):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return pd.read_csv(path)
    return pd.DataFrame()

def main():
    if not WEBHOOK:
        print("No SLACK_WEBHOOK provided; skipping.")
        return

    np = maybe_load_csv(os.path.join(OUT_DIR, "new_programs.csv"))
    ns = maybe_load_csv(os.path.join(OUT_DIR, "new_scopes.csv"))
    text = f"Latest Programs: {len(np)} new programs, {len(ns)} new scope items."

    blocks = [
        {"type":"section","text":{"type":"mrkdwn","text": "*Latest Bug Bounty Programs*"}},
        {"type":"section","text":{"type":"mrkdwn","text": f"*New programs:* {len(np)}"}},
        {"type":"section","text":{"type":"mrkdwn","text": f"*New scope entries:* {len(ns)}"}},
        {"type":"context","elements":[{"type":"mrkdwn","text":"Report attached as artifact in GitHub Actions."}]}
    ]
    try:
        r = requests.post(WEBHOOK, json={"text": text, "blocks": blocks}, timeout=10)
        print("Slack status:", r.status_code, r.text[:200])
    except Exception as e:
        print("Slack error:", e)

if __name__ == "__main__":
    main()
