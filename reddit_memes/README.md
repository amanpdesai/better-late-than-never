# Reddit Meme Analysis Pipeline

A comprehensive toolkit for scraping, analyzing, and clustering memes from Reddit with a focus on UK memes.

## 📁 Project Structure

```
reddit_memes/
├── scripts/                    # Main scraping and utility scripts
│   ├── get_memes.py          # General meme scraper
│   ├── get_uk_memes.py       # UK-specific meme scraper
│   ├── download_images.py     # Standalone image downloader
│   └── meme_utils.py         # Shared utilities
├── analysis/                  # Analysis and clustering scripts
│   ├── analyze_memes.py      # Image analysis with OpenAI Vision
│   ├── openai_embed_memes.py # Embedding generation and clustering
│   ├── analyze_clusters.py   # Cluster analysis and insights
│   └── visualize_clusters.py # Cluster visualization
├── data/                      # All data files
│   ├── uk_top_memes_last_24h.csv
│   ├── uk_memes_descriptions.json
│   ├── uk_memes_openai_clusters.json
│   └── uk_memes_images/      # Downloaded meme images
└── README.md
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install praw requests python-dotenv pydantic scikit-learn openai
```

### 2. Set Up Environment
Create a `.env` file with your API keys:
```bash
# Reddit API (get from https://www.reddit.com/prefs/apps)
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_user_agent

# OpenAI API (for analysis)
OPENAI_API_KEY=your_openai_key
# OR Azure OpenAI (for hackathon)
AZURE_OPENAI_API_KEY=your_azure_key
```

### 3. Scrape Memes
```bash
# General memes
python3 scripts/get_memes.py --download-images

# UK-specific memes
python3 scripts/get_uk_memes.py --download-images
```

### 4. Analyze Images
```bash
python3 analysis/analyze_memes.py
```

### 5. Generate Embeddings & Cluster
```bash
python3 analysis/openai_embed_memes.py
```

### 6. Analyze Results
```bash
python3 analysis/analyze_clusters.py
python3 analysis/visualize_clusters.py
```

## 📊 Features

### Scraping Scripts
- **`get_memes.py`**: Scrapes from popular meme subreddits
- **`get_uk_memes.py`**: UK-specific meme scraper with keyword filtering
- **`download_images.py`**: Standalone image downloader for existing data

### Analysis Pipeline
- **Image Analysis**: OpenAI Vision API for structured meme descriptions
- **Embedding Generation**: Multiple embedding models (3-small, 3-large, ada-002)
- **Clustering**: K-means clustering with optimal cluster selection
- **Visualization**: Interactive cluster exploration

### Data Management
- **CSV Export**: Structured meme metadata
- **Image Storage**: Organized image downloads
- **JSON Results**: Analysis and clustering outputs

## 🛠️ Usage Examples

### Basic Meme Scraping
```bash
# Scrape top 100 memes from last 24h
python3 scripts/get_memes.py --limit 100 --download-images

# Scrape specific subreddits
python3 scripts/get_memes.py --subreddits memes dankmemes --limit-per-sub 50
```

### UK Meme Analysis
```bash
# Scrape UK memes with filtering
python3 scripts/get_uk_memes.py --strict-uk --download-images

# Download images from existing data
python3 scripts/download_images.py data/uk_top_memes_last_24h.csv --output-dir uk_images
```

### Advanced Analysis
```bash
# Use different embedding models
python3 analysis/openai_embed_memes.py --model text-embedding-3-large --clusters 8

# Analyze specific clusters
python3 analysis/visualize_clusters.py --cluster 2 --limit 10
```

## 📈 Analysis Outputs

### Meme Descriptions
Each meme gets a structured description with:
- **Template**: Identified meme format
- **Text Content**: OCR of visible text
- **Visual Elements**: Description of components
- **Topic**: Main subject/theme
- **Humor Type**: Type of humor used
- **Context**: UK-specific references

### Clustering Results
- **Cluster Centers**: Representative memes for each cluster
- **Size Distribution**: Number of memes per cluster
- **Subreddit Analysis**: Distribution across source subreddits
- **Template Recognition**: Common meme formats identified

## 🔧 Configuration

### Scraping Options
- `--limit`: Total number of memes to scrape
- `--limit-per-sub`: Memes per subreddit
- `--subreddits`: Custom subreddit list
- `--download-images`: Enable image downloading
- `--min-upvotes`: Minimum upvote threshold

### Analysis Options
- `--model`: Embedding model selection
- `--clusters`: Number of clusters for K-means
- `--max-clusters`: Maximum clusters to test
- `--output-dir`: Custom output directory

## 📋 Requirements

### Python Packages
- `praw`: Reddit API client
- `requests`: HTTP requests for image downloading
- `python-dotenv`: Environment variable management
- `pydantic`: Data validation
- `scikit-learn`: Machine learning (clustering)
- `openai`: OpenAI API client

### API Keys Required
- **Reddit API**: Free, get credentials from Reddit
- **OpenAI API**: For image analysis and embeddings
- **Azure OpenAI**: Alternative for hackathon participants

## 🎯 Use Cases

### Research
- Meme trend analysis
- Cultural pattern recognition
- Humor classification
- Template evolution tracking

### Content Creation
- Meme inspiration
- Trend identification
- Audience analysis
- Content strategy

### Academic Study
- Digital culture research
- Humor theory analysis
- Social media patterns
- Cross-cultural comparisons

## 📝 Notes

- Images are automatically downloaded and organized
- All analysis results are saved as JSON for further processing
- The pipeline supports both personal OpenAI API and Azure OpenAI
- UK-specific filtering includes cultural keywords and subreddit selection
- Clustering uses multiple metrics to find optimal cluster count

## 🤝 Contributing

This is a research and analysis toolkit. Feel free to:
- Add new subreddit sources
- Implement additional analysis methods
- Improve clustering algorithms
- Add visualization features