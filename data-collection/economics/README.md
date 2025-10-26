# Economics Data Scraper

Scrapes economic data from 100% free sources.

## Features

- ✅ **World Bank API** - GDP, inflation, unemployment (no API key needed!)
- ✅ **Google Finance** - Stock indices, top gainers (Selenium scraping)
- ✅ **Google News** - Economic news headlines (Selenium scraping)
- ✅ **Sentiment Analysis** - Analyzes economic sentiment from news

## Installation

```bash
# Install dependencies
cd data-collection
pip install -r requirements.txt

# Install ChromeDriver (for Selenium)
brew install chromedriver  # macOS
# OR download from: https://chromedriver.chromium.org/
```

## Usage

```bash
cd economics/scripts

# Scrape data for USA
python scraper.py --country USA

# Scrape data for UK
python scraper.py --country UK

# Specify custom output directory
python scraper.py --country India --output /path/to/output/
```

## Supported Countries

- USA
- UK (United Kingdom)
- India
- Canada
- Australia
- Germany
- France
- Japan
- Brazil
- Mexico
- Spain
- Italy

## Output Format

The scraper saves data to `output/{country}/{date}.json`:

```json
{
  "country": "USA",
  "category": "economics",
  "timestamp": "2025-10-25T20:00:00Z",
  "economic_indicators": {
    "gdp_growth": {
      "value": 2.5,
      "year": "2023",
      "trend": "up",
      "unit": "%"
    },
    "inflation_rate": {
      "value": 3.2,
      "year": "2024",
      "trend": "down",
      "unit": "%"
    },
    "unemployment_rate": {
      "value": 3.8,
      "year": "2024",
      "trend": "stable",
      "unit": "%"
    },
    "stock_index": {
      "name": "S&P 500",
      "value": 4785.23,
      "change_pct": 0.52,
      "trend": "up"
    }
  },
  "market_data": {
    "top_gainers": [
      {
        "symbol": "NVDA",
        "name": "NVIDIA Corp",
        "price": "485.50",
        "change_pct": 3.2
      }
    ]
  },
  "news_headlines": [
    {
      "headline": "Fed holds rates steady...",
      "source": "CNN",
      "url": "https://...",
      "sentiment": "neutral",
      "timestamp": "2025-10-25T20:00:00Z"
    }
  ],
  "sentiment": {
    "overall": "neutral",
    "score": 50,
    "breakdown": {
      "positive": 3,
      "neutral": 5,
      "negative": 2
    }
  }
}
```

## Data Sources

1. **World Bank Open Data API**
   - URL: https://api.worldbank.org/v2/
   - 100% free, no authentication required
   - Provides: GDP, inflation, unemployment

2. **Google Finance**
   - URL: https://www.google.com/finance/
   - Scraped with Selenium
   - Provides: Stock indices, top gainers

3. **Google News**
   - URL: https://www.google.com/search?q={country}+economy+news&tbm=nws
   - Scraped with Selenium
   - Provides: Economic news headlines

## How It Works

1. **Fetches World Bank Data** - Gets latest GDP, inflation, unemployment via API
2. **Scrapes Google Finance** - Gets stock index and top gainers
3. **Scrapes Economic News** - Gets latest news from Google News
4. **Analyzes Sentiment** - Simple keyword-based sentiment analysis
5. **Saves to JSON** - Stores all data in structured JSON format

## Troubleshooting

### "ChromeDriver not found"
```bash
# macOS
brew install chromedriver

# Or download manually from:
# https://chromedriver.chromium.org/
```

### "World Bank API slow"
The World Bank API can be slow sometimes. The scraper has a 10-second timeout.

### "Google blocked the request"
Add delays between requests or run less frequently. The scraper already includes 2-second delays.

## Next Steps

1. **Test the scraper:**
   ```bash
   python scraper.py --country USA
   ```

2. **Check the output:**
   ```bash
   cat ../output/USA/2025-10-25.json
   ```

3. **Upload to Supabase:**
   ```bash
   cd ../../
   python upload_to_supabase.py --category economics --country USA
   ```

## Cost

**$0/month** - All data sources are 100% free!
