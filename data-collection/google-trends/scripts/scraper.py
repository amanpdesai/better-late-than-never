#!/usr/bin/env python3
"""
GOOGLE TRENDS SCRAPER (PyTrends + Selenium CSV Export)
======================================================

Fetches trending search data for selected countries using PyTrends,
and falls back to Selenium automation to export CSV data directly
from the Google Trends interface when PyTrends fails.

Supported countries:
    USA, UK, INDIA, CANADA, AUSTRALIA
"""

import argparse
import csv
import json
import logging
import time
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List

from pytrends.request import TrendReq
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------

COUNTRY_CONFIG = {
    "USA": {"geo": "US", "hl": "en-US", "tz": -300, "pn": "united_states"},
    "UK": {"geo": "GB", "hl": "en-GB", "tz": 0, "pn": "united_kingdom"},
    "INDIA": {"geo": "IN", "hl": "en-IN", "tz": 330, "pn": "india"},
    "CANADA": {"geo": "CA", "hl": "en-CA", "tz": -300, "pn": "canada"},
    "AUSTRALIA": {"geo": "AU", "hl": "en-AU", "tz": 600, "pn": "australia"},
}

CATEGORY_KEYWORDS = {
    "sports": ["match", "vs", "league", "cup", "nba", "nfl", "fifa", "cricket"],
    "entertainment": ["movie", "film", "series", "music", "concert", "actor", "song"],
    "news": ["attack", "election", "policy", "president", "minister", "law", "war"],
    "technology": ["iphone", "ai", "tech", "software", "app", "gadget"],
    "business": ["stock", "market", "earnings", "ipo", "crypto", "bitcoin"],
    "health": ["covid", "vaccine", "virus", "health", "disease"],
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------

def categorize_query(query: str) -> str:
    query_lower = query.lower()
    for cat, kws in CATEGORY_KEYWORDS.items():
        if any(kw in query_lower for kw in kws):
            return cat
    return "general"


def parse_trending_csv(csv_text: str, country_code: str) -> List[Dict[str, Any]]:
    """Parse the CSV downloaded from Google Trends Export → CSV"""
    f = StringIO(csv_text)
    reader = csv.DictReader(f)
    results = []

    for row in reader:
        query = (row.get("Trends") or "").strip()
        if not query:
            continue

        traffic_label = (row.get("Search volume") or "").strip()
        started = (row.get("Started") or "").strip()
        ended = (row.get("Ended") or "").strip()
        related_raw = (row.get("Trend breakdown") or "").strip()
        related = [r.strip() for r in related_raw.split(",") if r.strip()]
        explore_link = (row.get("Explore link") or "").strip()

        results.append({
            "query": query,
            "traffic_label": traffic_label,
            "start_time": started or None,
            "end_time": ended or None,
            "related_queries": related,
            "category": categorize_query(query),
            "share_url": explore_link or f"https://trends.google.com/trends/explore?q={query.replace(' ', '+')}&geo={country_code}"
        })

    return results


# ------------------------------------------------------------
# MAIN SCRAPER CLASS
# ------------------------------------------------------------

class GoogleTrendsScraper:
    def __init__(self, country: str):
        country = country.upper()
        if country not in COUNTRY_CONFIG:
            raise ValueError(f"Unsupported country: {country}")
        self.country = country
        self.conf = COUNTRY_CONFIG[country]
        self.trends = TrendReq(hl=self.conf["hl"], tz=self.conf["tz"], geo=self.conf["geo"])

    def fetch(self) -> Dict[str, Any]:
        logging.info(f"Fetching Google Trends data for {self.country}")
        try:
            df = self.trends.trending_searches(pn=self.conf["pn"])
        except Exception as e:
            logging.warning(f"PyTrends failed ({e}), switching to Selenium export.")
            return self._fetch_via_selenium()

        if df.empty:
            logging.warning(f"No PyTrends data found for {self.country}. Using Selenium fallback.")
            return self._fetch_via_selenium()

        queries = df[0].tolist()[:20]
        breakdown = self._category_breakdown(queries)
        summary = self._summary(queries, breakdown)
        return {
            "country": self.country,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "PyTrends",
            "trending_searches": [{"query": q, "category": categorize_query(q)} for q in queries],
            "category_breakdown": breakdown,
            "summary": summary,
        }

    def _fetch_via_selenium(self) -> Dict[str, Any]:
        """Automate export via Selenium (Export ▾ → Download CSV)"""
        logging.info(f"Launching Selenium CSV export for {self.country}")

        download_dir = str((Path.cwd() / "downloads").resolve())
        Path(download_dir).mkdir(parents=True, exist_ok=True)

        # Clean out stale CSVs before run
        for old in Path(download_dir).glob("*.csv"):
            try:
                old.unlink()
            except Exception:
                pass

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1600,1000")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-features=NetworkService,NetworkServiceInProcess")
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        }
        options.add_experimental_option("prefs", prefs)

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        url = f"https://trends.google.com/trends/trendingsearches/daily?geo={self.conf['geo']}"
        logging.info(f"Opening {url}")

        # --- HARD RELOAD SEQUENCE ---
        driver.get("https://trends.google.com")
        time.sleep(2)
        driver.delete_all_cookies()
        driver.execute_cdp_cmd("Network.clearBrowserCache", {})
        driver.execute_cdp_cmd("Network.clearBrowserCookies", {})
        driver.execute_cdp_cmd("ServiceWorker.disable", {})
        driver.get(url)
        time.sleep(8)

        # Verify region text actually matches target
        try:
            region_text = driver.execute_script("""
                const btn = document.querySelector('button[jsname="E2vDFb"]');
                return btn ? btn.innerText : null;
            """)
            logging.info(f"Region selector currently shows: {region_text}")
            if region_text and self.country.lower() not in region_text.lower():
                logging.info("Reselecting region manually...")
                driver.execute_script(f"""
                    const dropdown = document.querySelector('button[jsname="E2vDFb"]');
                    if (dropdown) {{
                        dropdown.click();
                        const items = Array.from(document.querySelectorAll('div[role="menuitem"], span'));
                        const target = items.find(el => el.innerText && el.innerText.toLowerCase().includes("{self.country.lower()}"));
                        if (target) target.click();
                    }}
                """)
                time.sleep(5)
        except Exception as e:
            logging.warning(f"Region reselect check failed: {e}")

        # Scroll to ensure content loads
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(3)

        # --- EXPORT ---
        try:
            export_btn = driver.execute_script("""
                const btns = Array.from(document.querySelectorAll('button, div[role="button"]'));
                return btns.find(b => b.innerText && b.innerText.includes('Export'));
            """)
            if not export_btn:
                raise RuntimeError("Export button not found")
            driver.execute_script("arguments[0].click();", export_btn)
            time.sleep(1)

            csv_btn = driver.execute_script("""
                const items = Array.from(document.querySelectorAll('li, div[role="menuitem"]'));
                return items.find(i => i.innerText && i.innerText.includes('Download CSV'));
            """)
            if not csv_btn:
                raise RuntimeError("CSV option not found")
            driver.execute_script("arguments[0].click();", csv_btn)
            logging.info("Clicked CSV export option, waiting for download...")

            timeout = time.time() + 25
            csv_file = None
            while time.time() < timeout:
                files = list(Path(download_dir).glob("*.csv"))
                if files:
                    csv_file = max(files, key=lambda f: f.stat().st_mtime)
                    break
                time.sleep(1)

            if not csv_file:
                raise RuntimeError("No CSV file downloaded")

            # Rename to prevent confusion
            renamed = csv_file.parent / f"trending_{self.conf['geo']}_{datetime.now().strftime('%Y%m%d-%H%M')}.csv"
            csv_file.rename(renamed)
            logging.info(f"Downloaded {renamed.name}")

            with open(renamed, "r", encoding="utf-8") as f:
                csv_text = f.read()

            driver.quit()

            trends = parse_trending_csv(csv_text, self.conf["geo"])
            breakdown = self._category_breakdown([t["query"] for t in trends])
            summary = self._summary([t["query"] for t in trends], breakdown)

            # Clean up
            try:
                renamed.unlink()
            except Exception:
                pass

            return {
                "country": self.country,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "Selenium Export (Localized Reloaded CSV)",
                "trending_searches": trends,
                "category_breakdown": breakdown,
                "summary": summary,
            }

        except Exception as e:
            logging.error(f"Selenium export failed: {e}")
            driver.quit()
            return {}

    # ------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------
    def _category_breakdown(self, queries: List[str]) -> Dict[str, int]:
        from collections import Counter
        c = Counter(categorize_query(q) for q in queries)
        total = sum(c.values()) or 1
        return {k: int(round((v / total) * 100)) for k, v in c.items()}

    def _summary(self, queries: List[str], breakdown: Dict[str, int]) -> Dict[str, Any]:
        top_category = max(breakdown, key=breakdown.get) if breakdown else "general"
        return {
            "total_trending_searches": len(queries),
            "top_category": top_category,
            "most_searched_term": queries[0] if queries else None,
            "notable_topics": queries[:5],
        }


# ------------------------------------------------------------
# CLI + SAVE
# ------------------------------------------------------------

def save_output(country: str, data: Dict[str, Any], outdir: str = "./output"):
    if not data:
        logging.warning(f"No data to save for {country}")
        return
    directory = Path(outdir) / country
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{datetime.now().strftime('%Y-%m-%d')}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logging.info(f"Saved: {path}")


def main():
    parser = argparse.ArgumentParser(description="Scrape Google Trends (PyTrends + Selenium Export)")
    parser.add_argument("--country", required=True, help="Country name (e.g., USA, UK, India)")
    parser.add_argument("--output", default="../output", help="Output directory")
    parser.add_argument("--print", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    scraper = GoogleTrendsScraper(args.country)
    data = scraper.fetch()
    save_output(scraper.country, data, args.output)

    if args.print:
        print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()