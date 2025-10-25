#!/usr/bin/env python3
"""
Meme Scraping Utilities
======================

Shared utilities for meme scraping scripts.
"""

import os
import re
import requests
from typing import List
from dataclasses import dataclass

try:
    import praw  # Reddit API wrapper
except ImportError:
    raise SystemExit("Please `pip install praw requests` before running this script.")

IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".gif", ".webp")
HEADERS = {"User-Agent": os.getenv("REDDIT_USER_AGENT", "meme-scraper/1.0")}

@dataclass
class MemePost:
    id: str
    subreddit: str
    title: str
    url: str
    permalink: str
    ups: int
    num_comments: int
    created_utc: float

def is_image_url(url: str, robust: bool = False, timeout: float = 4.0) -> bool:
    """
    Quick filter: extension check; Optional robust: HEAD request to confirm content-type is image/*.
    """
    if url.lower().endswith(IMAGE_EXTS):
        return True
    if not robust:
        return False
    try:
        r = requests.head(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        ct = r.headers.get("content-type", "").lower()
        return ct.startswith("image/")
    except requests.RequestException:
        return False

def init_reddit():
    cid = os.getenv("REDDIT_CLIENT_ID")
    csecret = os.getenv("REDDIT_CLIENT_SECRET")
    uagent = os.getenv("REDDIT_USER_AGENT", "meme-scraper/1.0")
    if not cid or not csecret:
        raise SystemExit(
            "Missing credentials. Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables."
        )
    return praw.Reddit(client_id=cid, client_secret=csecret, user_agent=uagent)

def fetch_top_day(reddit, sub: str, limit: int) -> List[MemePost]:
    out: List[MemePost] = []
    try:
        for post in reddit.subreddit(sub).top(time_filter="day", limit=limit):
            out.append(
                MemePost(
                    id=post.id,
                    subreddit=sub,
                    title=str(post.title or ""),
                    url=str(post.url or ""),
                    permalink=f"https://www.reddit.com{getattr(post, 'permalink', '')}",
                    ups=int(getattr(post, "score", 0) or 0),
                    num_comments=int(getattr(post, "num_comments", 0) or 0),
                    created_utc=float(getattr(post, "created_utc", 0.0) or 0.0),
                )
            )
    except Exception as e:
        print(f"[warn] failed to fetch r/{sub}: {e}")
    return out

def ensure_dir(p: str):
    from pathlib import Path
    Path(p).mkdir(parents=True, exist_ok=True)

def download_image(url: str, out_dir: str, name_hint: str, timeout: float = 10.0) -> str:
    from pathlib import Path
    ensure_dir(out_dir)
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        # infer extension
        ext = ".jpg"
        filename = url.split("/")[-1].split("?")[0].split("&")[0]
        if "." in filename:
            ext = "." + filename.split(".")[-1]
            if not ext.lower() in IMAGE_EXTS:
                ext = ".jpg"
        safe_name = re.sub(r"[^a-zA-Z0-9._-]", "_", name_hint)[:128]
        fp = Path(out_dir) / f"{safe_name}{ext}"
        with open(fp, "wb") as f:
            f.write(r.content)
        return str(fp)
    except Exception as e:
        print(f"[warn] download failed for {url}: {e}")
        return ""
