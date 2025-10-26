# Data Collection System

This directory contains scrapers for collecting country-specific data across multiple categories to power the 3D globe visualization frontend.

## Categories

### 1. Memes
**What people are laughing about**
- Reddit (r/memes, country-specific meme subreddits)
- Twitter/X trending memes
- Instagram/TikTok viral content
- Outputs: Viral memes, engagement metrics, sentiment

### 2. Economics
**What people are worried about economically**
- Economic indicators (GDP, inflation, unemployment)
- Financial news (Bloomberg, Reuters, etc.)
- Reddit finance communities
- Twitter economic discussions
- Outputs: Economic news, concern metrics, trending topics

### 3. Politics
**What people are worried about politically**
- Political news from major outlets
- Reddit political communities
- Twitter political discussions
- Government press releases
- Outputs: Political news, sentiment, polarization metrics

### 4. News
**General current events**
- News aggregators (NewsAPI, Google News)
- Major news outlets (BBC, CNN, Reuters)
- Reddit news communities
- Outputs: Top stories, trending topics, category breakdown

### 5. Google Trends
**What people are searching for**
- Google Trends API (trending searches)
- Interest over time
- Rising queries
- YouTube trending videos
- Outputs: Top searches, trending topics, breakout searches

### 6. YouTube
**What people are watching**
- YouTube trending videos
- YouTube Shorts
- Viral content across all categories
- Top creators
- Outputs: Trending videos/shorts, engagement, viral content

### 7. Sports
**Sports news and discussions**
- Sports news (ESPN, BBC Sport, etc.)
- Reddit sports communities
- Live scores and updates
- Twitter sports discussions
- Outputs: Sports news, scores, trending events

## Directory Structure

```
data-collection/
├── README.md
├── memes/
│   ├── scripts/
│   │   └── scraper.py
│   ├── schemas/
│   │   └── output_schema.json
│   └── output/
│       └── {country}/
│           └── {date}.json
├── economics/
│   ├── scripts/
│   ├── schemas/
│   └── output/
├── politics/
│   ├── scripts/
│   ├── schemas/
│   └── output/
├── news/
│   ├── scripts/
│   ├── schemas/
│   └── output/
├── google-trends/
│   ├── scripts/
│   ├── schemas/
│   └── output/
├── youtube/
│   ├── scripts/
│   ├── schemas/
│   └── output/
└── sports/
    ├── scripts/
    ├── schemas/
    └── output/
```

## Data Flow

1. **Scraping** → Run scrapers to collect data from various sources
2. **Processing** → Normalize, clean, and enrich data
3. **Storage** → Save to JSON files organized by country and date
4. **Database** → Upload to Supabase for frontend consumption
5. **Frontend** → Display on 3D globe visualization

## Common Data Schema

All scrapers output data in a consistent format:

```json
{
  "country": "USA",
  "category": "memes|economics|politics|news|google_trends|youtube|sports",
  "timestamp": "2025-10-25T20:00:00Z",
  "last_updated": "2025-10-25T20:00:00Z",
  "items": [...],
  "summary": {...}
}
```

## Frontend Integration

The data collected here will be displayed in the [CountryInfoPanel](../../earth-3d/components/country-info-panel.tsx):

- **Category selector** → Switch between data categories
- **Representative content** → Display top items from each category
- **Mood meter** → Based on sentiment analysis
- **Top topics** → Trending keywords/topics
- **Engagement stats** → Aggregated metrics

## Supabase Schema

Tables needed:
- `country_data` - Main table with country info
- `memes` - Meme content by country
- `economics` - Economic news and metrics
- `politics` - Political news and sentiment
- `news` - General news articles
- `google_trends` - Search trends
- `youtube` - Video content
- `sports` - Sports news and scores

## Implementation Plan

### Phase 1: Core Infrastructure
1. Set up API credentials for all data sources
2. Implement base scraper class with common functionality
3. Set up Supabase database schema
4. Create data validation and error handling

### Phase 2: Category Scrapers
1. Implement memes scraper (already have YouTube Shorts pipeline)
2. Implement economics scraper
3. Implement politics scraper
4. Implement news scraper
5. Implement Google Trends scraper
6. Implement YouTube scraper
7. Implement sports scraper

### Phase 3: Data Processing
1. Sentiment analysis pipeline
2. Virality score calculation
3. Topic extraction and trending analysis
4. Data aggregation and summarization

### Phase 4: Database & Frontend
1. Upload data to Supabase
2. Create API endpoints
3. Update frontend to consume real data
4. Add real-time updates

### Phase 5: Automation
1. Schedule scrapers (cron jobs)
2. Implement rate limiting
3. Set up monitoring and alerts
4. Add caching layer

## API Keys Required

- Reddit API (PRAW)
- Twitter/X API
- YouTube Data API v3
- NewsAPI.org
- Google Trends (pytrends)
- Financial data APIs (optional)
- OpenAI/Anthropic for sentiment analysis

## Running Scrapers

```bash
# Install dependencies
pip install -r requirements.txt

# Run a specific scraper
python data-collection/memes/scripts/scraper.py --country USA

# Run all scrapers
python run_all_scrapers.py

# Upload to Supabase
python upload_to_supabase.py
```

## Notes

- Rate limiting is crucial for all APIs
- Some data sources may require paid subscriptions
- Consider time zones for different countries
- Implement caching to reduce API calls
- Add error handling and retry logic
- Monitor API quotas and usage
