"""
Debug script to test news site scraping and see what's actually on the page
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def test_site(site_name, url):
    """Test scraping a single site and show what we find."""
    print(f"\n{'='*60}")
    print(f"Testing: {site_name}")
    print(f"URL: {url}")
    print(f"{'='*60}\n")

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(30)

    try:
        driver.get(url)
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Try to find all h1, h2, h3 tags
        print("All H1 tags:")
        h1_tags = soup.find_all('h1', limit=5)
        for i, tag in enumerate(h1_tags, 1):
            print(f"  {i}. {tag.get_text(strip=True)[:100]}")
            print(f"     Classes: {tag.get('class')}")

        print("\nAll H2 tags:")
        h2_tags = soup.find_all('h2', limit=5)
        for i, tag in enumerate(h2_tags, 1):
            print(f"  {i}. {tag.get_text(strip=True)[:100]}")
            print(f"     Classes: {tag.get('class')}")

        print("\nAll H3 tags:")
        h3_tags = soup.find_all('h3', limit=5)
        for i, tag in enumerate(h3_tags, 1):
            print(f"  {i}. {tag.get_text(strip=True)[:100]}")
            print(f"     Classes: {tag.get('class')}")

        print("\nAll article tags:")
        articles = soup.find_all('article', limit=5)
        for i, tag in enumerate(articles, 1):
            print(f"  {i}. Classes: {tag.get('class')}")
            headline = tag.find(['h1', 'h2', 'h3'])
            if headline:
                print(f"     Headline: {headline.get_text(strip=True)[:100]}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()


# Test sites that returned 0 articles
sites_to_test = [
    ("BBC", "https://www.bbc.com/news"),
    ("The Guardian", "https://www.theguardian.com/uk"),
    ("NBC News", "https://www.nbcnews.com"),
]

for site_name, url in sites_to_test:
    test_site(site_name, url)
    print("\n" + "="*60 + "\n")
