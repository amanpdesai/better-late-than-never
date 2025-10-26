# Category Data Collection Planning

## Overview

This document details exactly what data to collect for each category and where to get it.

---

## 1. 💰 ECONOMICS

### What to Collect

#### Core Economic Indicators
- **GDP Growth Rate** - Current and trend
- **Inflation Rate (CPI)** - Month-over-month, year-over-year
- **Unemployment Rate** - Current percentage
- **Interest Rates** - Central bank rates
- **Currency Exchange Rate** - vs USD, trend (inflation/deflation)
- **Stock Market Index** - Main index (S&P 500, FTSE, Nifty, etc.)

#### Market Data
- **Top Performing Stocks** - Top 5 gainers today
- **Major IPOs** - Recent and upcoming
- **Crypto Trends** - If relevant to country

#### Sentiment & News
- **Economic News Headlines** - Top 5-10 economic stories
- **Sentiment Score** - Are people worried? (positive/negative/neutral)
- **Key Concerns** - What are people worried about? (housing, jobs, inflation)

### Data Sources

#### Free APIs (No Scraping Needed)
```python
# 1. Alpha Vantage (Free - 25 requests/day)
#    - Stock data, forex, economic indicators
#    URL: https://www.alphavantage.co/
#    Example: GDP, CPI, unemployment

# 2. Exchange Rate API (Free)
#    - Currency exchange rates
#    URL: https://exchangerate-api.com/

# 3. World Bank API (Free, no key needed)
#    - GDP, inflation, unemployment
#    URL: https://api.worldbank.org/v2/country/US/indicator/NY.GDP.MKTP.CD.ZS?format=json

# 4. FRED API (Free with key)
#    - Federal Reserve Economic Data
#    URL: https://fred.stlouisfed.org/docs/api/fred/

# 5. Yahoo Finance (via yfinance library)
#    - Stock indices, top stocks
#    pip install yfinance
```

#### Selenium Scraping Targets
```python
# 1. Trading Economics
#    URL: https://tradingeconomics.com/united-states/indicators
#    Get: GDP, inflation, unemployment, interest rates
#    Frequency: Daily

# 2. Investing.com
#    URL: https://www.investing.com/economic-calendar/
#    Get: Economic calendar, upcoming events
#    Frequency: Daily

# 3. MarketWatch
#    URL: https://www.marketwatch.com/economy-politics
#    Get: Economic news, sentiment
#    Frequency: Every 6 hours

# 4. Google Finance
#    URL: https://www.google.com/finance/
#    Get: Stock indices, top movers
#    Frequency: Hourly
```

#### Google Search Queries
```python
# Use Selenium to scrape Google search results
queries = [
    f"{country} GDP growth rate 2025",
    f"{country} inflation rate today",
    f"{country} unemployment rate",
    f"{country} stock market index",
    f"{country} economic news",
    f"{country} biggest IPO",
    f"{country} economic policy changes"
]
```

### Dashboard Display

```
┌─────────────────────────────────────────┐
│ 🇺🇸 USA - ECONOMICS                     │
├─────────────────────────────────────────┤
│ 📊 Key Indicators                       │
│   GDP Growth:      2.5% ↑               │
│   Inflation (CPI): 3.2% ↓               │
│   Unemployment:    3.8% →               │
│   Interest Rate:   5.25% →              │
│   USD Exchange:    Strong ↑             │
│                                         │
│ 📈 Market Summary                       │
│   S&P 500:  4,785 (+0.5%)              │
│   Top Gainers:                          │
│   • NVDA: +3.2%                        │
│   • TSLA: +2.8%                        │
│   • AAPL: +1.5%                        │
│                                         │
│ 📰 Top Economic News                    │
│   1. Fed holds rates steady...         │
│   2. Job market remains strong...      │
│   3. Housing costs continue to rise... │
│                                         │
│ 😟 Sentiment: Concerned (65/100)       │
│   Top Worries:                          │
│   • Cost of living                     │
│   • Housing affordability              │
│   • Job security                       │
└─────────────────────────────────────────┘
```

---

## 2. 🔍 GOOGLE TRENDS

### What to Collect

- **Top Trending Searches** - What are people searching right now? (Top 20)
- **Rising Searches** - Breakout searches with 5000%+ growth
- **Category Breakdown** - Sports, Entertainment, News, etc.
- **Related Queries** - What else are people searching?
- **Geographic Distribution** - Which regions are searching most?
- **Time Context** - When did the trend start? How long has it been trending?

### Data Sources

#### PyTrends Library (Free, No API Key)
```python
# Google Trends unofficial API
# pip install pytrends

from pytrends.request import TrendReq

# Example usage
pytrends = TrendReq(hl='en-US', tz=360)

# 1. Trending searches (real-time)
trending = pytrends.trending_searches(pn='united_states')

# 2. Interest over time
pytrends.build_payload(['bitcoin'], timeframe='now 7-d')
interest = pytrends.interest_over_time()

# 3. Related queries
related = pytrends.related_queries()

# 4. Rising searches
suggestions = pytrends.suggestions(keyword='climate')
```

#### Google Trends Website Scraping (Selenium)
```python
# For real-time trending searches
# URL: https://trends.google.com/trends/trendingsearches/daily?geo={country_code}

# Example for USA
URL = "https://trends.google.com/trends/trendingsearches/daily?geo=US"

# Scrape:
# - Trending topics
# - Search volume (traffic)
# - Related news articles
# - Time trending
```

### Dashboard Display

```
┌─────────────────────────────────────────┐
│ 🇺🇸 USA - TRENDING SEARCHES             │
├─────────────────────────────────────────┤
│ 🔥 Top Trending (Right Now)            │
│   1. "World Series Game 5" 🔥          │
│      Traffic: 500K+ searches            │
│      Trend: ↑ Rising (2 hours)         │
│                                         │
│   2. "New iPhone release"              │
│      Traffic: 200K+ searches            │
│      Trend: ↑ Rising (5 hours)         │
│                                         │
│   3. "Election debate"                 │
│      Traffic: 150K+ searches            │
│      Trend: → Steady                   │
│                                         │
│ 📈 Breakout Searches                   │
│   • "AI breakthrough": +5000% ⚡       │
│   • "New tax policy": +2500%           │
│                                         │
│ 📊 Category Breakdown                  │
│   Sports:        30%                    │
│   Entertainment: 25%                    │
│   News:          20%                    │
│   Technology:    15%                    │
│   Other:         10%                    │
└─────────────────────────────────────────┘
```

---

## 3. 📰 NEWS

### What to Collect

#### Top Headlines
- **Top 5-10 Headlines** from each major news source in the country
- **Publication Time** - When was it published?
- **Category** - Politics, Business, Tech, Health, etc.
- **Sentiment** - Positive, Negative, Neutral
- **Engagement** - Shares, comments if available

#### News Sources by Country
```python
NEWS_SOURCES = {
    'USA': [
        'CNN', 'Fox News', 'New York Times',
        'Washington Post', 'Wall Street Journal'
    ],
    'UK': [
        'BBC', 'The Guardian', 'Daily Mail',
        'The Telegraph', 'The Times'
    ],
    'India': [
        'Times of India', 'Hindustan Times', 'NDTV',
        'The Hindu', 'Indian Express'
    ],
    'Canada': [
        'CBC', 'Global News', 'CTV News',
        'Toronto Star', 'National Post'
    ],
    'Australia': [
        'ABC News', 'News.com.au', 'The Age',
        'Sydney Morning Herald', 'The Australian'
    ]
    # Add more countries...
}
```

### Data Sources

#### NewsAPI (Free - 100 requests/day, paid for more)
```python
# pip install newsapi-python
from newsapi import NewsApiClient

newsapi = NewsApiClient(api_key='your_api_key')

# Get top headlines by country
headlines = newsapi.get_top_headlines(
    country='us',
    page_size=10
)

# Get headlines from specific sources
cnn_headlines = newsapi.get_top_headlines(
    sources='cnn',
    page_size=10
)
```

#### Google News Scraping (Selenium)
```python
# URL: https://news.google.com/topstories?hl=en-US&gl=US&ceid=US:en

# Scrape top stories for each country
# Can filter by category:
# - World
# - Local
# - Business
# - Technology
# - Entertainment
# - Sports
# - Science
# - Health
```

#### Direct News Site Scraping (BeautifulSoup + Selenium)
```python
# Example for CNN
URL = "https://www.cnn.com/"

# Scrape:
# - Top headlines (h1, h2 tags)
# - Article links
# - Publication time
# - Category tags

# Repeat for each major news source
```

### Dashboard Display

```
┌─────────────────────────────────────────┐
│ 🇺🇸 USA - TOP NEWS                      │
├─────────────────────────────────────────┤
│ 📰 CNN                                  │
│   1. "President announces new policy"  │
│      2 hours ago • Politics • 😐       │
│   2. "Stock market hits record high"   │
│      4 hours ago • Business • 😊       │
│                                         │
│ 📰 New York Times                       │
│   1. "Climate summit reaches deal"     │
│      1 hour ago • World • 😊           │
│   2. "Tech layoffs continue"           │
│      3 hours ago • Technology • 😟     │
│                                         │
│ 📰 Washington Post                      │
│   1. "Healthcare reform proposed"      │
│      5 hours ago • Politics • 😐       │
│                                         │
│ 📊 Overall Sentiment: Mixed            │
│   Positive: 40%                         │
│   Neutral:  35%                         │
│   Negative: 25%                         │
│                                         │
│ 🔥 Trending Topics                     │
│   • Climate policy                     │
│   • Economic growth                    │
│   • Technology regulation              │
└─────────────────────────────────────────┘
```

---

## 4. 🏛️ POLITICS

### What to Collect

#### Leadership & Government
- **Current Leader** - President, Prime Minister, etc.
- **Party in Power** - Political party/coalition
- **Approval Rating** - Current approval %
- **Term End Date** - When is the next election?

#### Recent & Upcoming
- **Recent Policies Passed** - Last 30 days (Top 5)
- **Upcoming Policies** - Bills being debated
- **Upcoming Elections** - Date, type, key candidates

#### Political Climate
- **Key Issues** - What's being debated? (Top 5)
- **Public Sentiment** - Support/opposition levels
- **Controversies** - Major scandals or issues

### Data Sources

#### Wikipedia Scraping
```python
# Great for current leaders and basic info
# URL: https://en.wikipedia.org/wiki/Politics_of_{country}
# URL: https://en.wikipedia.org/wiki/List_of_current_heads_of_state_and_government

# Scrape:
# - Current head of state/government
# - Party in power
# - Political system
# - Recent elections
```

#### Government Websites (Official Data)
```python
GOVERNMENT_SITES = {
    'USA': 'https://www.whitehouse.gov/',
    'UK': 'https://www.gov.uk/',
    'India': 'https://www.india.gov.in/',
    'Canada': 'https://www.canada.ca/',
    'Australia': 'https://www.australia.gov.au/'
}

# Scrape for:
# - Latest press releases
# - New policies/legislation
# - Official statements
```

#### Political News Sites (Selenium)
```python
# Politico, The Hill, BBC Politics, etc.
URLS = {
    'USA': 'https://www.politico.com/',
    'UK': 'https://www.bbc.com/news/politics',
    'India': 'https://www.ndtv.com/india'
}

# Scrape for:
# - Recent policy changes
# - Upcoming votes
# - Political controversies
```

#### Election Data
```python
# URL: https://www.electionguide.org/
# Comprehensive election calendar

# Scrape:
# - Upcoming election dates
# - Type of election
# - Key candidates (if available)
```

#### Google Search Queries
```python
queries = [
    f"{country} president prime minister",
    f"{country} current government",
    f"{country} recent laws passed",
    f"{country} upcoming election",
    f"{country} political news",
    f"{country} government approval rating"
]
```

### Dashboard Display

```
┌─────────────────────────────────────────┐
│ 🇺🇸 USA - POLITICS                      │
├─────────────────────────────────────────┤
│ 👤 Leadership                           │
│   President: Joe Biden (Democrat)      │
│   Approval: 42% ↓                      │
│   Term Ends: January 2025              │
│                                         │
│   Congress:                             │
│   • House: Republican majority         │
│   • Senate: Democrat majority          │
│                                         │
│ 📜 Recent Policies (Last 30 Days)      │
│   1. Infrastructure bill signed        │
│      Status: ✅ Passed                 │
│   2. Climate legislation debated       │
│      Status: ⏳ Pending                │
│                                         │
│ 🗳️ Upcoming Elections                   │
│   Presidential Election                │
│   Date: November 5, 2025               │
│   Days Away: 12                        │
│                                         │
│ 🔥 Key Political Issues                │
│   1. Immigration reform                │
│   2. Healthcare costs                  │
│   3. Climate policy                    │
│   4. Tax reform                        │
│   5. Foreign policy                    │
│                                         │
│ 📊 Political Climate: Divided          │
│   Polarization Score: 78/100           │
└─────────────────────────────────────────┘
```

---

## 5. ⚽ SPORTS

### What to Collect

#### Recent Games
- **Top Sports by Country** - Football, Basketball, Cricket, Soccer, etc.
- **Recent Game Results** - Last 3-5 major games per sport
- **Scores** - Final scores, key stats
- **Highlights** - Major plays, records broken

#### Upcoming Games
- **Next 5 Major Games** per sport
- **Date & Time** - When is the game?
- **Teams/Players** - Who's playing?
- **Importance** - Playoff game? Championship? Regular season?

#### Major Events
- **Recent Trades** - Player transfers, trades
- **Injuries** - Key players injured
- **Controversies** - Scandals, controversies
- **Records** - Records broken recently
- **Awards** - MVP, Player of the Week, etc.

### Top Sports by Country
```python
TOP_SPORTS = {
    'USA': ['Football (NFL)', 'Basketball (NBA)', 'Baseball (MLB)', 'Hockey (NHL)'],
    'UK': ['Soccer (Premier League)', 'Cricket', 'Rugby', 'Tennis'],
    'India': ['Cricket', 'Kabaddi', 'Hockey', 'Badminton'],
    'Canada': ['Hockey (NHL)', 'Basketball (NBA)', 'Football (CFL)', 'Soccer'],
    'Australia': ['Cricket', 'Rugby (NRL)', 'AFL', 'Tennis'],
    'Brazil': ['Soccer', 'Volleyball', 'MMA', 'Formula 1'],
    'Japan': ['Baseball (NPB)', 'Soccer (J-League)', 'Sumo', 'Tennis']
}
```

### Data Sources

#### ESPN API (Free, but limited)
```python
# ESPN has hidden APIs you can use
# URL: http://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard

# Example for NBA:
# http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard

# Available sports:
# - football/nfl
# - basketball/nba
# - baseball/mlb
# - hockey/nhl
# - soccer/eng.1 (Premier League)
# - cricket/international
```

#### TheSportsDB (Free API)
```python
# URL: https://www.thesportsdb.com/api.php

# Example:
# https://www.thesportsdb.com/api/v1/json/3/eventsnext.php?id={team_id}

# Get:
# - Recent events
# - Upcoming events
# - Team info
# - Player info
```

#### Web Scraping (Selenium + BeautifulSoup)
```python
SPORTS_SITES = {
    'ESPN': 'https://www.espn.com/',
    'BBC Sport': 'https://www.bbc.com/sport',
    'Sky Sports': 'https://www.skysports.com/',
    'Sports Illustrated': 'https://www.si.com/'
}

# Scrape for:
# - Latest scores
# - Upcoming games
# - Sports news/highlights
# - Player stats
```

#### Google Search Queries
```python
# For each top sport in country
queries = [
    f"{sport} {country} recent games",
    f"{sport} {country} upcoming games",
    f"{sport} {country} scores today",
    f"{sport} {country} latest news",
    f"{sport} {country} trades"
]
```

### Dashboard Display

```
┌─────────────────────────────────────────┐
│ 🇺🇸 USA - SPORTS                        │
├─────────────────────────────────────────┤
│ 🏈 NFL (Football)                       │
│   Recent Game:                          │
│   Chiefs 28 - 24 49ers  ✅             │
│   Oct 24, 2025                          │
│                                         │
│   Upcoming:                             │
│   Cowboys vs Eagles                     │
│   Oct 26, 8:20 PM ET                   │
│                                         │
│ 🏀 NBA (Basketball)                     │
│   Recent Game:                          │
│   Lakers 105 - 98 Celtics ✅           │
│   Oct 24, 2025                          │
│                                         │
│   Upcoming:                             │
│   Warriors vs Bucks                     │
│   Oct 25, 7:30 PM ET                   │
│                                         │
│ 🔥 Major Events                        │
│   • LeBron James reaches 40K points    │
│   • Trade: Player X to Team Y          │
│   • Injury: Star QB out 4 weeks        │
│                                         │
│ 📊 Trending                            │
│   1. World Series Game 5               │
│   2. NBA Season Opener                 │
│   3. NFL Trade Deadline                │
└─────────────────────────────────────────┘
```

---

## Summary Table

| Category | Primary Sources | Scraping Method | Update Frequency |
|----------|----------------|-----------------|------------------|
| **Economics** | Alpha Vantage, World Bank API, Trading Economics | API + Selenium | 6 hours |
| **Google Trends** | PyTrends, Google Trends Website | PyTrends + Selenium | 30 min |
| **News** | NewsAPI, Google News, Direct news sites | API + Selenium + BeautifulSoup | 1 hour |
| **Politics** | Wikipedia, Government sites, Political news | Selenium + BeautifulSoup | 6 hours |
| **Sports** | ESPN API, TheSportsDB, Sports sites | API + Selenium | 2 hours |

---

## Next Steps

1. **Remove** memes and youtube folders (already done)
2. **Implement** economics scraper using Alpha Vantage + Trading Economics
3. **Implement** google-trends using PyTrends
4. **Implement** news scraper using NewsAPI + Google News
5. **Implement** politics scraper using Wikipedia + government sites
6. **Implement** sports scraper using ESPN API + web scraping
