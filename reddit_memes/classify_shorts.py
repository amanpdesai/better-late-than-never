#!/usr/bin/env python3
"""
YouTube Shorts Meme Classifier
=============================

Classifies YouTube Shorts as memes or regular content using multiple approaches.
"""

import json
import pandas as pd
import re
from typing import Dict, List, Any

# Meme classification keywords
MEME_KEYWORDS = [
    # Meme formats
    "meme", "memes", "dank", "viral", "trending", "template",
    # Humor indicators  
    "funny", "hilarious", "lol", "lmao", "rofl", "comedy", "joke",
    # Internet culture
    "challenge", "reaction", "compilation", "fails", "wins", "prank",
    # Popular meme formats
    "pov", "when", "me when", "nobody:", "everyone:", "me:",
    # Hashtags
    "#meme", "#funny", "#viral", "#trending", "#comedy", "#dank",
    # Meme-specific terms
    "sigma", "alpha", "beta", "chad", "virgin", "based", "cringe",
    "sus", "no cap", "cap", "fr", "ong", "bussin", "slay", "periodt"
]

MEME_CHANNEL_KEYWORDS = [
    "meme", "funny", "comedy", "viral", "trending", "reaction",
    "fails", "wins", "compilation", "challenge", "prank", "dank"
]

def analyze_text_content(title: str, description: str, tags: str) -> Dict[str, Any]:
    """Analyze text content for meme indicators."""
    text = f"{title} {description} {tags}".lower()
    
    # Count meme keywords
    meme_matches = [keyword for keyword in MEME_KEYWORDS if keyword in text]
    meme_score = len(meme_matches)
    
    # Check for meme patterns
    patterns = {
        "pov_pattern": bool(re.search(r'\bpov\b', text)),
        "when_pattern": bool(re.search(r'\bwhen\b', text)),
        "nobody_pattern": bool(re.search(r'\bnobody\b', text)),
        "everyone_pattern": bool(re.search(r'\beveryone\b', text)),
        "me_pattern": bool(re.search(r'\bme\b', text)),
        "hashtag_meme": bool(re.search(r'#meme|#funny|#viral|#comedy', text)),
        "reaction_video": bool(re.search(r'\breaction\b|\bcompilation\b', text)),
        "challenge_video": bool(re.search(r'\bchallenge\b|\bprank\b', text))
    }
    
    pattern_score = sum(patterns.values())
    
    return {
        "meme_keywords": meme_matches,
        "meme_score": meme_score,
        "pattern_score": pattern_score,
        "patterns": patterns,
        "total_text_score": meme_score + pattern_score
    }

def analyze_metrics(duration_sec: int, view_count: int, like_count: int, comment_count: int) -> Dict[str, Any]:
    """Analyze engagement metrics for meme indicators."""
    metrics = {
        "duration_score": 0,
        "engagement_score": 0,
        "comment_score": 0
    }
    
    # Duration analysis (memes are typically 15-45 seconds)
    if 15 <= duration_sec <= 45:
        metrics["duration_score"] = 10
    elif 10 <= duration_sec <= 60:
        metrics["duration_score"] = 5
    
    # Engagement analysis
    if view_count and like_count:
        engagement_ratio = like_count / view_count
        if engagement_ratio > 0.08:  # 8%+ like rate
            metrics["engagement_score"] = 20
        elif engagement_ratio > 0.05:  # 5%+ like rate
            metrics["engagement_score"] = 15
        elif engagement_ratio > 0.03:  # 3%+ like rate
            metrics["engagement_score"] = 10
    
    # Comment engagement
    if view_count and comment_count:
        comment_ratio = comment_count / view_count
        if comment_ratio > 0.02:  # 2%+ comment rate
            metrics["comment_score"] = 15
        elif comment_ratio > 0.01:  # 1%+ comment rate
            metrics["comment_score"] = 10
    
    metrics["total_metrics_score"] = sum(metrics.values())
    return metrics

def analyze_channel(channel_title: str) -> Dict[str, Any]:
    """Analyze channel for meme indicators."""
    channel_lower = channel_title.lower()
    
    meme_channel_matches = [keyword for keyword in MEME_CHANNEL_KEYWORDS if keyword in channel_lower]
    channel_score = len(meme_channel_matches) * 5  # 5 points per match
    
    return {
        "meme_channel_keywords": meme_channel_matches,
        "channel_score": channel_score
    }

def classify_short(video_data: Dict[str, Any]) -> Dict[str, Any]:
    """Classify a single short as meme or regular content."""
    
    # Get video data
    title = video_data.get('title', '')
    description = video_data.get('description', '')
    tags = video_data.get('tags', '')
    channel_title = video_data.get('channelTitle', '')
    duration_sec = video_data.get('durationSec', 0)
    view_count = video_data.get('viewCount', 0)
    like_count = video_data.get('likeCount', 0)
    comment_count = video_data.get('commentCount', 0)
    
    # Analyze different aspects
    text_analysis = analyze_text_content(title, description, tags)
    metrics_analysis = analyze_metrics(duration_sec, view_count, like_count, comment_count)
    channel_analysis = analyze_channel(channel_title)
    
    # Calculate total score
    total_score = (
        text_analysis["total_text_score"] * 0.4 +  # 40% weight
        metrics_analysis["total_metrics_score"] * 0.3 +  # 30% weight
        channel_analysis["channel_score"] * 0.2 +  # 20% weight
        (10 if 15 <= duration_sec <= 45 else 0) * 0.1  # 10% weight for duration
    )
    
    # Classification threshold
    is_meme = total_score >= 25
    
    return {
        "videoId": video_data.get('videoId'),
        "title": title,
        "channelTitle": channel_title,
        "is_meme": is_meme,
        "meme_confidence": min(total_score / 50, 1.0),  # Normalize to 0-1
        "total_score": total_score,
        "text_analysis": text_analysis,
        "metrics_analysis": metrics_analysis,
        "channel_analysis": channel_analysis
    }

def classify_dataset(input_file: str, output_file: str):
    """Classify entire dataset of YouTube Shorts."""
    print(f"📊 Loading dataset from {input_file}")
    
    # Load data
    if input_file.endswith('.json'):
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        df = pd.read_csv(input_file)
        data = df.to_dict('records')
    
    print(f"📱 Processing {len(data)} Shorts...")
    
    # Classify each short
    results = []
    meme_count = 0
    
    for i, video in enumerate(data):
        if i % 100 == 0:
            print(f"  Progress: {i}/{len(data)} ({i/len(data)*100:.1f}%)")
        
        classification = classify_short(video)
        results.append(classification)
        
        if classification["is_meme"]:
            meme_count += 1
    
    print(f"\n🎯 CLASSIFICATION RESULTS:")
    print(f"  📱 Total Shorts: {len(data)}")
    print(f"  🎭 Memes: {meme_count} ({meme_count/len(data)*100:.1f}%)")
    print(f"  📺 Regular Content: {len(data) - meme_count} ({(len(data) - meme_count)/len(data)*100:.1f}%)")
    
    # Save results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Results saved to {output_file}")
    
    # Show top memes by confidence
    top_memes = sorted([r for r in results if r["is_meme"]], 
                      key=lambda x: x["meme_confidence"], reverse=True)[:10]
    
    print(f"\n🏆 TOP 10 MEMES (by confidence):")
    for i, meme in enumerate(top_memes, 1):
        print(f"  {i}. {meme['title'][:60]}... (confidence: {meme['meme_confidence']:.2f})")

if __name__ == "__main__":
    # Classify your dataset
    classify_dataset("massive_global_shorts.json", "classified_shorts.json")
