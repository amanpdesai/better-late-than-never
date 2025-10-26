# Quick Start Guide

Get up and running with the data collection system in 5 steps.

## Step 1: Install Dependencies

```bash
cd data-collection
pip install -r requirements.txt
```

## Step 2: Get API Keys

### Required (Free Tier Available):
1. **Reddit API** - [Apply here](https://www.reddit.com/prefs/apps)
   - Create an app, get client ID and secret

2. **YouTube Data API** - [Get key here](https://console.cloud.google.com/)
   - Enable YouTube Data API v3
   - Create credentials → API key

3. **Supabase** - [Sign up](https://supabase.com/)
   - Create a new project
   - Get URL and anon/service keys

### Optional (For Better Data):
4. **Twitter API** - [Apply here](https://developer.twitter.com/)
5. **NewsAPI** - [Get key](https://newsapi.org/)
6. **OpenAI** - [Sign up](https://platform.openai.com/)

## Step 3: Configure Environment

Create `.env` file in `data-collection/`:

```bash
# Copy template
cat > .env << 'EOF'
# Reddit
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=MyGlobeApp/1.0

# YouTube
YOUTUBE_API_KEY=your_youtube_api_key

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_key

# Optional
TWITTER_BEARER_TOKEN=
NEWSAPI_KEY=
OPENAI_API_KEY=
EOF
```

## Step 4: Set Up Supabase Database

Run this SQL in your Supabase SQL Editor:

```sql
-- Countries table
CREATE TABLE countries (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL UNIQUE,
  code TEXT,
  flag_emoji TEXT,
  latitude NUMERIC,
  longitude NUMERIC,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Category data table
CREATE TABLE category_data (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  country_id UUID REFERENCES countries(id),
  category TEXT NOT NULL,
  data JSONB NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  last_updated TIMESTAMP DEFAULT NOW(),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_category_data_country ON category_data(country_id);
CREATE INDEX idx_category_data_category ON category_data(category);
CREATE INDEX idx_category_data_timestamp ON category_data(timestamp);

-- Content items table
CREATE TABLE content_items (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  category_data_id UUID REFERENCES category_data(id),
  item_id TEXT,
  title TEXT,
  content TEXT,
  source_platform TEXT,
  source_url TEXT,
  engagement_data JSONB,
  sentiment TEXT,
  virality_score NUMERIC,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Mood metrics table
CREATE TABLE mood_metrics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  country_id UUID REFERENCES countries(id),
  category TEXT,
  timestamp TIMESTAMP NOT NULL,
  joy NUMERIC,
  curiosity NUMERIC,
  anger NUMERIC,
  confusion NUMERIC,
  sadness NUMERIC,
  overall_sentiment TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Trending topics table
CREATE TABLE trending_topics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  country_id UUID REFERENCES countries(id),
  category TEXT,
  topic TEXT,
  volume NUMERIC,
  sentiment TEXT,
  trend TEXT,
  timestamp TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Insert sample countries
INSERT INTO countries (name, code, flag_emoji, latitude, longitude) VALUES
  ('USA', 'US', '🇺🇸', 37.0902, -95.7129),
  ('United Kingdom', 'GB', '🇬🇧', 55.3781, -3.4360),
  ('Canada', 'CA', '🇨🇦', 56.1304, -106.3468),
  ('India', 'IN', '🇮🇳', 20.5937, 78.9629),
  ('Australia', 'AU', '🇦🇺', -25.2744, 133.7751);
```

## Step 5: Run Your First Scraper

### Option A: Start with Memes (Using Existing Shorts Pipeline)

You already have a YouTube Shorts pipeline in `shorts-to-analysis/`. Let's adapt it:

```bash
# Navigate to memes scraper
cd memes/scripts

# Edit scraper.py to use your existing pipeline
# Then run it
python scraper.py --country USA

# Upload to Supabase
cd ../..
python upload_to_supabase.py --category memes --country USA
```

### Option B: Test with Mock Data

Create a test file `memes/output/USA/test.json`:

```json
{
  "country": "USA",
  "category": "memes",
  "timestamp": "2025-10-25T20:00:00Z",
  "last_updated": "2025-10-25T20:00:00Z",
  "items": [
    {
      "id": "test123",
      "title": "Test Meme",
      "content": "This is a test meme",
      "source_platform": "reddit",
      "source_url": "https://reddit.com/r/memes/test",
      "created_at": "2025-10-25T19:00:00Z",
      "engagement": {
        "likes": 5000,
        "comments": 200,
        "shares": 500,
        "views": 50000
      },
      "sentiment": "positive",
      "virality_score": 75
    }
  ],
  "summary": {
    "total_items": 1,
    "avg_engagement": 5000,
    "overall_sentiment": "positive",
    "top_topics": ["humor", "relatable"]
  }
}
```

Then upload it:

```bash
python upload_to_supabase.py --input memes/output/USA/test.json
```

## Step 6: Update Frontend

In your `earth-3d` project:

```bash
cd ../earth-3d

# Install Supabase client
npm install @supabase/supabase-js

# Create .env.local
cat > .env.local << 'EOF'
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
EOF
```

Create `earth-3d/lib/supabase.ts`:

```typescript
import { createClient } from '@supabase/supabase-js'

export const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)
```

Test fetching data:

```typescript
// In your component
import { supabase } from '@/lib/supabase'

const { data, error } = await supabase
  .from('category_data')
  .select('*')
  .eq('category', 'memes')
  .limit(1)

console.log('Data from Supabase:', data)
```

## Verification Checklist

- [ ] API keys configured in `.env`
- [ ] Supabase database created with tables
- [ ] Sample countries inserted
- [ ] Test data uploaded successfully
- [ ] Frontend can query Supabase
- [ ] CountryInfoPanel shows real data

## Common Issues

### "ModuleNotFoundError: No module named 'praw'"
```bash
pip install -r requirements.txt
```

### "Supabase connection failed"
- Check your `.env` file has correct SUPABASE_URL and SUPABASE_SERVICE_KEY
- Verify Supabase project is active

### "YouTube API quota exceeded"
- Free tier: 10,000 units/day
- Each search = ~100 units
- Reduce scraping frequency or upgrade

### "Reddit rate limit"
- Free tier: 60 requests/minute
- Add delays between requests
- Use `time.sleep(1)` between API calls

## Next Steps

1. **Implement one scraper fully** - Get end-to-end working
2. **Add sentiment analysis** - Use OpenAI or local models
3. **Calculate virality scores** - Based on engagement metrics
4. **Automate scraping** - Set up cron jobs
5. **Scale to more categories** - Add politics, economics, etc.

## Need Help?

- Check [README.md](./README.md) for detailed documentation
- See [FRONTEND_INTEGRATION.md](./FRONTEND_INTEGRATION.md) for frontend setup
- Review [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) for overall architecture

## Example: Full Workflow

```bash
# 1. Scrape memes for USA
cd memes/scripts
python scraper.py --country USA

# 2. Upload to Supabase
cd ../..
python upload_to_supabase.py --category memes --country USA

# 3. Verify in frontend
cd ../earth-3d
npm run dev
# Click on USA on the globe
# Select "Memes" category
# See real data!
```

That's it! You're now collecting and displaying real-time global mood data. 🌍
