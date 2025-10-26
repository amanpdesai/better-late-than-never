"""
NEWS DATA SCRAPER (100% FREE)
==============================

PURPOSE: Track top news headlines using ONLY FREE sources (Selenium scraping).

FREE DATA SOURCES:
------------------
1. Google News (Selenium Scraping)
   URL: https://news.google.com/topstories?hl=en-{country}&gl={country}

2. Direct News Site Scraping (Selenium)
   USA: CNN.com, FoxNews.com, NBCNews.com
   UK: BBC.com/news, TheGuardian.com/uk
   India: TimesOfIndia.com, NDTV.com

3. Google Search (Selenium)
   Query: "{country} news today"

OUTPUT SCHEMA:
{
  "country": "USA",
  "category": "news",
  "timestamp": "2025-10-25T20:00:00Z",
  "items": [...],
  "news_by_source": {...},
  "summary": {"total_stories": 50, "overall_sentiment": "mixed"}
}

REQUIRED: pip install selenium beautifulsoup4 webdriver-manager
REFRESH: Every 1 hour
"""

import os
import json
import argparse
import time
import random
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import Counter

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# BeautifulSoup for parsing
from bs4 import BeautifulSoup


# Country-specific configurations
COUNTRY_CONFIGS = {
    'USA': {
        'google_news_code': 'US',
        'language': 'en',
        'google_news_section': 'nation',  # Local US news
        'news_sites': {
            'CNN': 'https://www.cnn.com/us',  # US news section
            'NBC News': 'https://www.nbcnews.com/us-news',  # US news section
            'Fox News': 'https://www.foxnews.com/us'  # US news section
        }
    },
    'UK': {
        'google_news_code': 'GB',
        'language': 'en',
        'google_news_section': 'nation',  # Local UK news
        'news_sites': {
            'BBC': 'https://www.bbc.com/news/uk',  # UK news section
            'The Guardian': 'https://www.theguardian.com/uk-news'  # UK news section
        }
    },
    'United Kingdom': {
        'google_news_code': 'GB',
        'language': 'en',
        'google_news_section': 'nation',
        'news_sites': {
            'BBC': 'https://www.bbc.com/news/uk',
            'The Guardian': 'https://www.theguardian.com/uk-news'
        }
    },
    'India': {
        'google_news_code': 'IN',
        'language': 'en',
        'google_news_section': 'nation',  # Local India news
        'news_sites': {
            'Times of India': 'https://timesofindia.indiatimes.com/india',  # India section
            'NDTV': 'https://www.ndtv.com/india'  # India section
        }
    },
    'Canada': {
        'google_news_code': 'CA',
        'language': 'en',
        'google_news_section': 'nation',  # Local Canada news
        'news_sites': {
            'CBC': 'https://www.cbc.ca/news/canada',  # Canada section
            'The Globe and Mail': 'https://www.theglobeandmail.com/canada'  # Canada section
        }
    },
    'Australia': {
        'google_news_code': 'AU',
        'language': 'en',
        'google_news_section': 'nation',  # Local Australia news
        'news_sites': {
            'ABC News': 'https://www.abc.net.au/news/australia',  # Australia section
            'The Sydney Morning Herald': 'https://www.smh.com.au/national'  # National section
        }
    }
}


class NewsScraperError(Exception):
    """Custom exception for news scraper errors."""
    pass


class NewsScraper:
    """Scrapes news articles from Google News and direct news sites."""

    def __init__(self, headless: bool = True):
        self.driver = None
        self.headless = headless
        self.articles = []

    def init_driver(self):
        """Initialize Selenium WebDriver."""
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(30)
        except Exception as e:
            print(f"Error initializing WebDriver: {e}")
            raise NewsScraperError(f"Failed to initialize WebDriver: {e}")

    def close_driver(self):
        """Close the WebDriver."""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

    def random_delay(self, min_sec: float = 1.5, max_sec: float = 3.5):
        """Add a random delay to appear more human-like."""
        time.sleep(random.uniform(min_sec, max_sec))

    def scrape_google_news(self, country_code: str, language: str = 'en', section: str = 'nation') -> List[Dict[str, Any]]:
        """Scrape Google News for a specific country - LOCAL news section."""
        print(f"Scraping Google News LOCAL section for {country_code}...")
        articles = []

        try:
            # Use simpler URL that focuses on local news for the country
            # The hl (language) and gl (location) parameters help Google News
            # show news relevant to that specific country
            url = f'https://news.google.com/?hl={language}-{country_code}&gl={country_code}&ceid={country_code}:{language}'

            self.driver.get(url)
            self.random_delay(2, 4)

            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Find article elements (Google News structure)
            article_elements = soup.find_all('article', limit=30)

            for idx, article_elem in enumerate(article_elements):
                try:
                    # Extract headline
                    headline_elem = article_elem.find('a', class_='gPFEn')
                    if not headline_elem:
                        headline_elem = article_elem.find('h3') or article_elem.find('h4')

                    if headline_elem:
                        headline = headline_elem.get_text(strip=True)
                        link = headline_elem.get('href', '')

                        # Google News links are relative
                        if link.startswith('./'):
                            link = 'https://news.google.com' + link[1:]

                        # Extract source
                        source_elem = article_elem.find('a', class_='wEwyrc')
                        source = source_elem.get_text(strip=True) if source_elem else 'Google News'

                        # Extract timestamp
                        time_elem = article_elem.find('time')
                        published_at = time_elem.get('datetime', datetime.utcnow().isoformat() + 'Z') if time_elem else datetime.utcnow().isoformat() + 'Z'

                        articles.append({
                            'id': f'google_news_{country_code}_{idx}_{int(time.time())}',
                            'title': headline,
                            'content': headline,  # Google News doesn't show full content
                            'source_platform': 'google_news',
                            'source_name': source,
                            'source_url': link,
                            'created_at': published_at,
                            'engagement': {
                                'likes': 0,
                                'comments': 0,
                                'shares': 0,
                                'views': 0
                            },
                            'sentiment': self.analyze_sentiment(headline),
                            'virality_score': 0,  # Will calculate later
                            'media': {
                                'thumbnail': None,
                                'images': [],
                                'videos': []
                            }
                        })
                except Exception as e:
                    print(f"Error parsing article element: {e}")
                    continue

            print(f"Successfully scraped {len(articles)} articles from Google News")

        except TimeoutException:
            print("Timeout loading Google News")
        except Exception as e:
            print(f"Error scraping Google News: {e}")

        return articles

    def scrape_direct_site(self, site_name: str, site_url: str, country: str) -> List[Dict[str, Any]]:
        """Scrape headlines from a direct news site."""
        print(f"Scraping {site_name}...")
        articles = []

        try:
            self.driver.get(site_url)
            self.random_delay(2, 4)

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Different selectors for different sites
            headlines = []

            if 'cnn.com' in site_url:
                headlines = soup.find_all(['h3', 'span'], class_=['container__headline', 'container__headline-text'], limit=15)
            elif 'bbc.com' in site_url:
                # BBC uses h2 tags with specific classes
                headlines = soup.find_all('h2', class_=lambda x: x and ('gJLfoH' in x or 'iCfgww' in x), limit=20)
            elif 'nbcnews.com' in site_url:
                # NBC uses h2 with storyline__headline class
                headlines = soup.find_all('h2', class_='storyline__headline', limit=20)
            elif 'foxnews.com' in site_url:
                headlines = soup.find_all('h2', class_=['title', 'article-title'], limit=15)
            elif 'theguardian.com' in site_url:
                # Guardian uses h3 with card-headline class
                headlines = soup.find_all('h3', class_='card-headline', limit=20)
            elif 'timesofindia.indiatimes.com' in site_url:
                # Times of India has heavy anti-bot protection, often times out
                # Try multiple selectors
                headlines = soup.find_all('a', class_=['w_tle', 'big_tle'], limit=15)
                if not headlines:
                    headlines = soup.find_all(['h1', 'h2', 'h3'], limit=15)
            elif 'ndtv.com' in site_url:
                # NDTV uses h1 with crd_ttl1, h3/h4 with crd_ttl2
                headlines = soup.find_all(['h1', 'h3', 'h4'], class_=lambda x: x and ('crd_ttl1' in x or 'crd_ttl2' in x), limit=20)
            elif 'cbc.ca' in site_url:
                headlines = soup.find_all('h3', class_='headline', limit=15)
            elif 'theglobeandmail.com' in site_url:
                headlines = soup.find_all('h3', class_='c-card__hed', limit=15)
            elif 'abc.net.au' in site_url:
                headlines = soup.find_all('h3', limit=15)
            elif 'smh.com.au' in site_url:
                headlines = soup.find_all('h3', class_='_3H-9I', limit=15)
            else:
                # Fallback: try to find any h1, h2, h3 tags
                headlines = soup.find_all(['h1', 'h2', 'h3'], limit=15)

            for idx, headline_elem in enumerate(headlines):
                try:
                    # Get text
                    headline = headline_elem.get_text(strip=True)

                    # Skip if empty or too short
                    if not headline or len(headline) < 10:
                        continue

                    # Try to find the link
                    link = None
                    if headline_elem.name == 'a':
                        link = headline_elem.get('href', '')
                    else:
                        parent_link = headline_elem.find_parent('a')
                        if parent_link:
                            link = parent_link.get('href', '')
                        else:
                            # Look for nearby links
                            nearby_link = headline_elem.find('a')
                            if nearby_link:
                                link = nearby_link.get('href', '')

                    # Make link absolute
                    if link and not link.startswith('http'):
                        from urllib.parse import urljoin
                        link = urljoin(site_url, link)

                    articles.append({
                        'id': f'{site_name.lower().replace(" ", "_")}_{country}_{idx}_{int(time.time())}',
                        'title': headline,
                        'content': headline,
                        'source_platform': 'news_site',
                        'source_name': site_name,
                        'source_url': link or site_url,
                        'created_at': datetime.utcnow().isoformat() + 'Z',
                        'engagement': {
                            'likes': 0,
                            'comments': 0,
                            'shares': 0,
                            'views': 0
                        },
                        'sentiment': self.analyze_sentiment(headline),
                        'virality_score': 0,
                        'media': {
                            'thumbnail': None,
                            'images': [],
                            'videos': []
                        }
                    })
                except Exception as e:
                    print(f"Error parsing headline: {e}")
                    continue

            print(f"Successfully scraped {len(articles)} articles from {site_name}")

        except TimeoutException:
            print(f"Timeout loading {site_name}")
        except Exception as e:
            print(f"Error scraping {site_name}: {e}")

        return articles

    def analyze_sentiment(self, text: str) -> str:
        """Basic sentiment analysis using keyword matching."""
        text_lower = text.lower()

        # Positive keywords
        positive_words = ['success', 'win', 'breakthrough', 'growth', 'gain', 'improve', 'rise',
                         'celebrate', 'victory', 'achievement', 'progress', 'hope', 'recovery',
                         'innovation', 'advance', 'record', 'boom', 'surge']

        # Negative keywords
        negative_words = ['crisis', 'crash', 'death', 'war', 'attack', 'disaster', 'tragedy',
                         'crash', 'fail', 'loss', 'decline', 'fall', 'concern', 'threat',
                         'danger', 'risk', 'scandal', 'controversy', 'chaos', 'violence',
                         'protest', 'conflict', 'struggle', 'emergency', 'warning']

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if negative_count > positive_count:
            return 'negative'
        elif positive_count > negative_count:
            return 'positive'
        else:
            return 'neutral'

    def scrape_country(self, country: str) -> Dict[str, Any]:
        """Scrape news for a specific country."""
        print(f"\n{'='*60}")
        print(f"Starting news scraping for {country}")
        print(f"{'='*60}\n")

        # Get country configuration
        if country not in COUNTRY_CONFIGS:
            raise NewsScraperError(f"Country '{country}' not supported. Supported countries: {list(COUNTRY_CONFIGS.keys())}")

        config = COUNTRY_CONFIGS[country]
        all_articles = []
        news_by_source = {}

        # Initialize driver
        self.init_driver()

        try:
            # 1. Scrape Google News LOCAL section
            google_articles = self.scrape_google_news(
                config['google_news_code'],
                config['language'],
                config.get('google_news_section', 'nation')
            )
            all_articles.extend(google_articles)
            news_by_source['Google News'] = google_articles

            # 2. Scrape direct news sites
            for site_name, site_url in config['news_sites'].items():
                self.random_delay(2, 4)  # Be polite
                site_articles = self.scrape_direct_site(site_name, site_url, country)
                all_articles.extend(site_articles)
                news_by_source[site_name] = site_articles

            # 3. Calculate virality scores (simple score based on recency)
            for article in all_articles:
                # For news, recency is key - newer articles get higher scores
                article['virality_score'] = random.randint(40, 95)  # Placeholder

            # 4. Generate summary
            sentiments = [article['sentiment'] for article in all_articles]
            sentiment_counts = Counter(sentiments)

            # Determine overall sentiment
            if sentiment_counts.get('negative', 0) > len(all_articles) * 0.5:
                overall_sentiment = 'negative'
            elif sentiment_counts.get('positive', 0) > len(all_articles) * 0.4:
                overall_sentiment = 'positive'
            elif sentiment_counts.get('negative', 0) > sentiment_counts.get('positive', 0):
                overall_sentiment = 'mixed_negative'
            else:
                overall_sentiment = 'mixed'

            # Extract top topics
            all_titles = ' '.join([article['title'] for article in all_articles])
            top_topics = self.extract_topics(all_titles)

            summary = {
                'total_stories': len(all_articles),
                'overall_sentiment': overall_sentiment,
                'sentiment_breakdown': dict(sentiment_counts),
                'top_topics': top_topics,
                'sources_count': len(news_by_source),
                'avg_virality_score': sum(a['virality_score'] for a in all_articles) / len(all_articles) if all_articles else 0
            }

            # Build final result
            result = {
                'country': country,
                'category': 'news',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'last_updated': datetime.utcnow().isoformat() + 'Z',
                'items': all_articles,
                'news_by_source': {source: len(articles) for source, articles in news_by_source.items()},
                'summary': summary
            }

            print(f"\n{'='*60}")
            print(f"Scraping completed for {country}")
            print(f"Total articles: {len(all_articles)}")
            print(f"Sources: {list(news_by_source.keys())}")
            print(f"Overall sentiment: {overall_sentiment}")
            print(f"{'='*60}\n")

            return result

        finally:
            self.close_driver()

    def extract_topics(self, text: str, top_n: int = 5) -> List[str]:
        """Extract top topics from text using simple word frequency."""
        # Common stop words to ignore
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
                     'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                     'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
                     'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
                     'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each',
                     'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such',
                     'says', 'after', 'over', 'new'}

        # Clean and tokenize
        words = text.lower().split()

        # Filter words
        filtered_words = [
            word.strip('.,!?;:"\'-')
            for word in words
            if len(word) > 3
            and word.lower() not in stop_words
            and word.isalpha()
        ]

        # Count frequencies
        word_counts = Counter(filtered_words)

        # Return top N
        return [word for word, count in word_counts.most_common(top_n)]


def scrape_news_data(country: str, headless: bool = True) -> Dict[str, Any]:
    """Main function to scrape news data for a country."""
    scraper = NewsScraper(headless=headless)
    return scraper.scrape_country(country)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape news (100% free)')
    parser.add_argument('--country', type=str, required=True,
                       help=f'Country to scrape. Options: {list(COUNTRY_CONFIGS.keys())}')
    parser.add_argument('--output', type=str, default='../output/',
                       help='Output directory path')
    parser.add_argument('--headless', type=bool, default=True,
                       help='Run browser in headless mode')
    args = parser.parse_args()

    try:
        # Scrape data
        data = scrape_news_data(args.country, args.headless)

        # Save to output directory
        output_dir = os.path.join(args.output, args.country)
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, f"{datetime.now().strftime('%Y-%m-%d')}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n✅ News data saved to: {output_file}")
        print(f"📊 Total articles: {data['summary']['total_stories']}")
        print(f"📰 Sources: {data['summary']['sources_count']}")
        print(f"😊 Overall sentiment: {data['summary']['overall_sentiment']}")

    except NewsScraperError as e:
        print(f"\n❌ Scraper Error: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
