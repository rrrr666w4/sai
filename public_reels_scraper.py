#!/usr/bin/env python3
"""
Instagram Public Reels Downloader (NO LOGIN / NO SESSION)
- Reads usernames from usernames.txt
- Downloads recent reels from each PUBLIC profile using yt-dlp
- Saves videos into scraped_reels/videos/<username>/
- Saves metadata into scraped_reels/reels_metadata.json
- Skips usernames that fail (private account / blocked / login wall)

Limitations (read SETUP_GUIDE.md):
- Only works for public accounts
- Instagram frequently rate-limits/blocks unauthenticated requests,
  especially from datacenter IPs like GitHub Actions runners
- No guarantee of consistent success run to run
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path("scraped_reels")
VIDEOS_DIR = BASE_DIR / "videos"
METADATA_FILE = BASE_DIR / "reels_metadata.json"
USERNAMES_FILE = Path("usernames.txt")

MAX_REELS_PER_USER = 5  # per username, per run

VIDEOS_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path: Path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return default
    return default


def save_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def read_usernames() -> list:
    if not USERNAMES_FILE.exists():
        print(f"❌ {USERNAMES_FILE} nahi mili. Ek username per line likh kar banao.")
        sys.exit(1)
    lines = USERNAMES_FILE.read_text(encoding="utf-8").splitlines()
    return [u.strip().lstrip("@") for u in lines if u.strip() and not u.strip().startswith("#")]


def download_user_reels(username: str, metadata: list, known_ids: set) -> int:
    user_dir = VIDEOS_DIR / username
    user_dir.mkdir(parents=True, exist_ok=True)

    profile_url = f"https://www.instagram.com/{username}/reels/"

    cmd = [
        "yt-dlp",
        "--playlist-end", str(MAX_REELS_PER_USER),
        "--print", "%(id)s|||%(webpage_url)s|||%(description)s|||%(like_count)s|||%(view_count)s|||%(timestamp)s",
        "-o", str(user_dir / "%(id)s.%(ext)s"),
        profile_url,
    ]

    print(f"🔍 @{username} ki public reels try kar rahe hain...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    if result.returncode != 0:
        print(f"⚠️ @{username} fail ho gaya (private / blocked / login-wall). Skip kar rahe hain.")
        print(f"   Detail: {result.stderr.strip()[:200]}")
        return 0

    new_count = 0
    for line in result.stdout.strip().splitlines():
        parts = line.split("|||")
        if len(parts) != 6:
            continue
        reel_id, url, desc, likes, views, ts = parts
        if reel_id in known_ids:
            continue

        metadata.append({
            "reel_id": reel_id,
            "url": url,
            "username": username,
            "caption": desc,
            "like_count": likes if likes != "NA" else None,
            "view_count": views if views != "NA" else None,
            "timestamp": ts if ts != "NA" else None,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        })
        known_ids.add(reel_id)
        new_count += 1

    print(f"✅ @{username}: {new_count} naye reels save hue")
    return new_count


def main():
    usernames = read_usernames()
    metadata = load_json(METADATA_FILE, [])
    known_ids = {m["reel_id"] for m in metadata}

    total_new = 0
    for username in usernames:
        total_new += download_user_reels(username, metadata, known_ids)
        save_json(METADATA_FILE, metadata)  # save progressively in case later usernames fail

    print(f"\n📊 Total naye reels is run mein: {total_new}")


if __name__ == "__main__":
    main()
