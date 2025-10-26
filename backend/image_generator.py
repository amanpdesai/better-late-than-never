"""
Image generation module using exact replica of image-pipeline-main.py
"""

import base64
from pathlib import Path
from typing import Dict, Any

from config import DEFAULT_BRAND, DEFAULT_TONE
from image_pipeline_replica import ImagePipelineOrchestrator


class ImageGenerator:
    """Handles image generation using exact replica of image-pipeline-main.py."""
    
    def __init__(self, cluster_data: Dict[str, Any]):
        self.cluster_data = cluster_data
        self.orchestrator = ImagePipelineOrchestrator()
    
    def generate_image(self, prompt: str, brand: str = DEFAULT_BRAND, 
                      tone: str = DEFAULT_TONE) -> Dict[str, Any]:
        """
        Generate an image meme using the exact image-pipeline-main.py logic.
        
        Args:
            prompt: User's natural language prompt
            brand: Brand name for the meme
            tone: Tone description for the meme
            
        Returns:
            Dict containing base64 image data and metadata
        """
        try:
            print("🚀 Running image pipeline replica...")
            
            # Run the exact pipeline replica (starting from step 5 = query step)
            result = self.orchestrator.run_pipeline(
                question=prompt,
                start_from=4,  # Skip steps 1-4, start from query step
                meme_brand=brand,
                meme_tone=tone,
                meme_model="gpt-image-1",
                top_k=3,
                model="gemini-2.5-flash-lite",
                random_count=2
            )
            
            if result["status"] != "success":
                return result
            
            # Convert generated image to base64
            image_path = Path(result["file_path"])
            with open(image_path, 'rb') as f:
                image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Clean up temp file
            if image_path.exists():
                image_path.unlink()
            
            return {
                "status": "success",
                "content_type": "image",
                "data": image_base64,
                "metadata": {
                    "brand": brand,
                    "tone": tone,
                    "prompt": prompt,
                    "pipeline_version": "image-pipeline-main.py-exact-replica"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Image generation failed: {str(e)}",
                "code": "IMAGE_GENERATION_FAILED"
            }