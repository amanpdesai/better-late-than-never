"""
Configuration constants for the Flask backend.
"""

import os
from pathlib import Path

# Base paths
BACKEND_DIR = Path(__file__).parent
PROJECT_ROOT = BACKEND_DIR.parent

# Cluster data paths (now using local backend data)
CLUSTER_DATA_PATHS = {
    "meme_clusters": BACKEND_DIR / "data" / "clustering" / "meme_clusters.json",
    "cluster_summaries": BACKEND_DIR / "data" / "clustering" / "cluster_summaries.json", 
    "all_results": BACKEND_DIR / "data" / "clustering" / "all_results.json",
    "meme_descriptions": BACKEND_DIR / "data" / "image-pipeline" / "meme_descriptions.json",
    "output_with_centroid": BACKEND_DIR / "data" / "image-pipeline" / "output_with_centroid.json",
    "cluster_labels_dict": BACKEND_DIR / "data" / "image-pipeline" / "cluster_labels_dict.json",
    "meme_clusters_txt": BACKEND_DIR / "data" / "image-pipeline" / "meme_clusters.txt"
}

# Output directories
OUTPUT_DIR = BACKEND_DIR / "outputs"
TEMP_DIR = BACKEND_DIR / "temp"

# OpenAI settings (with environment variable fallbacks)
OPENAI_MODELS = {
    "content_classifier": os.getenv("OPENAI_MODEL_CONTENT_CLASSIFIER", "gpt-4o-mini"),
    "image_generation": os.getenv("OPENAI_MODEL_IMAGE_GENERATION", "gpt-image-1"), 
    "video_generation": os.getenv("OPENAI_MODEL_VIDEO_GENERATION", "sora-2")
}

# Gemini settings
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Video generation settings
VIDEO_DURATION_SECONDS = os.getenv("VIDEO_DURATION_SECONDS", "8")
VIDEO_RESOLUTION = os.getenv("VIDEO_RESOLUTION", "720x1280")
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "10"))

# Image generation settings
DEFAULT_BRAND = os.getenv("DEFAULT_BRAND", "Lululemon")
DEFAULT_TONE = os.getenv("DEFAULT_TONE", "playfully aspirational with dry humor")

# Flask settings
FLASK_PORT = int(os.getenv("PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
FLASK_ENV = os.getenv("FLASK_ENV", "development")

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Ensure output directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
