"""
Flask backend for meme generation API.
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from config import CLUSTER_DATA_PATHS, FLASK_PORT, FLASK_DEBUG
from utils import load_cluster_data, validate_prompt, create_error_response, create_success_response
from content_classifier import classify_content_type
from image_generator import ImageGenerator
from video_generator import VideoGenerator

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Global variables for loaded data
cluster_data = None
image_generator = None
video_generator = None


def initialize_backend():
    """Initialize the backend by loading cluster data and creating generators."""
    global cluster_data, image_generator, video_generator
    
    print("🚀 Initializing Flask backend...")
    
    # Load cluster data
    print("📊 Loading cluster data...")
    cluster_data = load_cluster_data()
    
    # Check if we have the required data
    required_files = ["meme_clusters", "cluster_summaries", "all_results"]
    missing_files = [f for f in required_files if cluster_data.get(f) is None]
    
    if missing_files:
        print(f"⚠️ Missing required cluster data files: {missing_files}")
        print("Some features may not work properly.")
    else:
        print("✅ All required cluster data loaded successfully")
    
    # Initialize generators
    image_generator = ImageGenerator(cluster_data)
    video_generator = VideoGenerator(cluster_data)
    
    print("✅ Backend initialization complete")


@app.route('/api/generate', methods=['POST'])
def generate_meme():
    """
    Main endpoint for meme generation.
    
    Expected JSON payload:
    {
        "prompt": "User's natural language prompt"
    }
    
    Returns:
    {
        "status": "success" | "error",
        "content_type": "image" | "video",
        "data": "base64_encoded_content",
        "metadata": {...},
        "stages": [
            {"id": 1, "name": "Understanding", "status": "completed", "description": "..."},
            {"id": 2, "name": "Concept", "status": "completed", "description": "..."},
            {"id": 3, "name": "Text", "status": "completed", "description": "..."},
            {"id": 4, "name": "Design", "status": "completed", "description": "..."}
        ]
    }
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify(create_error_response("Request must be JSON", "INVALID_REQUEST", 400))
        
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify(create_error_response("Missing 'prompt' field", "MISSING_PROMPT", 400))
        
        prompt = data['prompt']
        
        # Validate prompt
        is_valid, error_msg = validate_prompt(prompt)
        if not is_valid:
            return jsonify(create_error_response(error_msg, "INVALID_PROMPT", 400))
        
        print(f"🎯 Received prompt: {prompt}")
        
        # Initialize stages
        stages = [
            {"id": 1, "name": "Understanding", "status": "running", "description": "Analyzing your request"},
            {"id": 2, "name": "Concept", "status": "pending", "description": "Generating meme concept"},
            {"id": 3, "name": "Text", "status": "pending", "description": "Crafting witty text"},
            {"id": 4, "name": "Design", "status": "pending", "description": "Finalizing meme design"}
        ]
        
        # Stage 1: Understanding (Content Classification)
        print("🎯 Stage 1: Understanding - Classifying content type...")
        content_type = classify_content_type(prompt)
        print(f"🎯 Classified as: {content_type}")
        stages[0]["status"] = "completed"
        stages[0]["description"] = f"Classified as {content_type} generation"
        
        # Stage 2: Concept (Cluster Selection)
        print("🎯 Stage 2: Concept - Selecting relevant clusters...")
        stages[1]["status"] = "running"
        stages[1]["description"] = "Selecting relevant meme clusters"
        
        # Generate content based on classification
        if content_type == "image":
            result = image_generator.generate_image(prompt)
        elif content_type == "video":
            result = video_generator.generate_video(prompt)
        else:
            return jsonify(create_error_response(f"Unknown content type: {content_type}", "UNKNOWN_CONTENT_TYPE", 500))
        
        # Update stages based on result
        if result["status"] == "success":
            stages[1]["status"] = "completed"
            stages[1]["description"] = "Selected relevant clusters"
            stages[2]["status"] = "completed"
            stages[2]["description"] = "Generated contextual text"
            stages[3]["status"] = "completed"
            stages[3]["description"] = f"Created {content_type} meme"
            
            response_data, status_code = create_success_response(
                result["content_type"],
                result["data"],
                result.get("metadata", {})
            )
            response_data["stages"] = stages
            return jsonify(response_data)
        else:
            # Mark stages as failed
            for stage in stages:
                if stage["status"] == "running":
                    stage["status"] = "failed"
                    stage["description"] = "Generation failed"
            
            error_response, status_code = create_error_response(
                result["message"],
                result.get("code", "GENERATION_ERROR"),
                500
            )
            error_response["stages"] = stages
            return jsonify(error_response)
    
    except Exception as e:
        print(f"❌ Unexpected error in generate_meme: {e}")
        return jsonify(create_error_response(f"Internal server error: {str(e)}", "INTERNAL_ERROR", 500))


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "cluster_data_loaded": cluster_data is not None,
        "available_clusters": list(cluster_data.keys()) if cluster_data else []
    })


@app.route('/api/clusters', methods=['GET'])
def get_cluster_info():
    """Get information about available clusters."""
    if not cluster_data:
        return jsonify(create_error_response("Cluster data not loaded", "NO_CLUSTER_DATA", 503))
    
    cluster_info = {}
    for name, data in cluster_data.items():
        if data is not None:
            if isinstance(data, dict):
                cluster_info[name] = {
                    "type": "dict",
                    "keys": list(data.keys()) if data else [],
                    "size": len(data)
                }
            elif isinstance(data, list):
                cluster_info[name] = {
                    "type": "list", 
                    "size": len(data)
                }
            else:
                cluster_info[name] = {
                    "type": type(data).__name__,
                    "size": "unknown"
                }
        else:
            cluster_info[name] = {
                "type": "missing",
                "size": 0
            }
    
    return jsonify({
        "status": "success",
        "clusters": cluster_info
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify(create_error_response("Endpoint not found", "NOT_FOUND", 404))


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify(create_error_response("Method not allowed", "METHOD_NOT_ALLOWED", 405))


@app.errorhandler(500)
def internal_error(error):
    return jsonify(create_error_response("Internal server error", "INTERNAL_ERROR", 500))


if __name__ == '__main__':
    # Initialize backend
    initialize_backend()
    
    # Get configuration from environment
    port = int(os.getenv('PORT', FLASK_PORT))  # Render uses PORT env var
    debug = FLASK_DEBUG
    
    print(f"🌐 Starting Flask server on port {port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"📡 API endpoint: http://localhost:{port}/api/generate")
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=debug)
