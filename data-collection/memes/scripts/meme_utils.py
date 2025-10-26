"""
MEME SCRAPING UTILITIES
=======================

Shared utilities for meme scraping from Reddit and YouTube Shorts.
"""

import os
import re
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    import praw  # Reddit API wrapper
except ImportError:
    praw = None

# Country-specific subreddit configurations
COUNTRY_SUBREDDITS = {
    'USA': [
        'memes', 'dankmemes', 'funny', 'AdviceAnimals', 'PoliticalHumor',
        'meirl', 'me_irl', 'wholesomememes', 'comedyheaven', 'starterpacks'
    ],
    'UK': [
        'CasualUK', 'BritishMemes', 'britishproblems', 'memes', 'dankmemes',
        'funny', 'AdviceAnimals', 'meirl', 'wholesomememes', 'starterpacks'
    ],
    'Australia': [
        'straya', 'AusMemes', 'australia', 'memes', 'dankmemes',
        'funny', 'AdviceAnimals', 'meirl', 'wholesomememes', 'starterpacks'
    ],
    'India': [
        'IndianDankMemes', 'IndiaMeme', 'IndianMeyMeys', 'bakchodi', 'memes',
        'dankmemes', 'funny', 'AdviceAnimals', 'meirl', 'wholesomememes'
    ],
    'Canada': [
        'canada', 'CanadianMemes', 'memes', 'dankmemes', 'funny',
        'AdviceAnimals', 'meirl', 'wholesomememes', 'starterpacks', 'hockey'
    ]
}

# YouTube region codes
YOUTUBE_REGIONS = {
    'USA': 'US',
    'UK': 'GB',
    'Australia': 'AU',
    'India': 'IN',
    'Canada': 'CA'
}

IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".gif", ".webp")
HEADERS = {"User-Agent": os.getenv("REDDIT_USER_AGENT", "meme-scraper/1.0")}


@dataclass
class MemePost:
    """Data class for meme posts from any platform."""
    id: str
    title: str
    platform: str  # 'reddit' or 'youtube'
    url: str
    permalink: str
    subreddit: Optional[str] = None  # For Reddit
    channel: Optional[str] = None  # For YouTube
    upvotes: int = 0
    comments: int = 0
    views: int = 0
    likes: int = 0
    created_at: str = ""
    thumbnail: Optional[str] = None
    is_video: bool = False
    tags: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return asdict(self)


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
    """Initialize Reddit API client."""
    if praw is None:
        raise SystemExit(
            "PRAW not installed. Please run: pip install praw"
        )

    cid = os.getenv("REDDIT_CLIENT_ID")
    csecret = os.getenv("REDDIT_CLIENT_SECRET")
    uagent = os.getenv("REDDIT_USER_AGENT", "meme-scraper/1.0")

    if not cid or not csecret:
        raise SystemExit(
            "Missing Reddit credentials. Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables."
        )

    return praw.Reddit(client_id=cid, client_secret=csecret, user_agent=uagent)


def fetch_reddit_memes(country: str, limit_per_sub: int = 5) -> List[MemePost]:
    """
    Fetch top memes from Reddit for a specific country.

    Args:
        country: Country name (USA, UK, Australia, India, Canada)
        limit_per_sub: Number of posts to fetch per subreddit

    Returns:
        List of MemePost objects
    """
    if country not in COUNTRY_SUBREDDITS:
        raise ValueError(f"Country '{country}' not supported. Supported: {list(COUNTRY_SUBREDDITS.keys())}")

    reddit = init_reddit()
    memes = []
    subreddits = COUNTRY_SUBREDDITS[country]

    print(f"Fetching Reddit memes from {len(subreddits)} subreddits for {country}...")

    for sub in subreddits:
        try:
            for post in reddit.subreddit(sub).hot(limit=limit_per_sub):
                # Skip stickied posts and non-meme content
                if post.stickied:
                    continue

                # Determine if it's an image or video
                url = str(post.url or "")
                is_video = any(x in url.lower() for x in ['v.redd.it', 'youtube.com', 'youtu.be', 'gfycat', 'imgur.com/a/'])

                # Get thumbnail
                thumbnail = None
                if hasattr(post, 'thumbnail') and post.thumbnail and post.thumbnail.startswith('http'):
                    thumbnail = post.thumbnail
                elif hasattr(post, 'preview') and post.preview:
                    try:
                        thumbnail = post.preview['images'][0]['source']['url']
                    except (KeyError, IndexError):
                        pass

                meme = MemePost(
                    id=f"reddit_{post.id}",
                    title=str(post.title or ""),
                    platform='reddit',
                    url=url,
                    permalink=f"https://www.reddit.com{getattr(post, 'permalink', '')}",
                    subreddit=sub,
                    upvotes=int(getattr(post, "score", 0) or 0),
                    comments=int(getattr(post, "num_comments", 0) or 0),
                    created_at=datetime.fromtimestamp(float(getattr(post, "created_utc", 0.0) or 0.0)).isoformat() + 'Z',
                    thumbnail=thumbnail,
                    is_video=is_video,
                    tags=[]
                )
                memes.append(meme)

        except Exception as e:
            print(f"[Warning] Failed to fetch r/{sub}: {e}")
            continue

    print(f"Successfully fetched {len(memes)} Reddit memes for {country}")
    return memes


def fetch_youtube_shorts(country: str, max_results: int = 50) -> List[MemePost]:
    """
    Fetch trending YouTube Shorts for a specific country.

    Args:
        country: Country name (USA, UK, Australia, India, Canada)
        max_results: Maximum number of shorts to fetch

    Returns:
        List of MemePost objects
    """
    if country not in YOUTUBE_REGIONS:
        raise ValueError(f"Country '{country}' not supported. Supported: {list(YOUTUBE_REGIONS.keys())}")

    api_key = os.getenv("YT_API_KEY")
    if not api_key:
        print("[Warning] YT_API_KEY not set, skipping YouTube Shorts")
        return []

    region = YOUTUBE_REGIONS[country]
    print(f"Fetching YouTube Shorts for {country} (region: {region})...")

    try:
        import requests

        # Fetch trending videos
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "key": api_key,
            "part": "snippet,contentDetails,statistics",
            "chart": "mostPopular",
            "regionCode": region,
            "maxResults": 50,  # API limit per page
            "videoCategoryId": "23"  # Comedy category for meme-like content
        }

        response = requests.get(url, params=params, timeout=20)
        if response.status_code != 200:
            print(f"[Warning] YouTube API error {response.status_code}: {response.text}")
            return []

        data = response.json()
        items = data.get("items", [])

        shorts = []
        for item in items:
            try:
                vid = item.get("id")
                snippet = item.get("snippet", {})
                stats = item.get("statistics", {})
                content = item.get("contentDetails", {})

                # Parse duration
                duration_iso = content.get("duration", "PT0S")
                duration_sec = parse_iso8601_duration(duration_iso)

                # Check if it's a Short (<=60 seconds or has #shorts tag)
                title = snippet.get("title", "") or ""
                desc = snippet.get("description", "") or ""
                is_shorts_tagged = ("#shorts" in title.lower()) or ("#shorts" in desc.lower())

                if duration_sec > 60 and not is_shorts_tagged:
                    continue  # Skip non-shorts

                # Extract tags
                tags = snippet.get("tags", []) or []

                # Get thumbnail
                thumbnails = snippet.get("thumbnails", {})
                thumbnail = (
                    thumbnails.get("high", {}).get("url") or
                    thumbnails.get("medium", {}).get("url") or
                    thumbnails.get("default", {}).get("url")
                )

                # Parse published date
                published_at = snippet.get("publishedAt", "")

                short = MemePost(
                    id=f"youtube_{vid}",
                    title=title,
                    platform='youtube',
                    url=f"https://www.youtube.com/watch?v={vid}",
                    permalink=f"https://www.youtube.com/shorts/{vid}",
                    channel=snippet.get("channelTitle"),
                    views=int(stats.get("viewCount", 0) or 0),
                    likes=int(stats.get("likeCount", 0) or 0),
                    comments=int(stats.get("commentCount", 0) or 0),
                    created_at=published_at,
                    thumbnail=thumbnail,
                    is_video=True,
                    tags=tags
                )
                shorts.append(short)

                if len(shorts) >= max_results:
                    break

            except Exception as e:
                print(f"[Warning] Failed to parse YouTube video: {e}")
                continue

        print(f"Successfully fetched {len(shorts)} YouTube Shorts for {country}")
        return shorts

    except Exception as e:
        print(f"[Error] Failed to fetch YouTube Shorts: {e}")
        return []


def parse_iso8601_duration(iso_dur: str) -> int:
    """
    Convert YouTube's ISO8601 duration (e.g., PT1M5S) to total seconds.
    """
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


def calculate_virality_score(meme: MemePost) -> float:
    """
    Calculate a virality score (0-100) based on engagement metrics.

    Formula combines:
    - Upvotes/Likes
    - Comments
    - Views (for YouTube)
    """
    if meme.platform == 'reddit':
        # Reddit scoring: upvotes + comments weight
        upvotes = meme.upvotes or 0
        comments = meme.comments or 0

        # Logarithmic scale for upvotes (0-10k -> 0-80 points)
        upvote_score = min(80, (upvotes / 10000) * 80)

        # Comments add bonus (0-500 -> 0-20 points)
        comment_score = min(20, (comments / 500) * 20)

        return min(100, upvote_score + comment_score)

    elif meme.platform == 'youtube':
        # YouTube scoring: views + likes + comments
        views = meme.views or 0
        likes = meme.likes or 0
        comments = meme.comments or 0

        # Logarithmic scale for views (0-1M -> 0-60 points)
        view_score = min(60, (views / 1000000) * 60)

        # Likes (0-10k -> 0-25 points)
        like_score = min(25, (likes / 10000) * 25)

        # Comments (0-1k -> 0-15 points)
        comment_score = min(15, (comments / 1000) * 15)

        return min(100, view_score + like_score + comment_score)

    return 50.0  # Default


def analyze_sentiment(text: str) -> str:
    """
    Basic sentiment analysis using keyword matching.
    Memes are typically humorous, so we focus on tone.
    """
    text_lower = text.lower()

    # Positive/funny keywords
    positive_words = [
        'lol', 'lmao', 'funny', 'hilarious', 'wholesome', 'blessed', 'mood',
        'relatable', 'epic', 'legend', 'king', 'queen', 'vibes', 'based',
        'win', 'perfect', 'amazing', 'love', 'best', 'good', 'happy', 'joy'
    ]

    # Negative/dark humor keywords
    negative_words = [
        'cringe', 'cursed', 'yikes', 'oof', 'sad', 'pain', 'suffering',
        'depression', 'anxiety', 'crisis', 'fail', 'worst', 'hate', 'angry',
        'rage', 'toxic', 'trash', 'awful', 'terrible', 'horrible'
    ]

    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)

    if negative_count > positive_count:
        return 'negative'
    elif positive_count > negative_count:
        return 'positive'
    else:
        return 'neutral'
