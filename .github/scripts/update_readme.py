"""Refresh the "Recently Active" section of the profile README.

Lists the most recently pushed public, non-fork repositories for the
profile owner and rewrites the block between the RECENT-REPOS markers.
"""
import json
import os
import re
import urllib.request
from datetime import datetime, timezone

USER = os.environ.get("GH_USER", "KARTHIKEYAN0807")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
LIMIT = 6
START, END = "<!-- RECENT-REPOS:START -->", "<!-- RECENT-REPOS:END -->"


def fetch_repos():
    url = f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed&type=owner"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def build_block(repos):
    picked = [
        r for r in repos
        if not r["fork"] and not r["archived"] and r["name"].lower() != USER.lower()
    ][:LIMIT]
    lines = ["| Project | Language | Last push |", "|---|---|---|"]
    for r in picked:
        desc = (r.get("description") or "").replace("|", "\\|").strip()
        name = f"[{r['name']}]({r['html_url']})" + (f"<br><sub>{desc}</sub>" if desc else "")
        pushed = r["pushed_at"][:10]
        lines.append(f"| {name} | {r.get('language') or '—'} | {pushed} |")
    stamp = datetime.now(timezone.utc).strftime("%d %b %Y")
    lines.append("")
    lines.append(f"<sub>Auto-updated weekly · last refresh {stamp}</sub>")
    return "\n".join(lines)


def main():
    with open("README.md", encoding="utf-8") as f:
        readme = f.read()
    block = build_block(fetch_repos())
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    new = pattern.sub(f"{START}\n{block}\n{END}", readme)
    if new != readme:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(new)


if __name__ == "__main__":
    main()
