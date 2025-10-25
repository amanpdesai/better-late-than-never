#!/usr/bin/env python3
"""
UK Meme Image Analysis with OpenAI Vision
========================================

Analyzes UK meme images using OpenAI GPT-5 Vision to generate structured descriptions
suitable for embedding and clustering analysis.
"""

import asyncio
import base64
import csv
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# Add root directory to path to import unwrap_openai
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from unwrap_openai import create_openai_completion, GPT5Deployment, ReasoningEffort


class MemeDescription(BaseModel):
    """Structured description of a meme image."""
    
    meme_template: str = Field(..., description="Identified image format or template type")
    text_content: str = Field(..., description="All text visible in the image")
    visual_elements: str = Field(..., description="Description of visual components and layout")
    topic: str = Field(..., description="Main subject or theme")
    humor_type: str = Field(..., description="Type of humor or communication style")
    context: str = Field(..., description="Cultural or regional context")
    description: str = Field(..., description="Overall description of the image content")


class MemeAnalysisResult(BaseModel):
    """Complete analysis result including original metadata and generated description."""
    
    # Original metadata from CSV
    id: str
    subreddit: str
    title: str
    url: str
    permalink: str
    ups: int
    num_comments: int
    created_utc: float
    
    # Generated description
    analysis: MemeDescription


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
                'permalink': row['permalink'],
                'ups': int(row['ups']),
                'num_comments': int(row['num_comments']),
                'created_utc': float(row['created_utc'])
            })
    return memes


def encode_image_to_base64(image_path: str) -> str:
    """Convert image file to base64 string for API submission."""
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


async def analyze_meme_image(image_path: str, meme_data: Dict[str, Any]) -> Optional[MemeDescription]:
    """Analyze a single meme image using OpenAI Vision API."""
    
    try:
        # Encode image to base64
        base64_image = encode_image_to_base64(image_path)
        
        # Create messages for OpenAI Vision API
        messages = [
            {
                "role": "system",
                "content": """Embed this meme into a text that follows a structured format that is good when i convert this into a embedding for the vectorDB to search"""
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Please describe this image content. The original title was: '{meme_data['title']}'"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
        
        # Call OpenAI API
        response = await create_openai_completion(
            messages=messages,
            model=GPT5Deployment.GPT_5,
            reasoning_effort=ReasoningEffort.LOW,
            max_completion_tokens=2048
        )
        
        # Parse response and create structured description
        content = response.choices[0].message.content
        
        # For now, use the full response as description and fill other fields with basic info
        return MemeDescription(
            meme_template="Image analysis",
            text_content="Text content extracted from image",
            visual_elements="Visual elements described in analysis",
            topic="Topic identified in analysis",
            humor_type="Communication style identified",
            context="Cultural context noted",
            description=content
        )
        
    except Exception as e:
        print(f"Error analyzing {image_path}: {e}")
        return None


async def process_all_memes(csv_path: str, images_dir: str, output_path: str) -> None:
    """Process all memes and generate structured descriptions."""
    
    # Load CSV data
    print("Loading meme data from CSV...")
    memes = load_csv_data(csv_path)
    print(f"Found {len(memes)} memes to analyze")
    
    results = []
    failed_images = []
    
    for i, meme in enumerate(memes, 1):
        print(f"\nProcessing {i}/{len(memes)}: {meme['id']} from r/{meme['subreddit']}")
        
        # Construct image path
        image_filename = f"{meme['subreddit']}_{meme['id']}.{meme['url'].split('.')[-1].split('?')[0]}"
        image_path = os.path.join(images_dir, image_filename)
        
        if not os.path.exists(image_path):
            print(f"  ⚠️  Image not found: {image_path}")
            failed_images.append(meme['id'])
            continue
        
        # Analyze the image
        print(f"  🔍 Analyzing image...")
        analysis = await analyze_meme_image(image_path, meme)
        
        if analysis:
            result = MemeAnalysisResult(
                **meme,
                analysis=analysis
            )
            results.append(result)
            print(f"  ✅ Analysis complete")
        else:
            print(f"  ❌ Analysis failed")
            failed_images.append(meme['id'])
    
    # Save results
    print(f"\nSaving results to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump([result.dict() for result in results], f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Analysis complete!")
    print(f"  - Successfully analyzed: {len(results)} memes")
    print(f"  - Failed: {len(failed_images)} memes")
    if failed_images:
        print(f"  - Failed IDs: {failed_images}")


async def main():
    """Main function to run the analysis."""
    
    # Set up paths
    script_dir = Path(__file__).parent
    csv_path = script_dir.parent / "data" / "uk_top_memes_last_24h.csv"
    images_dir = script_dir.parent / "data" / "uk_memes_images"
    output_path = script_dir.parent / "data" / "uk_memes_descriptions.json"
    
    # Check if files exist
    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        return
    
    if not images_dir.exists():
        print(f"❌ Images directory not found: {images_dir}")
        return
    
    print("🚀 Starting UK Meme Analysis")
    print(f"  - CSV: {csv_path}")
    print(f"  - Images: {images_dir}")
    print(f"  - Output: {output_path}")
    
    # Run analysis
    await process_all_memes(str(csv_path), str(images_dir), str(output_path))


if __name__ == "__main__":
    asyncio.run(main())
