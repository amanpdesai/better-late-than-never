# Flask Backend for Meme Generation

This Flask backend provides an API for generating memes (both images and videos) using AI-powered cluster analysis and content generation.

## Features

- **Automatic Content Classification**: Uses OpenAI to determine whether to generate an image or video based on user prompts
- **Image Generation**: Creates memes using OpenAI's image generation API with cluster-based context
- **Video Generation**: Creates short-form videos using OpenAI's Sora API with meme cluster insights
- **Cluster Integration**: Leverages pre-built meme clusters for context-aware generation
- **RESTful API**: Simple JSON API for frontend integration

## Setup

### Prerequisites

- Python 3.8+
- OpenAI API key (required for content classification and generation)
- Gemini API key (optional, for enhanced image generation)

### Installation

1. Navigate to the backend directory:
   ```bash
   cd better-late-than-never/backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # Edit .env with your actual API keys
   nano .env  # or use your preferred editor
   ```

   Required environment variables in `.env`:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here  # Optional
   FLASK_DEBUG=True  # For development
   PORT=5000
   ```

4. Ensure cluster data files exist:
   - `../shorts-to-analysis/clustering/meme_clusters.json`
   - `../shorts-to-analysis/clustering/cluster_summaries.json`
   - `../shorts-to-analysis/clustering/all_results.json`
   - `../image-pipeline/meme_descriptions.json`

### Running the Server

**Option 1: Using the startup script**
```bash
./start.sh
```

**Option 2: Direct Python execution**
```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### POST /api/generate

Generate a meme based on user prompt.

**Request:**
```json
{
  "prompt": "Create a funny meme about American coffee culture"
}
```

**Response (Success):**
```json
{
  "status": "success",
  "content_type": "image",
  "data": "base64_encoded_image_data",
  "metadata": {
    "clusters_used": ["DESCRIPTION", "HUMOR", "TOPIC", "MEME_TEMPLATE"],
    "brand": "Lululemon",
    "tone": "playfully aspirational with dry humor",
    "prompt": "Create a funny meme about American coffee culture"
  }
}
```

**Response (Error):**
```json
{
  "status": "error",
  "message": "Error description",
  "code": "ERROR_CODE"
}
```

### GET /api/health

Check server health and cluster data status.

**Response:**
```json
{
  "status": "healthy",
  "cluster_data_loaded": true,
  "available_clusters": ["meme_clusters", "cluster_summaries", "all_results"]
}
```

### GET /api/clusters

Get detailed information about available cluster data.

## Frontend Integration

The frontend (`earth-3d/app/custom/usa-meme-generator/page.tsx`) has been updated to:

- Send prompts to the backend API
- Display loading states during generation
- Show generated images and videos
- Handle errors gracefully
- Show real-time pipeline progress

### Frontend Environment Setup

1. Navigate to the frontend directory:
   ```bash
   cd better-late-than-never/earth-3d
   ```

2. Set up environment variables:
   ```bash
   # Copy the example environment file
   cp env.local.example .env.local
   
   # Edit .env.local with your backend URL
   nano .env.local  # or use your preferred editor
   ```

   Required environment variables in `.env.local`:
   ```bash
   # For local development
   NEXT_PUBLIC_API_URL=http://localhost:5000
   
   # For production deployment
   # NEXT_PUBLIC_API_URL=https://your-backend-domain.com
   ```

3. Start the frontend:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

The frontend will automatically connect to the backend using the configured API URL.

## Architecture

### Content Classification
- Uses OpenAI GPT-4o-mini to analyze user prompts
- Determines whether to generate image or video based on keywords and context
- Defaults to image generation if ambiguous

### Image Generation Pipeline
1. Query meme clusters using Gemini API
2. Select top clusters based on keyword matching
3. Augment with centroid data from cluster analysis
4. Build context-aware prompt for OpenAI image generation
5. Generate and return base64-encoded image

### Video Generation Pipeline
1. Use GPT to select best clusters for each category
2. Build video generation prompt using cluster insights
3. Submit job to OpenAI Sora API
4. Poll until completion
5. Download and return base64-encoded video

## Configuration

Key configuration options in `config.py`:

- **OpenAI Models**: Content classifier, image generation, video generation
- **Gemini Model**: For cluster analysis
- **Video Settings**: Duration, resolution, polling interval
- **Default Values**: Brand, tone for meme generation

## Error Handling

The API provides comprehensive error handling:

- Input validation (prompt length, format)
- API key validation
- Cluster data availability checks
- Generation failure recovery
- Network error handling

## Development

### File Structure
```
backend/
├── app.py                 # Main Flask application
├── config.py             # Configuration constants
├── utils.py              # Shared utilities
├── content_classifier.py  # Content type classification
├── image_generator.py    # Image generation logic
├── video_generator.py    # Video generation logic
├── requirements.txt      # Python dependencies
├── start.sh             # Startup script
└── README.md            # This file
```

### Adding New Features

1. **New Content Types**: Extend `content_classifier.py` and add corresponding generators
2. **Additional Models**: Update `config.py` with new model configurations
3. **Enhanced Error Handling**: Add new error codes and messages in `utils.py`

## Troubleshooting

### Common Issues

1. **Missing Cluster Data**: Ensure all required JSON files exist in the correct paths
2. **API Key Errors**: Verify OpenAI and Gemini API keys are set correctly
3. **Generation Failures**: Check API quotas and rate limits
4. **Frontend Connection**: Ensure CORS is enabled and API URL is correct

### Debug Mode

Run with debug mode enabled:
```bash
export FLASK_DEBUG=True
python app.py
```

This will provide detailed error messages and auto-reload on code changes.
