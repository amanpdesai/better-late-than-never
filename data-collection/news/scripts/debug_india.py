"""
Debug Indian news sites
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
        time.sleep(4)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Try to find all h1, h2, h3 tags
        print("All H1 tags:")
        h1_tags = soup.find_all('h1', limit=5)
        for i, tag in enumerate(h1_tags, 1):
            text = tag.get_text(strip=True)[:100]
            if text:
                print(f"  {i}. {text}")
                print(f"     Classes: {tag.get('class')}")

        print("\nAll H2 tags:")
        h2_tags = soup.find_all('h2', limit=10)
        for i, tag in enumerate(h2_tags, 1):
            text = tag.get_text(strip=True)[:100]
            if text:
                print(f"  {i}. {text}")
                print(f"     Classes: {tag.get('class')}")

        print("\nAll H3 tags:")
        h3_tags = soup.find_all('h3', limit=10)
        for i, tag in enumerate(h3_tags, 1):
            text = tag.get_text(strip=True)[:100]
            if text:
                print(f"  {i}. {text}")
                print(f"     Classes: {tag.get('class')}")

        print("\nAll H4 tags:")
        h4_tags = soup.find_all('h4', limit=10)
        for i, tag in enumerate(h4_tags, 1):
            text = tag.get_text(strip=True)[:100]
            if text:
                print(f"  {i}. {text}")
                print(f"     Classes: {tag.get('class')}")

        print("\nAll 'a' tags with class containing 'headline' or 'title':")
        a_tags = soup.find_all('a', class_=lambda x: x and ('headline' in ' '.join(x).lower() or 'title' in ' '.join(x).lower()), limit=10)
        for i, tag in enumerate(a_tags, 1):
            text = tag.get_text(strip=True)[:100]
            if text and len(text) > 10:
                print(f"  {i}. {text}")
                print(f"     Classes: {tag.get('class')}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()


# Test Indian news sites
sites_to_test = [
    ("Times of India", "https://timesofindia.indiatimes.com"),
    ("NDTV", "https://www.ndtv.com"),
]

for site_name, url in sites_to_test:
    test_site(site_name, url)
