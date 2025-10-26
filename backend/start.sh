#!/bin/bash

# Startup script for the Flask backend

echo "🚀 Starting Flask Backend for Meme Generation"
echo "============================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the backend directory."
    exit 1
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️ Warning: .env file not found."
    echo "📝 Please copy env.example to .env and fill in your API keys:"
    echo "   cp env.example .env"
    echo "   # Then edit .env with your actual API keys"
fi

# Check for required environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️ Warning: OPENAI_API_KEY not set. Video generation will not work."
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️ Warning: GEMINI_API_KEY not set. Image generation may not work optimally."
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Create necessary directories
mkdir -p outputs temp

echo "🌐 Starting Flask server..."
echo "📡 API will be available at: http://localhost:5000"
echo "🔗 Frontend should connect to: http://localhost:5000/api/generate"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the Flask app
python app.py
