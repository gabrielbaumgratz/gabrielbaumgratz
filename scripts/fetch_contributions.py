#!/usr/bin/env python3
"""
Scrapes GitHub's public contribution calendar markup without any authentication
and writes data/contributions.json.
"""
import os
import re
import sys
import json
import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_PROFILE_USER", "gabrielbaumgratz")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")

def main():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    resp = requests.get(URL, headers=headers, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        print("Calendar cells not found in public HTML markup.", file=sys.stderr)
        sys.exit(1)

    days = []
    for td in cells:
        date = td.get("data-date")
        if not date:
            continue
        td_id = td.get("id")
        tooltip = soup.find("tool-tip", attrs={"for": td_id}) if td_id else None
        text = tooltip.get_text(strip=True) if tooltip else ""
        if re.search(r"no contributions", text, re.I):
            count = 0
        else:
            m = re.match(r"(\d+)", text)
            count = int(m.group(1)) if m else 0
        
        try:
            level = int(td.get("data-level", 0))
        except (ValueError, TypeError):
            level = 0

        days.append({"date": date, "count": count, "level": level})

    days.sort(key=lambda d: d["date"])
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "username": USERNAME,
            "days": days,
            "total": sum(d["count"] for d in days)
        }, f, indent=2)

    print(f"Scraped {len(days)} days successfully for user {USERNAME}.")

if __name__ == "__main__":
    main()
