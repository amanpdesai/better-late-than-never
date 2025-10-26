# 100% FREE Data Sources Guide

**Goal:** Collect all data using only FREE sources - no paid APIs, no rate-limited APIs that cost money.

**Primary Methods:**
1. **Selenium Web Scraping** - Our main tool
2. **Free APIs** - Only truly free APIs (no credit card, no paid tiers)
3. **Google Search Scraping** - Using Selenium to scrape Google results

---

## 1. 💰 ECONOMICS

### ✅ FREE Data Sources

#### Google Finance (Selenium Scraping)
```
URL: https://www.google.com/finance/
Scrape:
- Stock indices (S&P 500, FTSE, Nifty, etc.)
- Top gainers/losers
- Currency exchange rates
- Market summary
```

#### Trading Economics (Selenium Scraping)
```
URL: https://tradingeconomics.com/{country}/indicators
Scrape:
- GDP growth rate
- Inflation rate (CPI)
- Unemployment rate
- Interest rates
- Economic forecasts
```

#### Yahoo Finance (Selenium Scraping - No API needed)
```
URL: https://finance.yahoo.com/
Scrape:
- Stock prices and indices
- Market data
- Economic news headlines
```

#### World Bank Open Data (100% Free API - No Key Needed!)
```
URL: https://api.worldbank.org/v2/
No authentication required!

Examples:
- GDP: https://api.worldbank.org/v2/country/US/indicator/NY.GDP.MKTP.CD.ZS?format=json
- Inflation: https://api.worldbank.org/v2/country/US/indicator/FP.CPI.TOTL.ZG?format=json
- Unemployment: https://api.worldbank.org/v2/country/US/indicator/SL.UEM.TOTL.ZS?format=json
```

#### Google Search (Selenium)
```
Search queries:
- "{country} GDP 2025"
- "{country} inflation rate"
- "{country} unemployment rate"
- "{country} stock market today"
- "{country} economic news"
```

### ❌ AVOID (Paid/Limited)
- ~~Bloomberg API~~ (Paid only)
- ~~Reuters API~~ (Paid only)
- ~~Alpha Vantage~~ (Only 25 requests/day - too limited)
- ~~IEX Cloud~~ (Limited free tier)

---

## 2. 🔍 GOOGLE TRENDS

### ✅ FREE Data Sources

#### PyTrends (100% Free Library - No API Key!)
```python
pip install pytrends

from pytrends.request import TrendReq

# No API key needed!
pytrends = TrendReq(hl='en-US', tz=360)

# Get trending searches
trending = pytrends.trending_searches(pn='united_states')

# Get interest over time
pytrends.build_payload(['bitcoin'], timeframe='now 7-d')
interest = pytrends.interest_over_time()

# Get related queries
related = pytrends.related_queries()
```

#### Google Trends Website (Selenium Backup)
```
URL: https://trends.google.com/trends/trendingsearches/daily?geo=US
Scrape if pytrends fails:
- Trending searches
- Search volume
- Related news
```

### ❌ AVOID
- None! PyTrends is perfect and 100% free

---

## 3. 📰 NEWS

### ✅ FREE Data Sources

#### Google News (Selenium Scraping)
```
URL: https://news.google.com/topstories?hl=en-{country}&gl={country}

By category:
- World: /topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB
- Local: /topics/CAAqJQgKIh9DQkFTRVFvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB
- Business: /topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB
- Technology: /topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB
- Sports: /topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FtVnVHZ0pWVXlnQVAB

Scrape:
- Headlines
- Source
- Publication time
- Article URL
```

#### Direct News Site Scraping (Selenium)
```
USA:
- CNN: https://www.cnn.com/
- Fox News: https://www.foxnews.com/
- NBC News: https://www.nbcnews.com/

UK:
- BBC: https://www.bbc.com/news
- Guardian: https://www.theguardian.com/uk

India:
- Times of India: https://timesofindia.indiatimes.com/
- NDTV: https://www.ndtv.com/

Scrape homepage headlines
```

#### Google Search for News (Selenium)
```
Search: "{country} news today"
Scrape top 10 news results
```

### ❌ AVOID (Paid/Limited)
- ~~NewsAPI~~ (Only 100 requests/day for free, then $449/month)
- ~~News APIs from specific companies~~ (Usually paid)

---

## 4. 🏛️ POLITICS

### ✅ FREE Data Sources

#### Wikipedia (Selenium Scraping)
```
URLs:
- https://en.wikipedia.org/wiki/Politics_of_{country}
- https://en.wikipedia.org/wiki/List_of_current_heads_of_state_and_government
- https://en.wikipedia.org/wiki/Government_of_{country}

Scrape:
- Current leader
- Political party in power
- Political system
- Recent elections
```

#### Government Websites (Selenium Scraping)
```
USA: https://www.whitehouse.gov/
UK: https://www.gov.uk/
India: https://www.india.gov.in/
Canada: https://www.canada.ca/
Australia: https://www.australia.gov.au/

Scrape:
- Latest press releases
- New policies
- Official statements
```

#### Ballotpedia (Selenium)
```
URL: https://ballotpedia.org/
Free election information for USA
```

#### Google Search (Selenium)
```
Queries:
- "{country} president prime minister"
- "{country} government 2025"
- "{country} recent laws passed"
- "{country} upcoming election date"
- "{country} political news"
```

### ❌ AVOID
- ~~Political polling APIs~~ (Usually paid)
- ~~GovTrack API~~ (US only, limited)

---

## 5. ⚽ SPORTS

### ✅ FREE Data Sources

#### ESPN (Selenium Scraping - No API Key)
```
URL: https://www.espn.com/

By sport:
- NFL: https://www.espn.com/nfl/scoreboard
- NBA: https://www.espn.com/nba/scoreboard
- MLB: https://www.espn.com/mlb/scoreboard
- NHL: https://www.espn.com/nhl/scoreboard
- Soccer: https://www.espn.com/soccer/scoreboard

Scrape:
- Recent game scores
- Upcoming games
- Sports news headlines
```

#### BBC Sport (Selenium)
```
URL: https://www.bbc.com/sport

By sport:
- Football: https://www.bbc.com/sport/football
- Cricket: https://www.bbc.com/sport/cricket
- Rugby: https://www.bbc.com/sport/rugby-union
- Tennis: https://www.bbc.com/sport/tennis

Scrape:
- Scores
- Fixtures
- Sports news
```

#### FlashScore (Selenium)
```
URL: https://www.flashscore.com/
Free live scores for all sports worldwide
```

#### Google Search (Selenium)
```
Queries:
- "{sport} {country} scores today"
- "{sport} {country} games this week"
- "{sport} {country} news"
- "{team name} next game"
```

### ❌ AVOID (Paid/Limited)
- ~~ESPN API~~ (Officially deprecated)
- ~~TheSportsDB~~ (Requires Patreon subscription for full access)
- ~~SportsRadar~~ (Paid only)

---

## Implementation Strategy

### 1. Core Selenium Setup
```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Headless Chrome setup (runs in background)
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')

driver = webdriver.Chrome(options=options)
```

### 2. Google Search Scraping Template
```python
def scrape_google_search(query, num_results=10):
    """Scrape Google search results."""
    driver.get(f'https://www.google.com/search?q={query}')
    time.sleep(2)  # Let page load

    # Get search results
    results = driver.find_elements(By.CSS_SELECTOR, 'div.g')

    data = []
    for result in results[:num_results]:
        try:
            title = result.find_element(By.CSS_SELECTOR, 'h3').text
            link = result.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
            snippet = result.find_element(By.CSS_SELECTOR, 'div.VwiC3b').text

            data.append({
                'title': title,
                'url': link,
                'snippet': snippet
            })
        except:
            continue

    return data
```

### 3. Rate Limiting & Politeness
```python
import random
import time

def polite_request(url, driver):
    """Make a polite request with random delays."""
    # Random delay between requests (2-5 seconds)
    time.sleep(random.uniform(2, 5))

    driver.get(url)

    # Wait for page to load
    time.sleep(random.uniform(1, 3))
```

### 4. Error Handling
```python
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def safe_scrape(url, scraper_func):
    """Scrape with error handling."""
    try:
        return scraper_func(url)
    except TimeoutException:
        print(f"Timeout scraping {url}")
        return None
    except NoSuchElementException:
        print(f"Element not found on {url}")
        return None
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None
```

---

## Libraries Needed (All Free!)

```bash
pip install selenium beautifulsoup4 pytrends requests pandas python-dotenv

# For Chrome WebDriver
# macOS:
brew install chromedriver

# Or download from: https://chromedriver.chromium.org/
```

---

## Cost Summary

| Category | Method | Cost |
|----------|--------|------|
| **Economics** | Selenium + World Bank API | $0 |
| **Google Trends** | PyTrends | $0 |
| **News** | Selenium (Google News + news sites) | $0 |
| **Politics** | Selenium (Wikipedia + gov sites) | $0 |
| **Sports** | Selenium (ESPN + BBC Sport) | $0 |

**Total Cost: $0/month** 🎉

---

## Pro Tips

1. **Use headless browser** - Faster and uses less resources
2. **Random delays** - Avoid getting blocked (2-5 seconds between requests)
3. **Rotate user agents** - Look like different browsers
4. **Cache results** - Don't scrape same data multiple times
5. **Run at off-peak hours** - Less likely to get rate limited
6. **Respect robots.txt** - Be a good internet citizen
7. **Handle errors gracefully** - Sites change, code should handle it

---

## Next Steps

1. Start with **Google Trends** (easiest - just install pytrends!)
2. Then **Sports** (ESPN scraping is straightforward)
3. Then **Economics** (World Bank API + Google Finance)
4. Then **News** (Google News scraping)
5. Finally **Politics** (Wikipedia + government sites)

Everything is 100% free! 🚀
