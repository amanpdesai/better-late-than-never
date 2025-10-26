# Geographic Data Sourcing for "The Internet’s Mood Board"

This document summarizes how to obtain **country-level and regional trend data** for the dashboard.  
It includes realistic APIs, scraping methods, and integration strategies.

---

## 1. Objective

Collect trending and sentiment-rich data per **region** (US, UK, Asia, etc.) to visualize how different parts of the world are feeling and talking online.

---

## 2. Key Data Sources

### A. YouTube Trending (Primary Source)

**Why Use It:**  
YouTube provides region-specific trending feeds for almost every country.

**API Endpoint:**  
`https://www.googleapis.com/youtube/v3/videos`

**Parameters:**
- `chart=mostPopular`
- `regionCode=<ISO code>` (e.g., `US`, `GB`, `IN`)
- `part=snippet,statistics`
- `maxResults=50`
- `key=<YOUR_API_KEY>`

**Python Example:**
```python
import requests

API_KEY = "YOUR_API_KEY"
url = "https://www.googleapis.com/youtube/v3/videos"
params = {
    "part": "snippet,statistics",
    "chart": "mostPopular",
    "regionCode": "US",
    "maxResults": 50,
    "key": API_KEY
}
res = requests.get(url, params=params).json()
```

**Advantages:**
- Region built-in (no inference required)
- Provides thumbnails, titles, and engagement metrics
- Easy to extend globally with a loop over region codes

**Suggested Coverage:**  
`['US', 'GB', 'IN', 'JP', 'BR', 'CA', 'DE', 'FR', 'AU']`

---

### B. Reddit (Regional Subreddit Mapping)

**Why Use It:**  
Subreddits often represent specific countries, giving strong geographic context.

**Access Method:**  
Use the **PRAW** API or Reddit’s JSON endpoints.

**Python Example:**
```python
import praw

reddit = praw.Reddit(client_id='YOUR_ID', client_secret='YOUR_SECRET', user_agent='MoodBoard')
subreddit = reddit.subreddit("ukpolitics")
for post in subreddit.hot(limit=10):
    print(post.title)
```

**Country Mapping Example:**
```python
subreddit_to_country = {
    "r/ukpolitics": "GB",
    "r/india": "IN",
    "r/AskAnAmerican": "US",
    "r/australia": "AU"
}
```

**Advantages:**
- Natural geographic granularity
- Text-rich data for sentiment analysis
- Strong correlation with political/economic discussion

**Limitations:**
- Uneven coverage across countries
- Requires manual subreddit-to-country mapping

---

### C. Google Trends (Supplementary Enrichment)

**Why Use It:**  
Provides search interest by region, helping normalize attention volume across topics.

**Library:** [Pytrends](https://github.com/GeneralMills/pytrends)

**Python Example:**
```python
from pytrends.request import TrendReq

pytrend = TrendReq()
pytrend.build_payload(kw_list=["memes"])
data = pytrend.interest_by_region()
print(data.head())
```

**Advantages:**
- Free and easy to use
- Offers country-level search volume
- Complements social sentiment with attention trends

**Use Cases:**
- Normalize topic frequencies
- Cross-check which countries are driving category spikes

---

### D. Twitter / X (Optional)
**Status:** API access is paid, but public datasets exist.

**Example Mirror Dataset:**  
[GitHub – theaidenlab/twitter-trends](https://github.com/theaidenlab/twitter-trends)

**How to Use:**
- Download JSONs of top trends by country
- Parse and merge with your sentiment dataset

**Advantages:**
- High-frequency updates
- Excellent for real-time social spikes

**Limitations:**
- No free official API
- Must rely on third-party scrapes or archives

---

## 3. Combining and Normalizing Data

**Goal:** Create unified country-level trend summaries per category (Memes, Economics, Politics).

**Aggregation Pipeline:**
```
YouTube (region feeds)
+ Reddit (regional subs)
+ Google Trends (enrichment)
→ Sentiment/Emotion Classification
→ Aggregation by Region
→ Store in Database
→ Globe Visualization
```

**Normalization Techniques:**
- Weight averages by post count per country
- Use rolling 3–6 hour windows for smoothing
- Convert sentiment scores to range [-1, +1]

**SQL Example:**
```sql
SELECT country, category, AVG(sentiment_score) AS avg_sentiment
FROM posts
GROUP BY country, category;
```

---

## 4. Recommended Global Coverage

| Region | Primary Source | Backup Source | Confidence |
|--------|----------------|----------------|-------------|
| North America | YouTube + Reddit | Google Trends | High |
| Europe | YouTube + Reddit | Google Trends | High |
| Asia | YouTube | Google Trends | Medium |
| South America | YouTube | Google Trends | High |
| Africa | Google Trends | Reddit (limited) | Medium |

---

## 5. Implementation Notes

- **Storage:** Use Supabase or PostgreSQL with country + category as primary keys.  
- **Scheduling:** Use cron jobs or Celery workers to update every hour.  
- **Visualization:** Convert region codes (ISO 3166-1 alpha-2) to country polygons on a Three.js globe.  
- **Language Detection:** Use `langdetect` or `fasttext` to verify country inference when needed.  

---

## 6. Future Enhancements

- Add TikTok or Instagram scraping (through public trend trackers).  
- Use multilingual emotion models for non-English content.  
- Incorporate cross-category correlations (e.g., memes reacting to political news).  

---

**Summary:**  
This pipeline ensures you can **reliably tag and analyze content geographically** without relying on paid APIs. YouTube gives structured country data, Reddit provides textual depth, and Google Trends normalizes the signal across the globe.
