#!/usr/bin/env python3
"""
Image Downloader for Existing Meme Data
======================================

Downloads images from existing CSV files with meme metadata.
"""

import csv
import os
import re
import sys
try:
    import requests
except ImportError:
    print("❌ Error: 'requests' module not found. Please install it with: pip install requests")
    sys.exit(1)
import argparse
from pathlib import Path
from typing import List, Dict, Any
from meme_utils import download_image, ensure_dir

def load_csv_data(csv_path: str) -> List[Dict[str, Any]]:
    """Load meme data from CSV file."""
    memes = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            memes.append({
                'id': row['id'],
                'subreddit': row['subreddit'],
                'title': row['title'],
                'url': row['url'],
                'ups': int(row['ups']),
                'num_comments': int(row['num_comments'])
            })
    return memes

def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """Sanitize filename by removing/replacing invalid characters."""
    # Remove or replace invalid filename characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace multiple spaces with single space
    filename = re.sub(r'\s+', ' ', filename)
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    # Truncate if too long
    if len(filename) > max_length:
        filename = filename[:max_length].rstrip()
    return filename

def download_meme_images(csv_path: str, output_dir: str, limit: int = None) -> None:
    """Download images from CSV meme data."""
    
    print(f"📖 Loading meme data from {csv_path}")
    memes = load_csv_data(csv_path)
    
    if limit:
        memes = memes[:limit]
        print(f"📊 Limited to first {limit} memes")
    
    print(f"🖼️  Downloading images to {output_dir}")
    print(f"📊 Processing {len(memes)} memes...")
    
    # Create output directory
    ensure_dir(output_dir)
    
    downloaded = 0
    failed = 0
    
    for i, meme in enumerate(memes, 1):
        print(f"\n[{i}/{len(memes)}] {meme['id']} from r/{meme['subreddit']}")
        print(f"  📝 {meme['title'][:60]}...")
        print(f"  👍 {meme['ups']} upvotes")
        
        # Create filename from title
        title = sanitize_filename(meme['title'])
        if not title:  # Fallback if title is empty after sanitization
            title = f"{meme['subreddit']}_{meme['id']}"
        
        name_hint = title
        
        try:
            saved_path = download_image(meme['url'], output_dir, name_hint)
            if saved_path:
                print(f"  ✅ Downloaded: {saved_path}")
                downloaded += 1
            else:
                print(f"  ❌ Download failed")
                failed += 1
        except Exception as e:
            print(f"  ❌ Error: {e}")
            failed += 1
    
    print(f"\n🎉 Download complete!")
    print(f"  ✅ Successfully downloaded: {downloaded} images")
    print(f"  ❌ Failed downloads: {failed} images")
    print(f"  📁 Images saved to: {output_dir}")

def main():
    """Main function."""
    ap = argparse.ArgumentParser(description="Download images from existing meme CSV data.")
    ap.add_argument("csv_file", help="Path to CSV file with meme data")
    ap.add_argument("--output-dir", "-o", default="downloaded_images", help="Output directory for images (default: downloaded_images)")
    ap.add_argument("--limit", "-l", type=int, help="Limit number of memes to process")
    ap.add_argument("--filter-subreddit", help="Only download from specific subreddit")
    ap.add_argument("--min-upvotes", type=int, help="Only download memes with minimum upvotes")
    args = ap.parse_args()
    
    # Check if CSV file exists
    if not os.path.exists(args.csv_file):
        print(f"❌ CSV file not found: {args.csv_file}")
        return
    
    # Load and filter data
    print(f"📖 Loading data from {args.csv_file}")
    memes = load_csv_data(args.csv_file)
    
    # Apply filters
    if args.filter_subreddit:
        memes = [m for m in memes if m['subreddit'] == args.filter_subreddit]
        print(f"🔍 Filtered to r/{args.filter_subreddit}: {len(memes)} memes")
    
    if args.min_upvotes:
        memes = [m for m in memes if m['ups'] >= args.min_upvotes]
        print(f"🔍 Filtered to {args.min_upvotes}+ upvotes: {len(memes)} memes")
    
    if args.limit:
        memes = memes[:args.limit]
        print(f"🔍 Limited to {args.limit} memes")
    
    if not memes:
        print("❌ No memes found matching criteria")
        return
    
    # Download images
    download_meme_images(args.csv_file, args.output_dir, len(memes))

if __name__ == "__main__":
    main()
