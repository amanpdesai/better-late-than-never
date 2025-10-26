"""
MEME DATA SCRAPER
=================

PURPOSE: Track trending memes using Reddit and YouTube Shorts.

DATA SOURCES:
-------------
1. Reddit (PRAW API - Free)
   - Country-specific subreddits
   - Top/Hot posts from last 24 hours

2. YouTube Shorts (YouTube Data API v3)
   - Trending shorts by country
   - Comedy category focus
   - Duration <= 60 seconds or #shorts tag

OUTPUT SCHEMA:
{
  "country": "USA",
  "category": "memes",
  "timestamp": "2025-10-26T00:00:00Z",
  "items": [...],
  "summary": {
    "total_memes": 100,
    "platform_breakdown": {"reddit": 75, "youtube": 25},
    "avg_virality_score": 65.5,
    "top_subreddits": [...],
    "top_channels": [...]
  }
}

REQUIRED:
- pip install praw google-api-python-client requests
- Environment variables: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, YT_API_KEY

REFRESH: Every 6 hours
"""

import os
import json
import argparse
from datetime import datetime
from typing import Dict, Any, List
from collections import Counter

# Load environment variables from .env file
from load_env import load_env
load_env()

from meme_utils import (
    fetch_reddit_memes,
    fetch_youtube_shorts,
    calculate_virality_score,
    analyze_sentiment,
    MemePost,
    COUNTRY_SUBREDDITS,
    YOUTUBE_REGIONS
)


# Supported countries
SUPPORTED_COUNTRIES = ['USA', 'UK', 'Australia', 'India', 'Canada']


class MemeScraper:
    """Scrapes memes from Reddit and YouTube Shorts."""

    def __init__(self):
        self.memes = []

    def scrape_country(self, country: str, reddit_limit: int = 10, youtube_limit: int = 20) -> Dict[str, Any]:
        """
        Scrape memes for a specific country.

        Args:
            country: Country name (USA, UK, Australia, India, Canada)
            reddit_limit: Number of posts per subreddit
            youtube_limit: Max YouTube Shorts to fetch

        Returns:
            Dictionary with meme data
        """
        print(f"\n{'='*60}")
        print(f"Starting meme scraping for {country}")
        print(f"{'='*60}\n")

        if country not in SUPPORTED_COUNTRIES:
            raise ValueError(f"Country '{country}' not supported. Supported: {SUPPORTED_COUNTRIES}")

        all_memes = []
        platform_counts = {'reddit': 0, 'youtube': 0}

        # 1. Fetch Reddit memes
        try:
            print("=" * 40)
            print("FETCHING REDDIT MEMES")
            print("=" * 40)
            reddit_memes = fetch_reddit_memes(country, limit_per_sub=reddit_limit)
            all_memes.extend(reddit_memes)
            platform_counts['reddit'] = len(reddit_memes)
            print(f"✓ Fetched {len(reddit_memes)} Reddit memes\n")
        except Exception as e:
            print(f"✗ Error fetching Reddit memes: {e}\n")

        # 2. Fetch YouTube Shorts
        try:
            print("=" * 40)
            print("FETCHING YOUTUBE SHORTS")
            print("=" * 40)
            youtube_shorts = fetch_youtube_shorts(country, max_results=youtube_limit)
            all_memes.extend(youtube_shorts)
            platform_counts['youtube'] = len(youtube_shorts)
            print(f"✓ Fetched {len(youtube_shorts)} YouTube Shorts\n")
        except Exception as e:
            print(f"✗ Error fetching YouTube Shorts: {e}\n")

        # 3. Process memes and calculate metrics
        processed_items = []
        sentiments = []
        virality_scores = []
        subreddit_counts = Counter()
        channel_counts = Counter()

        for meme in all_memes:
            # Calculate virality score
            virality = calculate_virality_score(meme)
            virality_scores.append(virality)

            # Analyze sentiment
            sentiment = analyze_sentiment(meme.title)
            sentiments.append(sentiment)

            # Track sources
            if meme.platform == 'reddit' and meme.subreddit:
                subreddit_counts[meme.subreddit] += 1
            elif meme.platform == 'youtube' and meme.channel:
                channel_counts[meme.channel] += 1

            # Build item
            item = {
                'id': meme.id,
                'title': meme.title,
                'content': meme.title,  # Use title as content for memes
                'source_platform': meme.platform,
                'source_name': meme.subreddit or meme.channel or 'Unknown',
                'source_url': meme.url,
                'permalink': meme.permalink,
                'created_at': meme.created_at or datetime.utcnow().isoformat() + 'Z',
                'engagement': {
                    'likes': meme.upvotes or meme.likes or 0,
                    'comments': meme.comments or 0,
                    'shares': 0,  # Not available
                    'views': meme.views or 0
                },
                'sentiment': sentiment,
                'virality_score': round(virality, 2),
                'media': {
                    'thumbnail': meme.thumbnail,
                    'images': [meme.url] if not meme.is_video and meme.url else [],
                    'videos': [meme.url] if meme.is_video else []
                },
                'tags': meme.tags or [],
                'is_video': meme.is_video
            }

            processed_items.append(item)

        # 4. Generate summary
        sentiment_counts = Counter(sentiments)

        # Overall sentiment
        if sentiment_counts.get('positive', 0) > len(sentiments) * 0.5:
            overall_sentiment = 'positive'
        elif sentiment_counts.get('negative', 0) > len(sentiments) * 0.4:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'mixed'

        summary = {
            'total_memes': len(processed_items),
            'platform_breakdown': platform_counts,
            'overall_sentiment': overall_sentiment,
            'sentiment_breakdown': dict(sentiment_counts),
            'top_subreddits': [sub for sub, count in subreddit_counts.most_common(10)],
            'top_channels': [ch for ch, count in channel_counts.most_common(10)],
            'avg_virality_score': round(sum(virality_scores) / len(virality_scores), 2) if virality_scores else 0,
            'video_count': sum(1 for item in processed_items if item['is_video']),
            'image_count': sum(1 for item in processed_items if not item['is_video'])
        }

        # Build final result
        result = {
            'country': country,
            'category': 'memes',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'last_updated': datetime.utcnow().isoformat() + 'Z',
            'items': processed_items,
            'summary': summary
        }

        print(f"\n{'='*60}")
        print(f"Scraping completed for {country}")
        print(f"Total memes: {len(processed_items)}")
        print(f"Reddit: {platform_counts['reddit']}, YouTube: {platform_counts['youtube']}")
        print(f"Overall sentiment: {overall_sentiment}")
        print(f"Avg virality: {summary['avg_virality_score']}")
        print(f"{'='*60}\n")

        return result


def scrape_meme_data(country: str, reddit_limit: int = 10, youtube_limit: int = 20) -> Dict[str, Any]:
    """
    Main function to scrape meme data for a country.

    Args:
        country: Country name
        reddit_limit: Posts per subreddit
        youtube_limit: Max YouTube Shorts

    Returns:
        Dictionary with meme data
    """
    scraper = MemeScraper()
    return scraper.scrape_country(country, reddit_limit, youtube_limit)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape meme data from Reddit and YouTube')
    parser.add_argument('--country', type=str, required=True,
                       help=f'Country to scrape. Options: {SUPPORTED_COUNTRIES}')
    parser.add_argument('--output', type=str, default='../output/',
                       help='Output directory path')
    parser.add_argument('--reddit-limit', type=int, default=10,
                       help='Number of posts per subreddit (default: 10)')
    parser.add_argument('--youtube-limit', type=int, default=20,
                       help='Max YouTube Shorts to fetch (default: 20)')
    args = parser.parse_args()

    try:
        # Scrape data
        data = scrape_meme_data(
            args.country,
            reddit_limit=args.reddit_limit,
            youtube_limit=args.youtube_limit
        )

        # Save to output directory
        output_dir = os.path.join(args.output, args.country)
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, f"{datetime.now().strftime('%Y-%m-%d')}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\nMeme data saved to: {output_file}")
        print(f"Total memes: {data['summary']['total_memes']}")
        print(f"Reddit: {data['summary']['platform_breakdown']['reddit']}")
        print(f"YouTube: {data['summary']['platform_breakdown']['youtube']}")
        print(f"Overall sentiment: {data['summary']['overall_sentiment']}")
        print(f"Avg virality score: {data['summary']['avg_virality_score']}")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
