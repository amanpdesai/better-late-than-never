#!/usr/bin/env python3
"""
US Memes 14-Day Scraper
======================

Quickstart:
1. Set environment variables:
   export REDDIT_CLIENT_ID="your_client_id"
   export REDDIT_CLIENT_SECRET="your_client_secret"
   export REDDIT_USER_AGENT="your_app_name/1.0"

2. Run: python3 us_memes_14d_uslean.py

3. Output files:
   - us_memes_strict.csv (US-focused memes only)
   - us_memes_all.csv (all memes with US scores)
"""

import os
import time
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
from dateutil import parser
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pathlib import Path
import re

# Load environment variables from .env file
load_dotenv()

# Configuration
STRONG_US_SUBREDDITS = ["USMemes", "PoliticalHumor", "nflmemes", "CollegeMemes"]
BROAD_SUBREDDITS = ["memes", "dankmemes", "funny", "me_irl"]
ALL_SUBREDDITS = STRONG_US_SUBREDDITS + BROAD_SUBREDDITS

# US cue tokens for title analysis
US_CUE_TOKENS = {
    "usa", "american", "biden", "trump", "nfl", "thanksgiving", 
    "florida", "california", "new york", "texas"
}

# Image domains and extensions
IMAGE_DOMAINS = {"i.redd.it", "imgur.com"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

# Reddit API configuration
REDDIT_BASE_URL = "https://www.reddit.com"
REDDIT_OAUTH_URL = "https://www.reddit.com/api/v1/access_token"
REDDIT_API_URL = "https://oauth.reddit.com"

class RedditScraper:
    def __init__(self):
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.user_agent = os.getenv("REDDIT_USER_AGENT", "us_memes_scraper/1.0")
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Missing REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET environment variables")
        
        self.access_token = None
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        
        # Image download settings
        self.images_dir = Path("us_memes_images")
        self.images_dir.mkdir(exist_ok=True)
    
    def authenticate(self) -> bool:
        """Authenticate with Reddit OAuth2."""
        print("🔐 Authenticating with Reddit...")
        
        auth_data = {
            "grant_type": "client_credentials"
        }
        
        auth_response = self.session.post(
            REDDIT_OAUTH_URL,
            data=auth_data,
            auth=(self.client_id, self.client_secret),
            timeout=10
        )
        
        if auth_response.status_code == 200:
            token_data = auth_response.json()
            self.access_token = token_data["access_token"]
            self.session.headers.update({
                "Authorization": f"Bearer {self.access_token}"
            })
            print("✅ Authentication successful")
            return True
        else:
            print(f"❌ Authentication failed: {auth_response.status_code}")
            return False
    
    def is_image_content(self, post: Dict[str, Any]) -> bool:
        """Check if post contains image content."""
        url = post.get("url", "").lower()
        domain = post.get("domain", "").lower()
        
        # Check for gallery posts
        if post.get("is_gallery", False):
            return True
        
        # Check for image domains
        if domain in IMAGE_DOMAINS:
            return True
        
        # Check for image extensions
        if any(url.endswith(ext) for ext in IMAGE_EXTENSIONS):
            return True
        
        return False
    
    def calculate_us_score(self, post: Dict[str, Any]) -> int:
        """Calculate US relevance score for a post."""
        score = 0
        
        # +2 if subreddit is in strong US subreddits
        subreddit = post.get("subreddit", "").lower()
        if subreddit in [s.lower() for s in STRONG_US_SUBREDDITS]:
            score += 2
        
        # +1 if posted during US peak hours (16:00-02:00 UTC)
        created_utc = post.get("created_utc", 0)
        if created_utc:
            dt = datetime.fromtimestamp(created_utc, tz=timezone.utc)
            hour = dt.hour
            if hour >= 16 or hour < 2:  # 16:00-02:00 UTC
                score += 1
        
        # +1 if title contains US cue tokens (capped at +1)
        title = post.get("title", "").lower()
        us_tokens_found = sum(1 for token in US_CUE_TOKENS if token in title)
        if us_tokens_found > 0:
            score += 1
        
        return score
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file system usage."""
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Replace spaces with underscores
        filename = re.sub(r'\s+', '_', filename)
        # Limit length
        if len(filename) > 100:
            filename = filename[:100]
        return filename.strip('_')
    
    def download_image(self, url: str, post_id: str, subreddit: str, title: str) -> Optional[str]:
        """Download an image and return the local file path."""
        try:
            # Get file extension from URL
            if url.endswith(('.jpg', '.jpeg')):
                ext = '.jpg'
            elif url.endswith('.png'):
                ext = '.png'
            elif url.endswith('.gif'):
                ext = '.gif'
            elif url.endswith('.webp'):
                ext = '.webp'
            else:
                ext = '.jpg'  # default
            
            # Create filename
            safe_title = self.sanitize_filename(title)[:50]  # Limit title length
            filename = f"{subreddit}_{post_id}_{safe_title}{ext}"
            filepath = self.images_dir / filename
            
            # Skip if already exists
            if filepath.exists():
                return str(filepath)
            
            # Download image
            response = self.session.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Save image
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return str(filepath)
            
        except Exception as e:
            print(f"    ❌ Failed to download {url}: {e}")
            return None
    
    def download_gallery_images(self, post: Dict[str, Any]) -> List[str]:
        """Download images from a gallery post."""
        downloaded_paths = []
        
        try:
            # Get gallery data
            gallery_data = post.get("gallery_data", {}).get("items", [])
            media_metadata = post.get("media_metadata", {})
            
            for item in gallery_data:
                media_id = item.get("media_id")
                if media_id and media_id in media_metadata:
                    media_info = media_metadata[media_id]
                    if media_info.get("status") == "valid":
                        # Get the best quality image URL
                        images = media_info.get("s", {})
                        if images:
                            # Try different quality levels
                            for quality in ["u", "s", "m"]:  # ultra, standard, medium
                                if quality in images:
                                    url = images[quality].get("u", "")
                                    if url:
                                        filepath = self.download_image(
                                            url, 
                                            post.get("id", ""), 
                                            post.get("subreddit", ""), 
                                            post.get("title", "")
                                        )
                                        if filepath:
                                            downloaded_paths.append(filepath)
                                        break
            
        except Exception as e:
            print(f"    ❌ Failed to download gallery: {e}")
        
        return downloaded_paths
    
    def fetch_subreddit_posts(self, subreddit: str, days_back: int = 14) -> List[Dict[str, Any]]:
        """Fetch posts from a subreddit within the last N days."""
        print(f"📊 Fetching posts from r/{subreddit}...")
        
        posts = []
        after = None
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=days_back)
        cutoff_timestamp = cutoff_time.timestamp()
        
        while True:
            try:
                # Build API URL
                url = f"{REDDIT_API_URL}/r/{subreddit}/new.json"
                params = {
                    "limit": 100,
                    "raw_json": 1
                }
                if after:
                    params["after"] = after
                
                response = self.session.get(url, params=params, timeout=10)
                
                if response.status_code == 429:
                    print("⏳ Rate limited, waiting 60 seconds...")
                    time.sleep(60)
                    continue
                
                if response.status_code != 200:
                    print(f"❌ Error fetching r/{subreddit}: {response.status_code}")
                    break
                
                data = response.json()
                children = data.get("data", {}).get("children", [])
                
                if not children:
                    break
                
                for child in children:
                    post_data = child.get("data", {})
                    created_utc = post_data.get("created_utc", 0)
                    
                    # Stop if we've gone too far back in time
                    if created_utc < cutoff_timestamp:
                        return posts
                    
                    # Filter content
                    if (post_data.get("over_18", False) or  # Skip NSFW
                        post_data.get("score", 0) < 20 or  # Require score >= 20
                        not self.is_image_content(post_data)):  # Must be image content
                        continue
                    
                    posts.append(post_data)
                
                # Check if we have more pages
                after = data.get("data", {}).get("after")
                if not after:
                    break
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Error fetching r/{subreddit}: {e}")
                break
        
        print(f"  ✅ Found {len(posts)} valid posts from r/{subreddit}")
        return posts
    
    def scrape_all_subreddits(self) -> List[Dict[str, Any]]:
        """Scrape all configured subreddits."""
        print(f"🚀 Starting scrape of {len(ALL_SUBREDDITS)} subreddits...")
        print(f"📅 Looking for posts from the last 14 days")
        print(f"🎯 Strong US subreddits: {STRONG_US_SUBREDDITS}")
        print(f"🌐 Broad subreddits: {BROAD_SUBREDDITS}")
        
        all_posts = []
        
        for subreddit in ALL_SUBREDDITS:
            try:
                posts = self.fetch_subreddit_posts(subreddit)
                all_posts.extend(posts)
                time.sleep(1)  # Be nice to Reddit
            except Exception as e:
                print(f"❌ Failed to scrape r/{subreddit}: {e}")
                continue
        
        print(f"\n📊 Total posts collected: {len(all_posts)}")
        return all_posts
    
    def process_posts(self, posts: List[Dict[str, Any]]) -> pd.DataFrame:
        """Process posts and calculate US scores."""
        print("🔍 Processing posts and calculating US scores...")
        print("📥 Downloading images for US-focused memes only...")
        
        processed_data = []
        downloaded_count = 0
        
        for i, post in enumerate(posts, 1):
            if i % 50 == 0:
                print(f"  Progress: {i}/{len(posts)} ({i/len(posts)*100:.1f}%)")
            
            # Calculate US score
            us_score = self.calculate_us_score(post)
            is_us = us_score >= 2
            
            # Download images only for US-focused memes
            image_paths = []
            if is_us:  # Only download images for US-focused memes
                if post.get("is_gallery", False):
                    # Download gallery images
                    image_paths = self.download_gallery_images(post)
                else:
                    # Download single image
                    url = post.get("url", "")
                    if url and self.is_image_content(post):
                        filepath = self.download_image(
                            url,
                            post.get("id", ""),
                            post.get("subreddit", ""),
                            post.get("title", "")
                        )
                        if filepath:
                            image_paths = [filepath]
            
            if image_paths:
                downloaded_count += len(image_paths)
            
            # Extract relevant data
            processed_post = {
                "id": post.get("id"),
                "subreddit": post.get("subreddit"),
                "title": post.get("title"),
                "url": post.get("url"),
                "permalink": f"https://reddit.com{post.get('permalink', '')}",
                "score": post.get("score", 0),
                "num_comments": post.get("num_comments", 0),
                "created_utc": post.get("created_utc"),
                "created_datetime": datetime.fromtimestamp(
                    post.get("created_utc", 0), tz=timezone.utc
                ).isoformat(),
                "domain": post.get("domain"),
                "is_gallery": post.get("is_gallery", False),
                "image_paths": "|".join(image_paths) if image_paths else "",
                "image_count": len(image_paths),
                "us_score": us_score,
                "is_us": is_us
            }
            
            processed_data.append(processed_post)
        
        print(f"  ✅ Downloaded {downloaded_count} images")
        
        df = pd.DataFrame(processed_data)
        
        # Sort by creation time (newest first)
        df = df.sort_values("created_utc", ascending=False)
        
        return df
    
    def save_results(self, df: pd.DataFrame):
        """Save results to CSV files."""
        print("💾 Saving results...")
        
        # Save all posts with scores
        df.to_csv("us_memes_all.csv", index=False)
        print(f"📄 us_memes_all.csv: {len(df)} rows")
        
        # Save only US-focused posts
        us_posts = df[df["is_us"] == True]
        us_posts.to_csv("us_memes_strict.csv", index=False)
        print(f"📄 us_memes_strict.csv: {len(us_posts)} rows")
        
        # Print summary
        print(f"\n📊 SUMMARY:")
        print(f"  📱 Total posts: {len(df)}")
        print(f"  🇺🇸 US-focused posts: {len(us_posts)} ({len(us_posts)/len(df)*100:.1f}%)")
        print(f"  📈 Average US score: {df['us_score'].mean():.2f}")
        print(f"  🖼️  Images downloaded: {df['image_count'].sum()}")
        print(f"  📁 Images saved to: {self.images_dir}")
        
        # Show score distribution
        score_dist = df['us_score'].value_counts().sort_index()
        print(f"\n📊 US Score Distribution:")
        for score, count in score_dist.items():
            print(f"  Score {score}: {count} posts")

def main():
    """Main execution function."""
    print("🇺🇸 US MEMES 14-DAY SCRAPER")
    print("=" * 50)
    
    try:
        # Initialize scraper
        scraper = RedditScraper()
        
        # Authenticate
        if not scraper.authenticate():
            return
        
        # Scrape all subreddits
        posts = scraper.scrape_all_subreddits()
        
        if not posts:
            print("❌ No posts found")
            return
        
        # Process posts
        df = scraper.process_posts(posts)
        
        # Save results
        scraper.save_results(df)
        
        print("\n✅ Scraping complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    main()
