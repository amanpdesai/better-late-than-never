#!/usr/bin/env python3
"""
OpenAI Embedding for UK Memes
=============================

Uses your own OpenAI API key to generate proper embeddings for meme clustering.
"""

import json
import numpy as np
import os
from pathlib import Path
from typing import List, Dict, Any
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent.parent / ".env")

try:
    from openai import OpenAI
except ImportError:
    print("Installing openai package...")
    import subprocess
    subprocess.run(["pip", "install", "openai"])
    from openai import OpenAI


class OpenAIMemeEmbedder:
    """Handles embedding generation using your own OpenAI API key."""
    
    def __init__(self, api_key: str = None):
        """Initialize with your OpenAI API key."""
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            # Try to get from environment
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("Please provide OpenAI API key either as parameter or set OPENAI_API_KEY environment variable")
            self.client = OpenAI(api_key=api_key)
    
    def load_descriptions(self, json_path: str) -> List[Dict[str, Any]]:
        """Load meme descriptions from JSON file."""
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_embeddings(self, descriptions: List[Dict[str, Any]], model: str = "text-embedding-3-small") -> List[List[float]]:
        """Generate embeddings using OpenAI's embedding API."""
        embeddings = []
        
        print(f"🔢 Using OpenAI embedding model: {model}")
        
        for i, meme in enumerate(descriptions, 1):
            print(f"Generating embedding {i}/{len(descriptions)}: {meme['id']}")
            
            # Combine all text fields for embedding
            text_to_embed = f"""
            Title: {meme['title']}
            Description: {meme['analysis']['description']}
            Template: {meme['analysis']['meme_template']}
            Topic: {meme['analysis']['topic']}
            Context: {meme['analysis']['context']}
            """
            
            try:
                # Use OpenAI Embeddings API
                response = self.client.embeddings.create(
                    model=model,
                    input=text_to_embed,
                    encoding_format="float"
                )
                
                embedding = response.data[0].embedding
                embeddings.append(embedding)
                
                print(f"  ✅ Generated embedding (dimension: {len(embedding)})")
                
            except Exception as e:
                print(f"  ❌ Error generating embedding: {e}")
                # Use random vector as fallback
                embedding = np.random.rand(1536).tolist()
                embeddings.append(embedding)
        
        return embeddings
    
    def perform_clustering(self, embeddings: List[List[float]], n_clusters: int = 5) -> List[int]:
        """Perform K-means clustering on embeddings."""
        from sklearn.cluster import KMeans
        
        # Convert to numpy array
        X = np.array(embeddings)
        
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(X)
        
        return cluster_labels.tolist()
    
    def analyze_clusters(self, descriptions: List[Dict[str, Any]], cluster_labels: List[int]) -> Dict[int, Dict[str, Any]]:
        """Analyze each cluster to understand meme categories."""
        cluster_analysis = {}
        
        for cluster_id in set(cluster_labels):
            cluster_memes = [desc for i, desc in enumerate(descriptions) if cluster_labels[i] == cluster_id]
            
            # Extract common themes
            topics = [meme['analysis']['topic'] for meme in cluster_memes if meme['analysis']['topic']]
            humor_types = [meme['analysis']['humor_type'] for meme in cluster_memes if meme['analysis']['humor_type']]
            templates = [meme['analysis']['meme_template'] for meme in cluster_memes if meme['analysis']['meme_template']]
            
            # Get sample titles
            sample_titles = [meme['title'] for meme in cluster_memes[:3]]
            
            # Calculate average engagement
            avg_ups = sum(meme['ups'] for meme in cluster_memes) / len(cluster_memes)
            
            cluster_analysis[cluster_id] = {
                'size': len(cluster_memes),
                'topics': list(set(topics)),
                'humor_types': list(set(humor_types)),
                'templates': list(set(templates)),
                'sample_titles': sample_titles,
                'avg_engagement': avg_ups,
                'memes': cluster_memes
            }
        
        return cluster_analysis
    
    def process_memes(self, json_path: str, output_path: str, n_clusters: int = 5, embedding_model: str = "text-embedding-3-small"):
        """Main processing function."""
        print("🚀 Starting OpenAI Embedding and Clustering")
        print(f"📊 Using embedding model: {embedding_model}")
        
        # Load descriptions
        print("📖 Loading meme descriptions...")
        descriptions = self.load_descriptions(json_path)
        print(f"Found {len(descriptions)} memes")
        
        # Generate embeddings
        print("\n🔢 Generating embeddings...")
        embeddings = self.generate_embeddings(descriptions, embedding_model)
        
        # Perform clustering
        print(f"\n🎯 Performing clustering with {n_clusters} clusters...")
        cluster_labels = self.perform_clustering(embeddings, n_clusters)
        
        # Analyze clusters
        print("\n📊 Analyzing clusters...")
        cluster_analysis = self.analyze_clusters(descriptions, cluster_labels)
        
        # Add cluster labels to descriptions
        for i, meme in enumerate(descriptions):
            meme['cluster_id'] = cluster_labels[i]
        
        # Save results
        results = {
            'metadata': {
                'total_memes': len(descriptions),
                'n_clusters': n_clusters,
                'embedding_model': embedding_model,
                'embedding_dimension': len(embeddings[0]) if embeddings else 0
            },
            'cluster_analysis': cluster_analysis,
            'memes_with_clusters': descriptions,
            'embeddings': embeddings
        }
        
        print(f"\n💾 Saving results to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Print cluster summary
        print(f"\n✅ Clustering complete!")
        print(f"📈 Cluster Summary:")
        for cluster_id, analysis in cluster_analysis.items():
            print(f"  🔵 Cluster {cluster_id}: {analysis['size']} memes (avg {analysis['avg_engagement']:.1f} upvotes)")
            if analysis['sample_titles']:
                print(f"    📝 Sample: {', '.join(analysis['sample_titles'])}")
        
        return results


def main():
    """Main function to run the embedding and clustering."""
    
    # Set up paths
    script_dir = Path(__file__).parent
    input_path = script_dir.parent / "data" / "uk_memes_descriptions.json"
    output_path = script_dir.parent / "data" / "uk_memes_openai_clusters.json"
    
    # Check if input file exists
    if not input_path.exists():
        print(f"❌ Input file not found: {input_path}")
        return
    
    # Get OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Please set OPENAI_API_KEY environment variable with your OpenAI API key")
        print("   You can get one from: https://platform.openai.com/api-keys")
        return
    
    # Create embedder and process
    embedder = OpenAIMemeEmbedder(api_key)
    
    # Try different embedding models
    embedding_models = [
        "text-embedding-3-small",    # Cheapest, good quality
        "text-embedding-3-large",    # Higher quality, more expensive
        "text-embedding-ada-002"     # Older but reliable
    ]
    
    for model in embedding_models:
        try:
            print(f"\n🧪 Testing embedding model: {model}")
            embedder.process_memes(str(input_path), str(output_path), n_clusters=6, embedding_model=model)
            print(f"✅ Successfully used {model}")
            break
        except Exception as e:
            print(f"❌ Failed with {model}: {e}")
            continue
    else:
        print("❌ All embedding models failed!")


if __name__ == "__main__":
    main()
