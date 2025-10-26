#!/usr/bin/env python3
"""
Quick verification that all essential files are present for Render deployment.
"""

from pathlib import Path

def main():
    backend_dir = Path(__file__).parent
    
    essential_files = [
        "app.py",
        "config.py", 
        "requirements.txt",
        "env.example",
        "data/clustering/meme_clusters.json",
        "data/clustering/cluster_summaries.json",
        "data/clustering/all_results.json",
        "data/image-pipeline/meme_descriptions.json",
        "data/image-pipeline/cluster_labels_dict.json",
    ]
    
    print("🔍 Checking essential files for Render deployment...")
    
    missing = []
    for file_path in essential_files:
        full_path = backend_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing.append(file_path)
    
    if missing:
        print(f"\n⚠️ Missing files: {missing}")
        return 1
    else:
        print("\n🎉 All essential files present! Ready for Render deployment.")
        return 0

if __name__ == "__main__":
    exit(main())
