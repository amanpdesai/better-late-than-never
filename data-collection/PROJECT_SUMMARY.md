# Data Collection Project Summary

## Overview

This project collects real-time data about what people around the world are:
- **Laughing about** (Memes)
- **Worried about** (Economics, Politics, News)
- **Searching for** (Google Trends)
- **Watching** (YouTube videos & Shorts, Sports)

The data powers a 3D globe visualization showing the mood and interests of different countries.

## Project Structure

```
data-collection/
├── README.md                      # Main documentation
├── PROJECT_SUMMARY.md             # This file
├── FRONTEND_INTEGRATION.md        # Frontend integration guide
├── common_schema.json             # Unified data schema
├── requirements.txt               # Python dependencies
├── run_all_scrapers.py           # Master orchestration script
├── upload_to_supabase.py         # Database upload script
│
├── memes/                         # What people are laughing about
│   ├── scripts/
│   │   └── scraper.py            # Reddit, Twitter, Instagram, TikTok memes
│   ├── schemas/
│   │   └── output_schema.json
│   └── output/
│       └── {country}/
│           └── {date}.json
│
├── economics/                     # What people are worried about (money)
│   ├── scripts/
│   │   └── scraper.py            # Financial news, economic indicators
│   ├── schemas/
│   └── output/
│
├── politics/                      # What people are worried about (politics)
│   ├── scripts/
│   │   └── scraper.py            # Political news, discussions
│   ├── schemas/
│   └── output/
│
├── news/                          # General current events
│   ├── scripts/
│   │   └── scraper.py            # News aggregators, major outlets
│   ├── schemas/
│   └── output/
│
├── google-trends/                 # What people are searching for
│   ├── scripts/
│   │   └── scraper.py            # Google Trends API, trending searches
│   ├── schemas/
│   └── output/
│
├── youtube/                       # What people are watching
│   ├── scripts/
│   │   └── scraper.py            # Trending videos, YouTube Shorts
│   ├── schemas/
│   └── output/
│
└── sports/                        # Sports news and events
    ├── scripts/
    │   └── scraper.py            # Sports news, scores, highlights
    ├── schemas/
    └── output/
```

## Data Categories

| Category | What It Shows | Data Sources | Refresh Rate |
|----------|---------------|--------------|--------------|
| **Memes** | What people are laughing about | Reddit, Twitter, Instagram, TikTok | 2 hours |
| **Economics** | Economic worries & concerns | Financial news, World Bank, Reddit, Twitter | 6 hours |
| **Politics** | Political discussions & sentiment | News outlets, Reddit, Twitter | 2 hours |
| **News** | General current events | NewsAPI, Google News, major outlets | 1 hour |
| **Google Trends** | What people are searching | Google Trends API, YouTube trending | 30 min |
| **YouTube** | What people are watching | YouTube API, trending videos/Shorts | 1 hour |
| **Sports** | Sports news & events | ESPN, sports outlets, Reddit, Twitter | 2 hours |

## Data Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                      DATA COLLECTION                         │
│                                                              │
│  Reddit  Twitter  YouTube  Google  News APIs  Instagram     │
│    │        │       │        │         │          │         │
│    └────────┴───────┴────────┴─────────┴──────────┘         │
│                           │                                  │
└───────────────────────────┼──────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  SCRAPER SCRIPTS (Python)                    │
│                                                              │
│  • Fetch data from APIs                                     │
│  • Normalize & clean data                                   │
│  • Sentiment analysis                                       │
│  • Calculate virality scores                                │
│  • Extract trending topics                                  │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   JSON OUTPUT FILES                          │
│                                                              │
│  {category}/output/{country}/{date}.json                    │
│                                                              │
│  Example: memes/output/USA/2025-10-25.json                  │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│               SUPABASE (PostgreSQL Database)                 │
│                                                              │
│  Tables:                                                     │
│  • countries                                                 │
│  • category_data                                            │
│  • content_items                                            │
│  • mood_metrics                                             │
│  • trending_topics                                          │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  NEXT.JS FRONTEND (earth-3d)                 │
│                                                              │
│  • Fetch data from Supabase                                 │
│  • Display on 3D globe                                      │
│  • CountryInfoPanel shows detailed data                     │
│  • Real-time updates (optional)                             │
└─────────────────────────────────────────────────────────────┘
```

## Common Data Schema

Every scraper outputs data in this format:

```json
{
  "country": "USA",
  "category": "memes|economics|politics|news|google_trends|youtube|sports",
  "timestamp": "2025-10-25T20:00:00Z",
  "last_updated": "2025-10-25T20:00:00Z",
  "items": [
    {
      "id": "unique_id",
      "title": "Item title",
      "content": "Item content/description",
      "source_platform": "reddit|twitter|youtube|etc",
      "source_url": "https://...",
      "created_at": "2025-10-25T18:00:00Z",
      "engagement": {
        "likes": 15000,
        "comments": 500,
        "shares": 2000,
        "views": 100000
      },
      "sentiment": "positive|negative|neutral",
      "virality_score": 85
    }
  ],
  "summary": {
    "total_items": 50,
    "avg_engagement": 12500,
    "overall_sentiment": "positive",
    "top_topics": ["topic1", "topic2", "topic3"]
  }
}
```

## Implementation Phases

### ✅ Phase 1: Planning & Structure (COMPLETED)
- [x] Create folder structure
- [x] Document scraping requirements for each category
- [x] Design unified data schema
- [x] Plan frontend integration
- [x] Create master orchestration script
- [x] Create database upload script

### 🔄 Phase 2: Core Infrastructure (NEXT)
- [ ] Set up API credentials (Reddit, Twitter, YouTube, etc.)
- [ ] Create base scraper class with common functionality
- [ ] Set up Supabase project and database schema
- [ ] Implement data validation and error handling
- [ ] Set up logging and monitoring

### 📋 Phase 3: Implement Scrapers
- [ ] Memes scraper (leverage existing YouTube Shorts pipeline)
- [ ] Economics scraper
- [ ] Politics scraper
- [ ] News scraper
- [ ] Google Trends scraper
- [ ] YouTube scraper
- [ ] Sports scraper

### 📋 Phase 4: Data Processing
- [ ] Sentiment analysis pipeline
- [ ] Virality score calculation
- [ ] Topic extraction and trending analysis
- [ ] Data aggregation and summarization
- [ ] Mood meter calculation

### 📋 Phase 5: Database & Frontend
- [ ] Create Supabase tables
- [ ] Test data upload to Supabase
- [ ] Update frontend TypeScript interfaces
- [ ] Create API functions to fetch data
- [ ] Update CountryInfoPanel component
- [ ] Add loading states and error handling

### 📋 Phase 6: Automation & Production
- [ ] Set up cron jobs for scheduled scraping
- [ ] Implement rate limiting
- [ ] Add monitoring and alerts
- [ ] Set up caching layer
- [ ] Deploy scrapers to cloud (AWS Lambda, GCP, etc.)

## Getting Started

### 1. Install Dependencies

```bash
cd data-collection
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file:

```bash
# API Keys
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_user_agent

TWITTER_BEARER_TOKEN=your_twitter_bearer_token

YOUTUBE_API_KEY=your_youtube_api_key

NEWSAPI_KEY=your_newsapi_key

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key

# OpenAI (for sentiment analysis)
OPENAI_API_KEY=your_openai_api_key
```

### 3. Implement First Scraper

Start with memes since you already have the YouTube Shorts pipeline:

```bash
cd memes/scripts
# Edit scraper.py and implement the scraping logic
python scraper.py --country USA
```

### 4. Test Data Upload

```bash
python upload_to_supabase.py --category memes --country USA
```

### 5. Run All Scrapers

```bash
python run_all_scrapers.py --mode quick
```

## Countries to Track

**High Priority:**
- USA, UK, Canada, India, Australia

**Medium Priority:**
- Germany, France, Japan, Brazil

**Low Priority:**
- Mexico, Spain, Italy, Netherlands, South Korea

## API Keys Required

| Service | Purpose | Free Tier | Cost |
|---------|---------|-----------|------|
| Reddit API | Memes, discussions | ✅ 60 req/min | Free |
| Twitter API | Tweets, trends | ⚠️ Limited | $100/mo |
| YouTube API | Videos, Shorts | ✅ 10k units/day | Free |
| NewsAPI | News articles | ✅ 100 req/day | $449/mo |
| Google Trends | Trending searches | ✅ Unlimited | Free |
| Supabase | Database | ✅ 500MB | Free |
| OpenAI | Sentiment analysis | ⚠️ Limited | Pay-as-go |

## Success Metrics

- **Data Coverage**: 15+ countries across 7 categories
- **Update Frequency**: Data refreshed every 30 min - 6 hours
- **Data Quality**: 90%+ successful scrapes
- **Frontend Performance**: <2s load time
- **User Engagement**: Interactive globe with real-time data

## Next Steps

1. **Set up Supabase project** - Create database and tables
2. **Get API keys** - Sign up for all required services
3. **Implement memes scraper** - Start with one category
4. **Test end-to-end flow** - Scrape → Store → Display
5. **Scale to all categories** - Implement remaining scrapers
6. **Automate & Deploy** - Set up scheduled jobs

## Notes

- Start simple: One category, one country
- Iterate quickly: Get something working end-to-end
- Scale gradually: Add more categories and countries
- Monitor usage: Watch API quotas and costs
- Handle errors: Implement retry logic and fallbacks
- Cache aggressively: Reduce API calls and costs

## Resources

- [Reddit API Docs](https://www.reddit.com/dev/api/)
- [Twitter API Docs](https://developer.twitter.com/en/docs)
- [YouTube Data API](https://developers.google.com/youtube/v3)
- [NewsAPI Docs](https://newsapi.org/docs)
- [Google Trends API (pytrends)](https://github.com/GeneralMills/pytrends)
- [Supabase Docs](https://supabase.com/docs)

---

**Created:** October 25, 2025
**Status:** Phase 1 Complete - Ready for Implementation
