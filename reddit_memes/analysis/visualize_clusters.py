#!/usr/bin/env python3
"""
Visualize Meme Clusters
=======================

Shows exactly what memes are clustered together with their details.
"""

import json
from pathlib import Path
from typing import Dict, List, Any


def visualize_clusters(json_path: str):
    """Show detailed cluster visualizations."""
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("🔍 UK Meme Cluster Visualization")
    print("=" * 60)
    
    metadata = data['metadata']
    print(f"📊 Total memes: {metadata['total_memes']}")
    print(f"🎯 Number of clusters: {metadata['n_clusters']}")
    print(f"🔢 Embedding model: {metadata.get('embedding_model', 'Unknown')}")
    print(f"📐 Embedding dimension: {metadata['embedding_dimension']}")
    print()
    
    cluster_analysis = data['cluster_analysis']
    
    # Sort clusters by size (largest first)
    sorted_clusters = sorted(cluster_analysis.items(), key=lambda x: x[1]['size'], reverse=True)
    
    for cluster_id, analysis in sorted_clusters:
        print(f"🔵 CLUSTER {cluster_id} ({analysis['size']} memes)")
        print("=" * 50)
        
        # Show all memes in this cluster
        for i, meme in enumerate(analysis['memes'], 1):
            print(f"\n{i}. {meme['title']}")
            print(f"   📍 r/{meme['subreddit']} | 👍 {meme['ups']} upvotes | 💬 {meme['num_comments']} comments")
            print(f"   🔗 {meme['url']}")
            
            # Show key parts of the analysis
            analysis_data = meme['analysis']
            if analysis_data['topic']:
                print(f"   🎯 Topic: {analysis_data['topic']}")
            if analysis_data['humor_type']:
                print(f"   😄 Humor: {analysis_data['humor_type']}")
            if analysis_data['context']:
                print(f"   🇬🇧 Context: {analysis_data['context']}")
            
            # Show a snippet of the description
            description = analysis_data['description']
            if description and len(description) > 200:
                description = description[:200] + "..."
            if description:
                print(f"   📝 Description: {description}")
        
        # Show cluster summary
        print(f"\n📊 Cluster {cluster_id} Summary:")
        print(f"   • Size: {analysis['size']} memes")
        
        if 'avg_engagement' in analysis:
            print(f"   • Avg upvotes: {analysis['avg_engagement']:.1f}")
        else:
            total_ups = sum(meme['ups'] for meme in analysis['memes'])
            avg_ups = total_ups / analysis['size']
            print(f"   • Avg upvotes: {avg_ups:.1f}")
        
        # Show subreddit breakdown
        subreddits = [meme['subreddit'] for meme in analysis['memes']]
        subreddit_counts = {}
        for sub in subreddits:
            subreddit_counts[sub] = subreddit_counts.get(sub, 0) + 1
        
        print(f"   • Subreddits: {', '.join([f'r/{sub}({count})' for sub, count in subreddit_counts.items()])}")
        
        # Show common themes
        topics = [meme['analysis']['topic'] for meme in analysis['memes'] if meme['analysis']['topic']]
        humor_types = [meme['analysis']['humor_type'] for meme in analysis['memes'] if meme['analysis']['humor_type']]
        
        if topics:
            unique_topics = list(set(topics))
            print(f"   • Common topics: {', '.join(unique_topics[:3])}")
        
        if humor_types:
            unique_humor = list(set(humor_types))
            print(f"   • Humor types: {', '.join(unique_humor[:3])}")
        
        print("\n" + "─" * 60 + "\n")


def compare_clusters(json_path: str):
    """Compare clusters side by side."""
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("🔄 Cluster Comparison")
    print("=" * 60)
    
    cluster_analysis = data['cluster_analysis']
    
    # Create a comparison table
    print(f"{'Cluster':<8} {'Size':<6} {'Avg Ups':<10} {'Top Subreddit':<15} {'Sample Title':<30}")
    print("-" * 80)
    
    for cluster_id, analysis in cluster_analysis.items():
        size = analysis['size']
        
        # Calculate average upvotes
        if 'avg_engagement' in analysis:
            avg_ups = analysis['avg_engagement']
        else:
            total_ups = sum(meme['ups'] for meme in analysis['memes'])
            avg_ups = total_ups / size
        
        # Get most common subreddit
        subreddits = [meme['subreddit'] for meme in analysis['memes']]
        subreddit_counts = {}
        for sub in subreddits:
            subreddit_counts[sub] = subreddit_counts.get(sub, 0) + 1
        top_subreddit = max(subreddit_counts.items(), key=lambda x: x[1])[0]
        
        # Get a sample title
        sample_title = analysis['sample_titles'][0] if analysis['sample_titles'] else "N/A"
        if len(sample_title) > 27:
            sample_title = sample_title[:24] + "..."
        
        print(f"{cluster_id:<8} {size:<6} {avg_ups:<10.1f} {top_subreddit:<15} {sample_title:<30}")
    
    print()


def find_similar_memes(json_path: str, target_meme_id: str):
    """Find memes in the same cluster as a target meme."""
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Find the target meme
    target_meme = None
    target_cluster = None
    
    for meme in data['memes_with_clusters']:
        if meme['id'] == target_meme_id:
            target_meme = meme
            target_cluster = meme['cluster_id']
            break
    
    if not target_meme:
        print(f"❌ Meme with ID '{target_meme_id}' not found")
        return
    
    print(f"🎯 Finding memes similar to: {target_meme['title']}")
    print(f"📍 Cluster: {target_cluster}")
    print("=" * 60)
    
    # Find all memes in the same cluster
    cluster_memes = [meme for meme in data['memes_with_clusters'] if meme['cluster_id'] == target_cluster]
    
    print(f"Found {len(cluster_memes)} memes in the same cluster:")
    print()
    
    for i, meme in enumerate(cluster_memes, 1):
        if meme['id'] == target_meme_id:
            print(f"🎯 {i}. {meme['title']} (TARGET)")
        else:
            print(f"   {i}. {meme['title']}")
        print(f"      📍 r/{meme['subreddit']} | 👍 {meme['ups']} upvotes")


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
    
    print(f"📊 Visualizing clusters from: {clusters_path.name}")
    print()
    
    # Show detailed cluster visualization
    visualize_clusters(str(clusters_path))
    
    # Show cluster comparison
    compare_clusters(str(clusters_path))
    
    # Example: find similar memes to a specific one
    print("🔍 Example: Finding similar memes")
    print("=" * 40)
    print("To find memes similar to a specific one, use:")
    print("python3 visualize_clusters.py --similar MEME_ID")
    print()
    print("Example meme IDs from your data:")
    
    # Show some example meme IDs
    with open(clusters_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for i, meme in enumerate(data['memes_with_clusters'][:5], 1):
        print(f"   {i}. {meme['id']} - {meme['title'][:50]}...")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 2 and sys.argv[1] == "--similar":
        target_id = sys.argv[2]
        script_dir = Path(__file__).parent
        
        # Find cluster file
        cluster_files = [
            "uk_memes_openai_clusters.json",
            "uk_memes_smart_clusters.json", 
            "uk_memes_proper_clusters.json",
            "uk_memes_clusters.json"
        ]
        
        clusters_path = None
        for filename in cluster_files:
            path = script_dir / filename
            if path.exists():
                clusters_path = path
                break
        
        if clusters_path:
            find_similar_memes(str(clusters_path), target_id)
        else:
            print("❌ No cluster files found")
    else:
        main()
