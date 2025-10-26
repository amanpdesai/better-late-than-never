#!/usr/bin/env python3
"""
General Meme Scraper (Last 24 Hours)
====================================

Scrapes memes from popular meme subreddits and saves them with metadata.
"""

import csv
import time
import argparse
from dataclasses import asdict
from meme_utils import (
    MemePost, is_image_url, init_reddit, fetch_top_day, 
    download_image, ensure_dir
)

# Popular meme subreddits
MEME_SUBREDDITS = [
    "memes",
    "dankmemes", 
    "wholesomememes",
    "funny",
    "PrequelMemes",
    "lotrmemes",
    "HistoryMemes",
    "ProgrammerHumor",
    "terriblefacebookmemes",
    "AdviceAnimals",
    "MemeEconomy",
    "comedyheaven",
    "okbuddyretard",
    "196",
    "me_irl",
    "2meirl4meirl",
    "starterpacks",
    "bonehurtingjuice",
    "antimeme",
    "surrealmemes"
]

def main():
    ap = argparse.ArgumentParser(description="Pull top memes from last 24 hours.")
    ap.add_argument("--limit-per-sub", type=int, default=100, help="Max posts per subreddit (default: 100)")
    ap.add_argument("--out", type=str, default="memes_last_24h.csv", help="Output CSV path")
    ap.add_argument("--download-images", action="store_true", help="If set, download images to ./meme_images")
    ap.add_argument("--robust-image-check", action="store_true", help="Use HEAD requests to confirm image content-type")
    ap.add_argument("--subreddits", nargs="+", default=MEME_SUBREDDITS, help="Subreddits to scrape (default: popular meme subs)")
    args = ap.parse_args()

    reddit = init_reddit()

    print(f"[info] fetching top(day) from: {', '.join(args.subreddits)}")
    all_posts: List[MemePost] = []
    subreddit_counts = {}
    
    for sub in args.subreddits:
        posts = fetch_top_day(reddit, sub, limit=args.limit_per_sub)
        all_posts.extend(posts)
        subreddit_counts[sub] = len(posts)
        print(f"[debug] r/{sub}: {len(posts)} posts fetched")
        time.sleep(0.2)

    print(f"[info] fetched {len(all_posts)} posts (pre-filter)")

    # Filter to images only
    filtered: List[MemePost] = []
    image_count = 0
    
    for p in all_posts:
        if not is_image_url(p.url, robust=args.robust_image_check):
            continue
        image_count += 1
        filtered.append(p)
    
    print(f"[debug] {image_count} posts were images")
    print(f"[info] {len(filtered)} posts after image filtering")

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
        out_dir = "meme_images"
        for p in filtered:
            name_hint = f"{p.subreddit}_{p.id}"
            saved = download_image(p.url, out_dir, name_hint=name_hint)
            if saved:
                print(f"[img] saved {saved}")

if __name__ == "__main__":
    main()
