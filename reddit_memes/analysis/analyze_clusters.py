#!/usr/bin/env python3
"""
Cluster Analysis Summary
========================

Analyzes the clustering results and provides insights into meme categories.
"""

import json
from pathlib import Path


def analyze_clusters(json_path: str):
    """Analyze and display cluster insights."""
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("🎯 UK Meme Cluster Analysis (OpenAI Embeddings)")
    print("=" * 60)
    
    metadata = data['metadata']
    print(f"📊 Total memes: {metadata['total_memes']}")
    print(f"🎯 Number of clusters: {metadata['n_clusters']}")
    print(f"🔢 Embedding model: {metadata.get('embedding_model', 'Unknown')}")
    print(f"📐 Embedding dimension: {metadata['embedding_dimension']}")
    print()
    
    cluster_analysis = data['cluster_analysis']
    
    for cluster_id, analysis in cluster_analysis.items():
        print(f"🔵 Cluster {cluster_id} ({analysis['size']} memes)")
        print("-" * 40)
        
        # Show sample titles
        print("📝 Sample titles:")
        for title in analysis['sample_titles']:
            print(f"   • {title}")
        
        # Show engagement stats
        if 'avg_engagement' in analysis:
            print(f"📈 Average upvotes: {analysis['avg_engagement']:.1f}")
        else:
            total_ups = sum(meme['ups'] for meme in analysis['memes'])
            avg_ups = total_ups / analysis['size']
            print(f"📈 Average upvotes: {avg_ups:.1f}")
        
        # Analyze common themes from descriptions
        descriptions = [meme['analysis']['description'] for meme in analysis['memes']]
        
        # Extract key themes (simplified analysis)
        political_keywords = ['political', 'election', 'party', 'government', 'vote', 'reform', 'tory', 'labour', 'politics']
        cultural_keywords = ['british', 'uk', 'england', 'scotland', 'wales', 'london', 'culture', 'britain']
        humor_keywords = ['funny', 'joke', 'humor', 'comedy', 'laugh', 'meme', 'comic']
        template_keywords = ['template', 'format', 'meme', 'image', 'panel', 'comic']
        
        political_count = sum(1 for desc in descriptions if any(kw in desc.lower() for kw in political_keywords))
        cultural_count = sum(1 for desc in descriptions if any(kw in desc.lower() for kw in cultural_keywords))
        humor_count = sum(1 for desc in descriptions if any(kw in desc.lower() for kw in humor_keywords))
        template_count = sum(1 for desc in descriptions if any(kw in desc.lower() for kw in template_keywords))
        
        print(f"🏛️  Political content: {political_count}/{analysis['size']} memes")
        print(f"🇬🇧 Cultural references: {cultural_count}/{analysis['size']} memes")
        print(f"😄 Humor focus: {humor_count}/{analysis['size']} memes")
        print(f"🎨 Template recognition: {template_count}/{analysis['size']} memes")
        
        # Show subreddit distribution
        subreddits = [meme['subreddit'] for meme in analysis['memes']]
        subreddit_counts = {}
        for sub in subreddits:
            subreddit_counts[sub] = subreddit_counts.get(sub, 0) + 1
        
        print(f"📊 Subreddit distribution:")
        for sub, count in sorted(subreddit_counts.items()):
            print(f"   • r/{sub}: {count} memes")
        
        print()


def main():
    """Main function."""
    script_dir = Path(__file__).parent
    
    # Look for different cluster files in order of preference
    cluster_files = [
        "data/uk_memes_openai_clusters.json",  # New OpenAI embeddings
        "data/uk_memes_smart_clusters.json",   # Smart GPT-5 features
        "data/uk_memes_proper_clusters.json",  # Proper embeddings (if they worked)
        "data/uk_memes_clusters.json"          # Original clusters
    ]
    
    clusters_path = None
    for filename in cluster_files:
        path = script_dir / filename
        if path.exists():
            clusters_path = path
            break
    
    if not clusters_path:
        print("❌ No cluster files found. Available options:")
        for filename in cluster_files:
            print(f"   • {filename}")
        print("\n💡 Run the embedding script first to generate clusters.")
        return
    
    print(f"📊 Analyzing clusters from: {clusters_path.name}")
    analyze_clusters(str(clusters_path))


if __name__ == "__main__":
    main()
