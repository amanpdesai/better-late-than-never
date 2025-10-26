"""
Video generation module using exact replica of generate_video.py
"""

from typing import Dict, Any
from video_generator_replica import VideoGeneratorReplica


class VideoGenerator:
    """Handles video generation using exact replica of generate_video.py."""
    
    def __init__(self, cluster_data: Dict[str, Any]):
        self.cluster_data = cluster_data
        self.replica = VideoGeneratorReplica(cluster_data)
    
    def generate_video(self, prompt: str, use_simple_mode: bool = False) -> Dict[str, Any]:
        """
        Generate a video meme.

        Args:
            prompt: User's natural language prompt
            use_simple_mode: If True, uses simple direct prompt (no cluster context).
                           If False (DEFAULT), uses YouTube shorts clusters + Gemini sanitization.

        Returns:
            Dict containing base64 video data and metadata

        The default mode uses real trending YouTube shorts data with intelligent
        Gemini-powered sanitization to prevent OpenAI moderation blocks while
        preserving the user's creative intent.
        """
        return self.replica.generate_video(prompt, use_simple_mode=use_simple_mode)