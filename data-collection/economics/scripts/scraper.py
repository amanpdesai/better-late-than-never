"""
ECONOMICS DATA SCRAPER (100% FREE)
===================================

Scrapes economic data from free sources:
- World Bank API (GDP, inflation, unemployment)
- Google Finance (stock indices, top gainers)
- Google Search (economic news)

USAGE:
    python scraper.py --country USA
    python scraper.py --country UK --output ../output/
"""

import os
import json
import argparse
import requests
import time
import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("⚠️  yfinance not installed. Top gainers will be limited. Install with: pip install yfinance")

# Country code mappings
COUNTRY_CODES = {
    'USA': 'US',
    'UK': 'GB',
    'United Kingdom': 'GB',
    'India': 'IN',
    'Canada': 'CA',
    'Australia': 'AU',
    'Germany': 'DE',
    'France': 'FR',
    'Japan': 'JP',
    'Brazil': 'BR',
    'Mexico': 'MX',
    'Spain': 'ES',
    'Italy': 'IT'
}

# Stock index mappings
STOCK_INDICES = {
    'USA': '.INX',      # S&P 500
    'UK': 'FTSE',       # FTSE 100
    'India': 'NSEI',    # NIFTY 50
    'Canada': 'GSPTSE', # S&P/TSX
    'Australia': 'AXJO', # ASX 200
    'Germany': 'GDAXI', # DAX
    'France': 'FCHI',   # CAC 40
    'Japan': 'N225',    # Nikkei 225
    'Brazil': 'BVSP',   # Bovespa
    'Mexico': 'MXX'     # IPC Mexico
}

# Popular tickers by country for finding gainers
POPULAR_TICKERS = {
    'USA': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'JPM', 'V', 'WMT',
            'JNJ', 'PG', 'MA', 'HD', 'DIS', 'NFLX', 'ADBE', 'CRM', 'PFE', 'KO',
            'PEP', 'CSCO', 'INTC', 'AMD', 'QCOM', 'TXN', 'ORCL', 'IBM', 'BA', 'GE'],
    'UK': ['HSBA.L', 'AZN.L', 'SHEL.L', 'BP.L', 'ULVR.L', 'DGE.L', 'GSK.L', 'RIO.L',
           'BATS.L', 'REL.L', 'NG.L', 'LSEG.L', 'VOD.L', 'BARC.L', 'LLOY.L'],
    'India': ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS',
              'HINDUNILVR.NS', 'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'KOTAKBANK.NS'],
    'Canada': ['SHOP.TO', 'TD.TO', 'RY.TO', 'BNS.TO', 'CNQ.TO', 'ENB.TO', 'CP.TO'],
    'Australia': ['BHP.AX', 'CBA.AX', 'CSL.AX', 'NAB.AX', 'WBC.AX', 'ANZ.AX'],
    'Germany': ['SAP.DE', 'SIE.DE', 'ALV.DE', 'VOW3.DE', 'DTE.DE', 'MBG.DE'],
    'France': ['MC.PA', 'OR.PA', 'SAN.PA', 'TTE.PA', 'BNP.PA', 'AIR.PA'],
    'Japan': ['7203.T', '6758.T', '9984.T', '6861.T', '8306.T', '6954.T'],
    'Brazil': ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'B3SA3.SA'],
    'Mexico': ['WALMEX.MX', 'AMXL.MX', 'GFNORTEO.MX', 'CEMEXCPO.MX']
}

def setup_driver() -> webdriver.Chrome:
    """Set up headless Chrome driver."""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

    driver = webdriver.Chrome(options=options)
    return driver


def get_world_bank_data(country_code: str) -> Dict[str, Any]:
    """
    Fetch economic indicators from World Bank API (100% free, no authentication).

    Args:
        country_code: ISO country code (US, GB, IN, etc.)

    Returns:
        Dictionary with GDP, inflation, unemployment data
    """
    print(f"Fetching World Bank data for {country_code}...")

    indicators = {
        'gdp_growth': 'NY.GDP.MKTP.KD.ZG',        # GDP growth (annual %)
        'inflation': 'FP.CPI.TOTL.ZG',             # Inflation, consumer prices (annual %)
        'unemployment': 'SL.UEM.TOTL.ZS'           # Unemployment, total (% of labor force)
    }

    data = {}

    for name, indicator_code in indicators.items():
        url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}?format=json&per_page=5"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            result = response.json()

            if len(result) > 1 and result[1]:
                latest = result[1][0]
                value = latest.get('value')
                year = latest.get('date')

                # Try to get previous year for trend
                trend = 'stable'
                if len(result[1]) > 1:
                    prev_value = result[1][1].get('value')
                    if value and prev_value:
                        if value > prev_value:
                            trend = 'up'
                        elif value < prev_value:
                            trend = 'down'

                data[name] = {
                    'value': round(value, 2) if value else None,
                    'year': year,
                    'trend': trend,
                    'unit': '%'
                }

                print(f"  ✓ {name}: {value}% ({year})")
            else:
                print(f"  ✗ {name}: No data available")
                data[name] = {'value': None, 'year': None, 'trend': 'unknown', 'unit': '%'}

        except Exception as e:
            print(f"  ✗ Error fetching {name}: {e}")
            data[name] = {'value': None, 'year': None, 'trend': 'unknown', 'unit': '%'}

    return data


def get_top_gainers_yfinance(country: str) -> List[Dict[str, Any]]:
    """
    Get top gainers using yfinance library (more reliable than web scraping).
    Fetches weekly data to find stocks with best weekly performance.

    Args:
        country: Country name

    Returns:
        List of top gaining stocks over the past week
    """
    if not YFINANCE_AVAILABLE:
        print("  ⚠ yfinance not available, skipping top gainers")
        return []

    print(f"Fetching top gainers for {country} using yfinance (weekly data)...")

    tickers = POPULAR_TICKERS.get(country, [])
    if not tickers:
        print(f"  ⚠ No ticker list available for {country}")
        return []

    gainers = []

    try:
        # Fetch data for all tickers at once - last week (5 trading days)
        ticker_str = ' '.join(tickers)
        data = yf.download(ticker_str, period='5d', progress=False, group_by='ticker', threads=True)

        # Process each ticker
        for ticker in tickers:
            try:
                # Handle single ticker vs multiple tickers differently
                if len(tickers) == 1:
                    ticker_data = data
                else:
                    ticker_data = data[ticker]

                # Skip if no data or not enough data points
                if ticker_data.empty or len(ticker_data) < 2:
                    continue

                # Get first and last available trading day
                first_close = ticker_data['Close'].iloc[0]
                last_close = ticker_data['Close'].iloc[-1]

                if first_close and last_close and first_close > 0:
                    # Calculate percentage change over the week
                    change_pct = ((last_close - first_close) / first_close) * 100

                    # Only include gainers (positive change)
                    if change_pct > 0:
                        # Get ticker info for company name
                        try:
                            ticker_obj = yf.Ticker(ticker)
                            info = ticker_obj.info
                            name = info.get('longName', info.get('shortName', ticker))
                        except:
                            name = ticker

                        gainers.append({
                            'symbol': ticker,
                            'name': name,
                            'price': f"{last_close:.2f}",
                            'change_pct': round(change_pct, 2)
                        })
            except Exception as e:
                # Skip tickers with errors
                continue

        # Sort by change percentage and get top 5
        gainers = sorted(gainers, key=lambda x: x['change_pct'], reverse=True)[:5]

        if gainers:
            print(f"  ✓ Found {len(gainers)} top weekly gainers")
            for gainer in gainers:
                print(f"    • {gainer['symbol']}: +{gainer['change_pct']}% (week)")
        else:
            print(f"  ⚠ No gainers found for {country}")

        return gainers

    except Exception as e:
        print(f"  ✗ Error fetching top gainers: {e}")
        return []


def scrape_google_finance(country: str, driver: webdriver.Chrome) -> Dict[str, Any]:
    """
    Scrape Google Finance for stock market data.

    Args:
        country: Country name
        driver: Selenium WebDriver instance

    Returns:
        Dictionary with stock index and top gainers
    """
    print(f"Scraping Google Finance for {country}...")

    market_data = {
        'stock_index': {},
        'top_gainers': []
    }

    try:
        # Get main stock index for the country
        index_symbol = STOCK_INDICES.get(country)

        if index_symbol:
            # Search for the index on Google Finance
            url = f"https://www.google.com/finance/quote/{index_symbol}"
            driver.get(url)
            time.sleep(3)

            try:
                # Try multiple selector strategies (Google changes their HTML)
                name = None
                value = None
                change_text = None

                # Get the page source and parse with BeautifulSoup as backup
                soup = BeautifulSoup(driver.page_source, 'html.parser')

                # Strategy 1: Try original selectors
                try:
                    name_element = driver.find_element(By.CSS_SELECTOR, 'div.zzDege')
                    name = name_element.text
                except:
                    # Strategy 2: Use known index name for country
                    index_names = {
                        '.INX': 'S&P 500',
                        'FTSE': 'FTSE 100',
                        'NSEI': 'NIFTY 50',
                        'GSPTSE': 'S&P/TSX Composite',
                        'AXJO': 'ASX 200',
                        'GDAXI': 'DAX',
                        'FCHI': 'CAC 40',
                        'N225': 'Nikkei 225',
                        'BVSP': 'Bovespa',
                        'MXX': 'IPC Mexico'
                    }
                    name = index_names.get(index_symbol, f"{country} Main Index")

                # Get value - try multiple approaches
                try:
                    value_element = driver.find_element(By.CSS_SELECTOR, 'div.YMlKec.fxKbKc')
                    value = value_element.text.replace(',', '')
                except:
                    # Try finding the largest number on the page
                    try:
                        # Look for price in page source
                        price_divs = soup.find_all('div', class_=re.compile('YMlKec'))
                        if price_divs:
                            value = price_divs[0].get_text().replace(',', '')
                    except:
                        pass

                # Get change percentage
                try:
                    change_element = driver.find_element(By.CSS_SELECTOR, 'div.JwB6zf')
                    change_text = change_element.text
                except:
                    # Try BeautifulSoup
                    try:
                        change_divs = soup.find_all('div', class_=re.compile('JwB6zf'))
                        if change_divs:
                            change_text = change_divs[0].get_text()
                    except:
                        pass

                # Parse change percentage
                change_pct = 0.0
                trend = 'stable'

                if change_text and '%' in change_text:
                    match = re.search(r'([-+]?\d+\.?\d*)%', change_text)
                    if match:
                        change_pct = float(match.group(1))
                        trend = 'up' if change_pct > 0 else 'down' if change_pct < 0 else 'stable'

                if name or value:
                    market_data['stock_index'] = {
                        'name': name or f"{country} Main Index",
                        'value': float(value) if value and value.replace('.', '').replace('-', '').isdigit() else None,
                        'change_pct': change_pct,
                        'trend': trend
                    }

                    print(f"  ✓ Stock index: {name or 'Index'} = {value or 'N/A'} ({change_pct:+.2f}%)")
                else:
                    print(f"  ⚠ Could not extract all stock index data")

            except Exception as e:
                print(f"  ✗ Error parsing stock index: {e}")

        # Scrape top gainers from Google Finance homepage
        try:
            driver.get("https://www.google.com/finance/")
            time.sleep(2)

            # Look for "You may be interested in" or top movers section
            gainers = driver.find_elements(By.CSS_SELECTOR, 'div.SxL2pb')[:5]

            for gainer in gainers:
                try:
                    symbol = gainer.find_element(By.CSS_SELECTOR, 'div.COaKTb').text
                    name = gainer.find_element(By.CSS_SELECTOR, 'div.ZvmM7').text
                    price = gainer.find_element(By.CSS_SELECTOR, 'div.YMlKec').text
                    change = gainer.find_element(By.CSS_SELECTOR, 'div.JwB6zf').text

                    # Parse change percentage
                    change_pct = 0.0
                    if '%' in change:
                        match = re.search(r'([-+]?\d+\.?\d*)%', change)
                        if match:
                            change_pct = float(match.group(1))

                    if change_pct > 0:  # Only add gainers
                        market_data['top_gainers'].append({
                            'symbol': symbol,
                            'name': name,
                            'price': price,
                            'change_pct': change_pct
                        })
                except:
                    continue

            if market_data['top_gainers']:
                print(f"  ✓ Found {len(market_data['top_gainers'])} top gainers")

        except Exception as e:
            print(f"  ✗ Error scraping top gainers: {e}")

    except Exception as e:
        print(f"  ✗ Error scraping Google Finance: {e}")

    return market_data


def scrape_economic_news(country: str, driver: webdriver.Chrome) -> List[Dict[str, Any]]:
    """
    Scrape economic news from Google Search.

    Args:
        country: Country name
        driver: Selenium WebDriver instance

    Returns:
        List of news headlines
    """
    print(f"Scraping economic news for {country}...")

    news_headlines = []

    try:
        # Search for economic news
        query = f"{country} economy news"
        url = f"https://www.google.com/search?q={query}&tbm=nws"
        driver.get(url)
        time.sleep(3)

        # Parse with BeautifulSoup for more reliable extraction
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Try multiple selector strategies
        # Strategy 1: Standard news results
        articles = driver.find_elements(By.CSS_SELECTOR, 'div.SoaBEf')

        # Strategy 2: If no results, try different selector
        if not articles:
            articles = driver.find_elements(By.CSS_SELECTOR, 'div.Gx5Zad')

        # Strategy 3: Try generic news card selector
        if not articles:
            articles = driver.find_elements(By.CSS_SELECTOR, 'div[data-hveid]')

        for article in articles[:10]:
            try:
                headline = None
                source = None
                article_url = None

                # Try to get headline
                try:
                    headline_elem = article.find_element(By.CSS_SELECTOR, 'div.n0jPhd')
                    headline = headline_elem.text
                except:
                    try:
                        headline_elem = article.find_element(By.CSS_SELECTOR, 'div.mCBkyc')
                        headline = headline_elem.text
                    except:
                        try:
                            # Try finding any heading
                            headline_elem = article.find_element(By.TAG_NAME, 'h3')
                            headline = headline_elem.text
                        except:
                            continue

                # Try to get source - extract from URL if CSS fails
                try:
                    source_elem = article.find_element(By.CSS_SELECTOR, 'div.MgUUmf')
                    source = source_elem.text.split('·')[0].strip() if '·' in source_elem.text else source_elem.text
                except:
                    try:
                        source_elem = article.find_element(By.CSS_SELECTOR, 'span.NUnG9d')
                        source = source_elem.text
                    except:
                        # Extract from URL as fallback
                        try:
                            link_elem = article.find_element(By.CSS_SELECTOR, 'a')
                            url_temp = link_elem.get_attribute('href')
                            if 'yahoo.com' in url_temp:
                                source = "Yahoo Finance"
                            elif 'cnn.com' in url_temp:
                                source = "CNN"
                            elif 'bbc.com' in url_temp:
                                source = "BBC"
                            elif 'reuters.com' in url_temp:
                                source = "Reuters"
                            elif 'bloomberg.com' in url_temp:
                                source = "Bloomberg"
                            elif 'ft.com' in url_temp:
                                source = "Financial Times"
                            elif 'wsj.com' in url_temp:
                                source = "Wall Street Journal"
                            elif 'cnbc.com' in url_temp:
                                source = "CNBC"
                            elif 'pbs.org' in url_temp:
                                source = "PBS"
                            elif 'pewresearch.org' in url_temp:
                                source = "Pew Research"
                            elif 'investing.com' in url_temp:
                                source = "Investing.com"
                            elif 'aljazeera.com' in url_temp:
                                source = "Al Jazeera"
                            elif 'cbsnews.com' in url_temp:
                                source = "CBS News"
                            else:
                                source = "News Source"
                        except:
                            source = "News Source"

                # Try to get URL
                try:
                    link_elem = article.find_element(By.CSS_SELECTOR, 'a')
                    article_url = link_elem.get_attribute('href')
                except:
                    article_url = ""

                if headline:
                    # Simple sentiment analysis based on keywords
                    sentiment = analyze_sentiment(headline)

                    news_headlines.append({
                        'headline': headline,
                        'source': source,
                        'url': article_url,
                        'sentiment': sentiment,
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })

            except Exception as e:
                continue

        print(f"  ✓ Found {len(news_headlines)} news articles")

    except Exception as e:
        print(f"  ✗ Error scraping news: {e}")

    return news_headlines


def analyze_sentiment(text: str) -> str:
    """
    Simple sentiment analysis based on keywords.

    Args:
        text: Text to analyze

    Returns:
        Sentiment: 'positive', 'negative', or 'neutral'
    """
    text_lower = text.lower()

    positive_keywords = ['growth', 'surge', 'rise', 'gain', 'up', 'boost', 'strong', 'recover', 'improve', 'increase']
    negative_keywords = ['fall', 'drop', 'decline', 'loss', 'down', 'weak', 'recession', 'crisis', 'concern', 'worry', 'decrease']

    positive_count = sum(1 for word in positive_keywords if word in text_lower)
    negative_count = sum(1 for word in negative_keywords if word in text_lower)

    if positive_count > negative_count:
        return 'positive'
    elif negative_count > positive_count:
        return 'negative'
    else:
        return 'neutral'


def calculate_overall_sentiment(news_headlines: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate overall sentiment from news headlines."""
    if not news_headlines:
        return {'overall': 'neutral', 'score': 50, 'breakdown': {'positive': 0, 'neutral': 0, 'negative': 0}}

    sentiments = [article['sentiment'] for article in news_headlines]

    positive = sentiments.count('positive')
    neutral = sentiments.count('neutral')
    negative = sentiments.count('negative')
    total = len(sentiments)

    # Calculate score (0-100, where 50 is neutral)
    score = int(((positive - negative) / total) * 50 + 50)

    # Determine overall sentiment
    if score > 60:
        overall = 'optimistic'
    elif score < 40:
        overall = 'concerned'
    else:
        overall = 'neutral'

    return {
        'overall': overall,
        'score': score,
        'breakdown': {
            'positive': positive,
            'neutral': neutral,
            'negative': negative
        }
    }


def scrape_economics_data(country: str) -> Dict[str, Any]:
    """
    Main function to scrape all economics data for a country.

    Args:
        country: Country name (e.g., 'USA', 'UK', 'India')

    Returns:
        Dictionary with all economics data
    """
    print(f"\n{'='*60}")
    print(f"SCRAPING ECONOMICS DATA FOR {country.upper()}")
    print(f"{'='*60}\n")

    # Get country code
    country_code = COUNTRY_CODES.get(country, 'US')

    # Initialize driver
    driver = setup_driver()

    try:
        # 1. Get World Bank data
        wb_data = get_world_bank_data(country_code)

        # 2. Scrape Google Finance for stock index
        market_data = scrape_google_finance(country, driver)

        # 3. Get top gainers using yfinance (more reliable than scraping)
        if not market_data['top_gainers']:  # Only if Google Finance scraping failed
            top_gainers = get_top_gainers_yfinance(country)
            market_data['top_gainers'] = top_gainers

        # 4. Scrape economic news
        news_headlines = scrape_economic_news(country, driver)

        # 5. Calculate sentiment
        sentiment = calculate_overall_sentiment(news_headlines)

        # Compile all data
        result = {
            'country': country,
            'category': 'economics',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'economic_indicators': {
                'gdp_growth': wb_data.get('gdp_growth', {}),
                'inflation_rate': wb_data.get('inflation', {}),
                'unemployment_rate': wb_data.get('unemployment', {}),
                'stock_index': market_data.get('stock_index', {})
            },
            'market_data': {
                'top_gainers': market_data.get('top_gainers', [])
            },
            'news_headlines': news_headlines[:10],
            'sentiment': sentiment,
            'summary': {
                'economic_health': 'moderate',
                'key_indicators': {
                    'gdp': wb_data.get('gdp_growth', {}).get('value'),
                    'inflation': wb_data.get('inflation', {}).get('value'),
                    'unemployment': wb_data.get('unemployment', {}).get('value')
                },
                'data_sources': ['World Bank API', 'Google Finance', 'Google News']
            }
        }

        print(f"\n{'='*60}")
        print(f"✅ SUCCESSFULLY SCRAPED DATA FOR {country.upper()}")
        print(f"{'='*60}\n")

        return result

    finally:
        # Always close the driver
        driver.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Scrape economics data using 100% free sources'
    )
    parser.add_argument(
        '--country',
        type=str,
        required=True,
        help='Country name (e.g., USA, UK, India, Canada)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='../output/',
        help='Output directory'
    )

    args = parser.parse_args()

    # Scrape data
    data = scrape_economics_data(args.country)

    # Save to file
    output_dir = os.path.join(args.output, args.country)
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{datetime.now().strftime('%Y-%m-%d')}.json"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"📁 Data saved to: {filepath}")
    print(f"\n✨ Done! You can now use this data in your frontend.\n")
