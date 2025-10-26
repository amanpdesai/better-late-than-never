import os
import json
import time
import math
import requests
import pandas as pd
from datetime import datetime, timezone
from dateutil import parser as dateparser

API_KEY = os.getenv("YT_API_KEY")
if not API_KEY:
    raise SystemExit("Missing env var YT_API_KEY. Set it with: export YT_API_KEY=YOUR_KEY")

YOUTUBE_API = "https://www.googleapis.com/youtube/v3/videos"

# ---- Config ----
REGION = "US"
MAX_RESULTS_PER_PAGE = 50          # API max
TARGET_RESULTS = 250               # change to 100/150 if you want more
OUTPUT_CSV = "us_trending_shorts.csv"
OUTPUT_JSON = "us_trending_shorts.json"
REQUEST_TIMEOUT = 20
SLEEP_BETWEEN_PAGES_SEC = 0.4      # be polite to API

def parse_iso8601_duration_to_seconds(iso_dur: str) -> int:
    """
    Convert YouTube's ISO8601 duration (e.g., PT1M5S) to total seconds.
    """
    # Very small parser (no hours for Shorts, but we handle them anyway).
    # PT#H#M#S with each component optional.
    hours = minutes = seconds = 0
    if not iso_dur or not iso_dur.startswith("PT"):
        return 0
    num = ""
    for ch in iso_dur[2:]:
        if ch.isdigit():
            num += ch
        else:
            if ch == "H":
                hours = int(num or 0)
            elif ch == "M":
                minutes = int(num or 0)
            elif ch == "S":
                seconds = int(num or 0)
            num = ""
    return hours * 3600 + minutes * 60 + seconds

def fetch_trending_page(page_token=None):
    params = {
        "key": API_KEY,
        "part": "snippet,contentDetails,statistics",
        "chart": "mostPopular",
        "regionCode": REGION,
        "maxResults": MAX_RESULTS_PER_PAGE,
    }
    if page_token:
        params["pageToken"] = page_token

    r = requests.get(YOUTUBE_API, params=params, timeout=REQUEST_TIMEOUT)
    if r.status_code != 200:
        raise RuntimeError(f"API error {r.status_code}: {r.text}")
    return r.json()

def normalize_item(v):
    vid = v.get("id")
    sn = v.get("snippet", {})
    st = v.get("statistics", {})
    cd = v.get("contentDetails", {})

    duration_iso = cd.get("duration", "PT0S")
    duration_sec = parse_iso8601_duration_to_seconds(duration_iso)

    # Shorts heuristic:
    # 1) True duration ≤ 60 seconds (primary)
    # 2) OR title/description include "#shorts" (fallback)
    title = sn.get("title", "") or ""
    desc = sn.get("description", "") or ""
    is_shorts_tagged = ("#shorts" in title.lower()) or ("#shorts" in desc.lower())
    is_short = duration_sec <= 60 or is_shorts_tagged

    reason = []
    if duration_sec <= 60:
        reason.append("duration<=60s")
    if is_shorts_tagged:
        reason.append("#shorts-tagged")

    # safe parse counts
    def to_int(x):
        try:
            return int(x)
        except Exception:
            return None

    published_at = sn.get("publishedAt")
    try:
        published_dt = dateparser.parse(published_at).astimezone(timezone.utc).isoformat()
    except Exception:
        published_dt = published_at

    return {
        "videoId": vid,
        "url": f"https://www.youtube.com/watch?v={vid}" if vid else None,
        "title": title,
        "channelTitle": sn.get("channelTitle"),
        "publishedAt": published_dt,
        "duration": duration_iso,
        "durationSec": duration_sec,
        "isShort": is_short,
        "shortReason": ",".join(reason) if reason else "",
        "viewCount": to_int(st.get("viewCount")),
        "likeCount": to_int(st.get("likeCount")),      # may be None if hidden
        "commentCount": to_int(st.get("commentCount")),
        "tags": ",".join(sn.get("tags", [])) if sn.get("tags") else "",
        "description": desc,
        "region": REGION,
        "thumbnails_default": sn.get("thumbnails", {}).get("default", {}).get("url"),
        "thumbnails_medium": sn.get("thumbnails", {}).get("medium", {}).get("url"),
        "thumbnails_high": sn.get("thumbnails", {}).get("high", {}).get("url"),
    }

def main():
    print(f"Fetching up to {TARGET_RESULTS} trending videos for region {REGION}…")
    collected = []
    page_token = None

    while len(collected) < TARGET_RESULTS:
        data = fetch_trending_page(page_token)
        items = data.get("items", [])
        for v in items:
            collected.append(v)
            if len(collected) >= TARGET_RESULTS:
                break

        page_token = data.get("nextPageToken")
        if not page_token or len(collected) >= TARGET_RESULTS:
            break
        time.sleep(SLEEP_BETWEEN_PAGES_SEC)

    print(f"Fetched {len(collected)} total trending videos. Filtering for Shorts (<=60s or #shorts)…")
    rows = [normalize_item(v) for v in collected]
    shorts_only = [r for r in rows if r["isShort"]]

    # If trending has fewer than TARGET_RESULTS Shorts, just return what we have.
    print(f"Found {len(shorts_only)} Shorts.")

    # Sort by viewCount desc (when available)
    shorts_only.sort(key=lambda x: (x["viewCount"] is not None, x["viewCount"]), reverse=True)

    df = pd.DataFrame(shorts_only)
    df.to_csv(OUTPUT_CSV, index=False)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(shorts_only, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(shorts_only)} rows to {OUTPUT_CSV} and {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
