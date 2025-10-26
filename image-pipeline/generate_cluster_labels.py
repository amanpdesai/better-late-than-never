#!/usr/bin/env python3
"""
Generate concise 5-word labels for meme clusters using OpenAI API.
Analyzes the meme_clusters.txt file and creates descriptive labels for each cluster.
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any

# Import OpenAI
try:
    import openai
except ImportError:
    print("❌ Error: 'openai' module not found. Please install it with: pip install openai")
    exit(1)

# Initialize OpenAI client with environment variable
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_cluster_file(file_path: str) -> Dict[str, List[Dict[str, str]]]:
    """Parse the meme_clusters.txt file and extract cluster data."""
    clusters = {}
    current_field = None
    current_cluster = None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Detect field headers
            if line.startswith("=== FIELD:"):
                current_field = line.split(":")[1].strip()
                clusters[current_field] = {}
                continue
            
            # Detect cluster headers
            if line.startswith("📁 Cluster") and "—" in line:
                cluster_match = re.match(r"📁 Cluster (\d+) — (\d+) memes", line)
                if cluster_match:
                    cluster_num = cluster_match.group(1)
                    meme_count = cluster_match.group(2)
                    current_cluster = f"Cluster {cluster_num}"
                    if current_field:
                        if current_field not in clusters:
                            clusters[current_field] = {}
                        clusters[current_field][current_cluster] = {
                            "count": int(meme_count),
                            "memes": []
                        }
                continue
            
            # Parse meme descriptions
            if line.startswith("•") and current_cluster and current_field:
                # Extract filename and description
                parts = line.split(": ", 1)
                if len(parts) == 2:
                    filename = parts[0][2:]  # Remove "• " prefix
                    description = parts[1]
                    clusters[current_field][current_cluster]["memes"].append({
                        "filename": filename,
                        "description": description
                    })
    
    return clusters

def generate_cluster_label(descriptions: List[str], field_name: str, cluster_num: str) -> str:
    """Generate a distinctive label that explains what makes this cluster unique."""
    
    # Prepare the descriptions for analysis
    descriptions_text = "\n".join([f"- {desc}" for desc in descriptions])
    
    prompt = f"""Analyze the following {field_name.lower()} descriptions from Cluster {cluster_num} and identify what makes this cluster DISTINCTIVE and UNIQUE compared to other clusters.

Focus on:
1. What common characteristics bind these memes together?
2. What makes this cluster different from others?
3. What specific patterns or themes are unique to this group?

Descriptions:
{descriptions_text}

Generate a concise 5-word label that captures the DISTINCTIVE characteristics that make this cluster unique. Focus on what separates it from other clusters, not just what it contains.

5-word distinctive label:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert at analyzing meme clusters and identifying what makes each cluster unique and distinctive. Focus on distinguishing characteristics that separate this cluster from others, not just general themes."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=25,
            temperature=0.4
        )
        
        label = response.choices[0].message.content.strip()
        
        # Validate it's exactly 5 words
        words = label.split()
        if len(words) != 5:
            # If not exactly 5 words, try to fix it
            if len(words) > 5:
                label = " ".join(words[:5])
            else:
                # Pad with distinctive words if too short
                padding = ["Distinctive", "Unique", "Pattern", "Characteristics", "Elements"]
                while len(words) < 5:
                    words.append(padding[len(words) - len(label.split())])
                label = " ".join(words)
        
        return label
        
    except Exception as e:
        print(f"❌ Error generating label: {e}")
        return "Distinctive Meme Cluster Characteristics"

def main():
    """Main function to process clusters and generate labels."""
    print("🔍 Analyzing meme clusters and generating labels...")
    
    # Parse the cluster file
    cluster_file = Path("meme_clusters.txt")
    if not cluster_file.exists():
        print(f"❌ Error: {cluster_file} not found!")
        return
    
    clusters = parse_cluster_file(str(cluster_file))
    
    if not clusters:
        print("❌ No clusters found in the file!")
        return
    
    # Generate labels for each field and cluster
    results = {}
    
    for field_name, field_clusters in clusters.items():
        print(f"\n📊 Processing {field_name} field...")
        results[field_name] = {}
        
        for cluster_name, cluster_data in field_clusters.items():
            print(f"  🏷️  Generating label for {cluster_name} ({cluster_data['count']} memes)...")
            
            # Extract cluster number
            cluster_num = cluster_name.split()[-1]  # Extract number from "Cluster X"
            
            # Extract descriptions
            descriptions = [meme["description"] for meme in cluster_data["memes"]]
            
            # Generate label
            label = generate_cluster_label(descriptions, field_name, cluster_num)
            results[field_name][cluster_name] = {
                "label": label,
                "count": cluster_data["count"],
                "description": f"Contains {cluster_data['count']} memes with distinctive characteristics: {label.lower()}"
            }
            
            print(f"    ✅ {cluster_name}: {label}")
    
    # Create dictionary format for each field
    cluster_dictionaries = {}
    for field_name, field_clusters in results.items():
        cluster_dictionaries[field_name] = {}
        for cluster_name, cluster_info in field_clusters.items():
            cluster_dictionaries[field_name][cluster_name] = cluster_info['label']
    
    # Save results
    output_file = "cluster_labels.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Save dictionary format
    dict_file = "cluster_labels_dict.json"
    with open(dict_file, 'w', encoding='utf-8') as f:
        json.dump(cluster_dictionaries, f, indent=2, ensure_ascii=False)
    
    # Generate summary report
    summary_file = "cluster_labels_summary.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("🏷️  MEME CLUSTER DISTINCTIVE LABELS\n")
        f.write("=" * 50 + "\n\n")
        
        for field_name, field_clusters in results.items():
            f.write(f"📊 {field_name.upper()} FIELD\n")
            f.write("-" * 30 + "\n")
            
            for cluster_name, cluster_info in field_clusters.items():
                f.write(f"{cluster_name}: {cluster_info['label']}\n")
                f.write(f"  └─ {cluster_info['description']}\n\n")
            
            f.write("\n")
    
    print(f"\n✅ Results saved to:")
    print(f"  📄 {output_file}")
    print(f"  📄 {dict_file}")
    print(f"  📄 {summary_file}")
    
    # Print summary to console
    print(f"\n🏷️  CLUSTER DISTINCTIVE LABELS")
    print("=" * 50)
    
    for field_name, field_clusters in results.items():
        print(f"\n📊 {field_name.upper()}")
        print("-" * 30)
        for cluster_name, cluster_info in field_clusters.items():
            print(f"{cluster_name}: {cluster_info['label']}")
    
    # Print dictionary format
    print(f"\n📋 DICTIONARY FORMAT:")
    print("=" * 30)
    for field_name, field_dict in cluster_dictionaries.items():
        print(f"\n{field_name} = {{")
        for cluster_name, label in field_dict.items():
            print(f'    "{cluster_name}": "{label}",')
        print("}")

if __name__ == "__main__":
    main()
