#!/usr/bin/env python3
"""
UK Meme Scraper (Last 24 Hours)
===============================

Scrapes UK-specific memes from UK subreddits and global meme subreddits with UK keywords.
"""

import re
import csv
import time
import argparse
from dataclasses import asdict
from meme_utils import (
    MemePost, is_image_url, init_reddit, fetch_top_day, 
    download_image, ensure_dir
)

# UK-specific subreddits
UK_SUBREDDITS = [
    "ukmemes",
    "greatbritishmemes", 
    "CasualUK",
    "UnitedKingdom",
    "AskUK",
    "britishproblems",
    "okmatewanker",
    "ScottishPeopleTwitter",
    "Wales",
    "NorthernIreland"
]

# Global meme subreddits (filtered for UK keywords)
MEME_SUBREDDITS = [
    "memes",
    "dankmemes",
    "wholesomememes",
    "funny",
    "PrequelMemes",
    "HistoryMemes",
    "ProgrammerHumor"
]

# UK keywords for filtering global meme subreddits
UK_KEYWORDS = re.compile(
    r"""(?ix)
    \b(uk|u\.k\.|britain|british|england|english|scotland|scottish|wales|welsh|
       northern\s+ireland|ni\b|london|manchester|birmingham|leeds|liverpool|
       edinburgh|glasgow|cardiff|belfast|oxford|cambridge|sheffield|newcastle|
       bristol|nottingham|leicester|coventry|brighton|portsmouth|southampton|
       brexit|tories|labour|downing\s+street|sunak|keir\s+starmer|ofcom|nhs|
       tea|queen|king|prince|princess|royal|buckingham|westminster|parliament|
       fish\s+and\s+chips|bangers\s+and\s+mash|yorkshire\s+pudding|sunday\s+roast|
       pub|pint|ale|stella|carling|fosters|guinness|whisky|scotch|gin)\b
    """
)

def main():
    ap = argparse.ArgumentParser(description="Pull top UK memes from last 24 hours.")
    ap.add_argument("--limit-per-sub", type=int, default=100, help="Max posts per subreddit (default: 100)")
    ap.add_argument("--out", type=str, default="uk_memes_last_24h.csv", help="Output CSV path")
    ap.add_argument("--download-images", action="store_true", help="If set, download images to ./uk_meme_images")
    ap.add_argument("--robust-image-check", action="store_true", help="Use HEAD requests to confirm image content-type")
    ap.add_argument("--strict-uk", action="store_true", help="Only include UK-centric subreddits; ignore keyword matches from global meme subs")
    ap.add_argument("--debug-filtering", action="store_true", help="Show detailed filtering debug info")
    args = ap.parse_args()

    reddit = init_reddit()

    # 1) Always fetch from UK-centric subs
    subs_to_fetch = list(UK_SUBREDDITS)

    # 2) Optionally fetch global meme subs as well (we'll filter by UK keywords)
    if not args.strict_uk:
        subs_to_fetch += MEME_SUBREDDITS

    print(f"[info] fetching top(day) from: {', '.join(subs_to_fetch)}")
    all_posts: List[MemePost] = []
    subreddit_counts = {}
    
    for sub in subs_to_fetch:
        posts = fetch_top_day(reddit, sub, limit=args.limit_per_sub)
        all_posts.extend(posts)
        subreddit_counts[sub] = len(posts)
        print(f"[debug] r/{sub}: {len(posts)} posts fetched")
        time.sleep(0.2)

    print(f"[info] fetched {len(all_posts)} posts (pre-filter)")

    # Filter to images and (if from global meme subs) UK keyword matched titles
    filtered: List[MemePost] = []
    image_count = 0
    uk_keyword_count = 0
    uk_subreddit_count = 0
    
    for p in all_posts:
        if not is_image_url(p.url, robust=args.robust_image_check):
            continue
        image_count += 1
        
        if p.subreddit in UK_SUBREDDITS:
            filtered.append(p)
            uk_subreddit_count += 1
        else:
            # For global meme subs, require UK keyword in title
            if UK_KEYWORDS.search(p.title):
                filtered.append(p)
                uk_keyword_count += 1
    
    print(f"[debug] {image_count} posts were images")
    print(f"[debug] {uk_subreddit_count} posts from UK subreddits")
    print(f"[debug] {uk_keyword_count} posts from global subs with UK keywords")
    
    # Show breakdown by subreddit
    filtered_by_sub = {}
    for p in filtered:
        filtered_by_sub[p.subreddit] = filtered_by_sub.get(p.subreddit, 0) + 1
    
    print(f"[debug] Final results by subreddit:")
    for sub, count in sorted(filtered_by_sub.items()):
        print(f"[debug]   r/{sub}: {count} posts")

    print(f"[info] {len(filtered)} posts after UK + image filtering")

    # Sort by upvotes desc, then comments desc
    filtered.sort(key=lambda x: (x.ups, x.num_comments), reverse=True)

    # Save CSV
    fieldnames = list(asdict(filtered[0]).keys()) if filtered else [
        "id","subreddit","title","url","permalink","ups","num_comments","created_utc"
    ]
    out_csv = args.out
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for p in filtered:
            w.writerow(asdict(p))

    print(f"[ok] wrote {len(filtered)} rows to {out_csv}")

    # Optionally download images
    if args.download_images and filtered:
        out_dir = "uk_meme_images"
        for p in filtered:
            name_hint = f"{p.subreddit}_{p.id}"
            saved = download_image(p.url, out_dir, name_hint=name_hint)
            if saved:
                print(f"[img] saved {saved}")

if __name__ == "__main__":
    main()
