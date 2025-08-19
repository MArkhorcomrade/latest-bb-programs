
# Latest Bug Bounty Programs — Daily @ 06:00 PKT

This repo fetches the **latest public bug bounty program scopes** from `arkadiyt/bounty-targets-data`, saves a daily snapshot, diffs against yesterday to find **new programs** and **new in-scope assets**, and generates a simple **HTML report**. It runs daily at **06:00 Asia/Karachi** via GitHub Actions (cron in UTC: **01:00**).

### What you get
- `data/snapshots/YYYY-MM-DD.json` — daily raw snapshot of `programs.json`
- `data/latest/programs.json` — a copy of today's snapshot
- `out/new_programs.csv` — programs that are *new today*
- `out/new_scopes.csv` — scope entries that are *new today*
- `out/targets.txt` — domains & hosts extracted from scope
- `out/index.html` — clean HTML report (uploaded as workflow artifact)

### Quick start
1. **Create a new GitHub repo** (empty).
2. Download and unzip this project locally, then push, or upload via GitHub UI.
3. In the repo, go to **Actions** and enable workflows if prompted.
4. It will run daily at **06:00 PKT** (01:00 UTC). You can also run it manually from Actions → "Daily Latest Programs".
5. Download artifacts from each run (contains the `out/` folder with the report).

> Optional: add a Slack Incoming Webhook URL as a repo secret `SLACK_WEBHOOK` to receive a daily summary message.

### Legal
This pipeline only downloads *public program directories* and does not scan any targets. If you later add recon/scanning, ensure you only test assets **explicitly in scope** and follow each program’s policy.
