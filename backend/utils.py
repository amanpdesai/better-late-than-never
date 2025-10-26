"""
Shared utilities for the Flask backend.
"""

import base64
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

from config import CLUSTER_DATA_PATHS


def load_cluster_data() -> Dict[str, Any]:
    """Load all cluster data from JSON files."""
    cluster_data = {}
    
    for name, path in CLUSTER_DATA_PATHS.items():
        if path.exists():
            try:
                # Handle JSONL files (like all_results.json)
                if name == "all_results":
                    data = {}
                    with open(path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            line = line.strip()
                            if line:
                                try:
                                    record = json.loads(line)
                                    url = record.get("url")
                                    if url:
                                        data[url] = record
                                except json.JSONDecodeError as e:
                                    print(f"⚠️ Skipping malformed JSON on line {line_num} of {path}: {e}")
                                    continue
                    cluster_data[name] = data
                # Handle text files (like meme_clusters_txt)
                elif name == "meme_clusters_txt":
                    cluster_data[name] = path.read_text(encoding='utf-8')
                # Handle regular JSON files
                else:
                    with open(path, 'r', encoding='utf-8') as f:
                        cluster_data[name] = json.load(f)
                print(f"✅ Loaded {name} from {path}")
            except Exception as e:
                print(f"⚠️ Failed to load {name} from {path}: {e}")
                cluster_data[name] = None
        else:
            print(f"⚠️ Cluster data file not found: {path}")
            cluster_data[name] = None
    
    return cluster_data


def encode_file_to_base64(file_path: Path) -> str:
    """Convert a file to base64 encoded string."""
    with open(file_path, 'rb') as f:
        file_data = f.read()
    return base64.b64encode(file_data).decode('utf-8')


def validate_prompt(prompt: str) -> tuple[bool, Optional[str]]:
    """Validate user prompt input."""
    if not prompt or not prompt.strip():
        return False, "Prompt cannot be empty"
    
    if len(prompt.strip()) < 3:
        return False, "Prompt must be at least 3 characters long"
    
    if len(prompt) > 1000:
        return False, "Prompt must be less than 1000 characters"
    
    return True, None


def create_error_response(message: str, code: str = "GENERATION_ERROR", status_code: int = 500) -> tuple[Dict[str, str], int]:
    """Create standardized error response."""
    return {
        "status": "error",
        "message": message,
        "code": code
    }, status_code


def create_success_response(content_type: str, data: str, metadata: Optional[Dict[str, Any]] = None) -> tuple[Dict[str, Any], int]:
    """Create standardized success response."""
    response = {
        "status": "success",
        "content_type": content_type,
        "data": data
    }
    
    if metadata:
        response["metadata"] = metadata
    
    return response, 200


def ensure_temp_file(filename: str) -> Path:
    """Ensure a temporary file path exists and return it."""
    from config import TEMP_DIR
    temp_file = TEMP_DIR / filename
    temp_file.parent.mkdir(parents=True, exist_ok=True)
    return temp_file


def cleanup_temp_files(pattern: str = "*") -> None:
    """Clean up temporary files matching pattern."""
    from config import TEMP_DIR
    import glob
    
    for file_path in glob.glob(str(TEMP_DIR / pattern)):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"⚠️ Failed to clean up {file_path}: {e}")


def timing_decorator(func):
    """Decorator to measure function execution time."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = round(end_time - start_time, 2)
        
        # Add timing to result if it's a dict
        if isinstance(result, dict):
            result["execution_time"] = execution_time
        
        return result
    return wrapper
