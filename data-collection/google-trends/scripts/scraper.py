#!/usr/bin/env python3
"""
GOOGLE TRENDS SCRAPER (PyTrends + Selenium Fallback)
====================================================

Fetches trending search data for selected countries using PyTrends,
and falls back to Selenium to download CSV data directly from the
Google Trends UI when the API returns 404 or empty results.

Supported countries:
    USA, UK, INDIA, CANADA, AUSTRALIA
"""

import argparse
import csv
import json
import logging
import os
import re
import time
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from pytrends.request import TrendReq
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


# ---------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------

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


# ---------------------------------------------------------------------
# UTILITIES
# ---------------------------------------------------------------------

def categorize_query(query: str) -> str:
    q = query.lower()
    for cat, kws in CATEGORY_KEYWORDS.items():
        if any(kw in q for kw in kws):
            return cat
    return "general"


def parse_csv_text(csv_text: str, geo: str) -> List[Dict[str, Any]]:
    """Parse Google Trends CSV export into structured list."""
    reader = csv.DictReader(StringIO(csv_text))
    results = []
    for row in reader:
        title = row.get("Title") or row.get("title")
        if not title:
            continue
        traffic = row.get("Traffic", "")
        related = row.get("Related queries", "")
        snippet = row.get("Articles", "")
        results.append({
            "query": title,
            "traffic_label": traffic,
            "related_queries": [r.strip() for r in related.split(",") if r.strip()],
            "snippet": snippet,
            "category": categorize_query(title),
            "share_url": f"https://trends.google.com/trends/explore?q={title.replace(' ', '+')}&geo={geo}",
        })
    return results

def parse_trending_csv(csv_text: str, country_code: str) -> List[Dict[str, Any]]:
    """
    Parse the CSV downloaded from Google Trends Export → CSV
    """
    f = StringIO(csv_text)
    reader = csv.DictReader(f)
    results = []

    for row in reader:
        title = row.get("Title") or row.get("title")
        if not title:
            continue
        traffic = row.get("Traffic", "")
        related = row.get("Related queries", "")
        snippet = row.get("Articles", "")

        results.append({
            "query": title.strip(),
            "traffic_label": traffic.strip(),
            "related_queries": [r.strip() for r in related.split(",") if r.strip()],
            "snippet": snippet.strip(),
            "category": categorize_query(title),
            "share_url": f"https://trends.google.com/trends/explore?q={title.replace(' ', '+')}&geo={country_code}",
        })

    return results



# ---------------------------------------------------------------------
# MAIN SCRAPER
# ---------------------------------------------------------------------

class GoogleTrendsScraper:
    def __init__(self, country: str):
        country = country.upper()
        if country not in COUNTRY_CONFIG:
            raise ValueError(f"Unsupported country: {country}")
        self.country = country
        self.conf = COUNTRY_CONFIG[country]
        self.trends = TrendReq(hl=self.conf["hl"], tz=self.conf["tz"], geo=self.conf["geo"])

    # =====================================================
    # PRIMARY FETCH (PyTrends)
    # =====================================================
    def fetch(self) -> Dict[str, Any]:
        logging.info(f"Fetching Google Trends data for {self.country}")
        try:
            df = self.trends.trending_searches(pn=self.conf["pn"])
        except Exception as e:
            logging.warning(f"PyTrends failed ({e}), switching to Selenium fallback.")
            return self._fetch_via_selenium()

        if df.empty:
            logging.warning(f"No PyTrends data found for {self.country}. Using Selenium fallback.")
            return self._fetch_via_selenium()

        queries = df[0].tolist()[:20]
        breakdown = self._category_breakdown(queries)
        summary = self._summary(queries, breakdown)

        data = {
            "country": self.country,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "PyTrends",
            "trending_searches": [{"query": q, "category": categorize_query(q)} for q in queries],
            "category_breakdown": breakdown,
            "summary": summary,
        }
        return data

    # =====================================================
    # FALLBACK (Selenium Automation)
    # =====================================================
    def _fetch_via_selenium(self) -> Dict[str, Any]:
        logging.info(f"Launching Selenium CSV export for {self.country}")

        download_dir = str((Path.cwd() / "downloads").resolve())
        Path(download_dir).mkdir(parents=True, exist_ok=True)

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
<<<<<<< HEAD
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1400,900")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )

        driver = None
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.get(
                f"https://trends.google.com/trends/trendingsearches/daily?geo={self.config['geo']}"
            )
            driver.implicitly_wait(5)

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            rows = soup.select("tr.enOdEe-wZVHld-xMbwt")
            parsed_rows: List[Dict[str, Any]] = []

            for row in rows[: self.limit]:
                query = text_or_none(row.select_one("div.mZ3RIc"))
                if not query:
                    continue

                traffic_text = None
                traffic_el = row.select_one("div.qNpYPd")
                if traffic_el:
                    traffic_text = traffic_el.get_text(strip=True).replace(" searches", "")

                percent_text = text_or_none(row.select_one("div.TXt85b"))
                trend_state = text_or_none(row.select_one("div.QxIiwc div"))
                trend_icon = text_or_none(row.select_one("div.QxIiwc i"))
                recency = text_or_none(row.select_one("div.A7jE4")) or text_or_none(
                    row.select_one("td.WirRge .vdw3Ld")
                )

                related_terms = []
                for button in row.select("td.xm9Xec button[data-term]"):
                    term = button.get("data-term")
                    if term:
                        related_terms.append(html_unescape(term))

                metadata = {
                    "percent_label": percent_text,
                    "trend_state": trend_state,
                    "trend_icon": trend_icon,
                    "last_seen": recency,
                }

                parsed_rows.append(
                    {
                        "title": {"query": html_unescape(query)},
                        "formattedTraffic": traffic_text,
                        "articles": [],
                        "entityNames": [],
                        "relatedQueries": [{"query": rq} for rq in dedupe_preserve(related_terms)],
                        "metadata": metadata,
                    }
                )

            logger.info(
                "Selenium fallback captured %d rows for %s",
                len(parsed_rows),
                self.country_key,
            )
            return parsed_rows

        except Exception as exc:  # noqa: BLE001
            logger.error("Selenium fallback failed: %s", exc)
            return []
        finally:
            if driver:
                driver.quit()

    def _build_interest_meta(self, queries: Sequence[str]) -> Dict[str, TrendMeta]:
        """Fetch hourly interest history per query to infer the trend direction."""
        meta: Dict[str, TrendMeta] = {}
        unique_queries = list(dict.fromkeys(queries))
        logger.info(f"Building interest meta for {len(unique_queries)} queries: {unique_queries[:5]}...")
        
        for batch in chunked(unique_queries, MAX_INTEREST_BATCH):
            if not batch:
                continue
            try:
                logger.debug(f"Fetching interest data for batch: {batch}")
                self.pytrends.build_payload(
                    batch, timeframe="now 1-d", geo=self.config["geo"]
                )
                df = self.pytrends.interest_over_time()
                logger.debug(f"Interest data shape: {df.shape}, columns: {list(df.columns)}")
            except Exception as exc:  # noqa: BLE001
                logger.warning("interest_over_time failed for %s: %s", batch, exc)
                continue

            if df.empty:
                logger.warning(f"Empty interest data for batch: {batch}")
                continue

            for query in batch:
                if query not in df.columns:
                    logger.debug(f"Query '{query}' not found in interest data columns")
                    continue
                series = df[query].dropna()
                if series.empty:
                    logger.debug(f"Empty series for query: {query}")
                    continue
                logger.debug(f"Analyzing series for '{query}': {series.tolist()}")
                meta[query] = analyze_interest_series(series)
        
        logger.info(f"Built interest meta for {len(meta)} queries")
        return meta

    def _fetch_related_queries(self, queries: Sequence[str]) -> Dict[str, List[str]]:
        related: Dict[str, List[str]] = {}
        seed = list(dict.fromkeys(queries))[:MAX_INTEREST_BATCH]
        if not seed:
            return related

        try:
            self.pytrends.build_payload(seed, timeframe="now 7-d", geo=self.config["geo"])
            response = self.pytrends.related_queries()
        except Exception as exc:  # noqa: BLE001
            logger.debug("related_queries failed: %s", exc)
            return related

        for query, payload in response.items():
            queries_df = payload.get("top")
            rising_df = payload.get("rising")
            combined = []
            if isinstance(queries_df, pd.DataFrame):
                combined.extend(queries_df["query"].tolist())
            if isinstance(rising_df, pd.DataFrame):
                combined.extend(rising_df["query"].tolist())
            if combined:
                related[query] = list(dict.fromkeys(combined))
        return related

    def _build_breakout_list(
        self, related_query_map: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        breakouts: List[Dict[str, Any]] = []
        for query, related_list in related_query_map.items():
            for related in related_list[:3]:
                if related.lower() == query.lower():
                    continue
                breakouts.append(
                    {
                        "query": related,
                        "parent_query": query,
                        "growth": "5000%+",
                        "category": categorize_query(related),
                    }
                )
        # Deduplicate while preserving order
        seen = set()
        deduped: List[Dict[str, Any]] = []
        for item in breakouts:
            key = item["query"].lower()
            if key in seen:
                continue
            deduped.append(item)
            seen.add(key)
        return deduped[:15]

    def _build_geographic_distribution(self, queries: Sequence[str]) -> Dict[str, float]:
        seed = list(dict.fromkeys(queries))[:MAX_INTEREST_BATCH]
        if not seed:
            return {}

        try:
            self.pytrends.build_payload(seed, timeframe="now 7-d", geo=self.config["geo"])
            df = self.pytrends.interest_by_region(resolution="REGION", inc_low_vol=True)
        except Exception as exc:  # noqa: BLE001
            logger.debug("interest_by_region failed: %s", exc)
            return {}

        if df.empty:
            return {}

        df["total"] = df.sum(axis=1)
        df = df[df["total"] > 0]
        if df.empty:
            return {}

        top_regions = df["total"].nlargest(8)
        total_sum = float(top_regions.sum()) or 1.0
        return {
            region: round((value / total_sum) * 100, 1)
            for region, value in top_regions.to_dict().items()
        }

    def _build_trending_items(
        self,
        raw_trends: List[Dict[str, Any]],
        interest_meta: Dict[str, TrendMeta],
        related_query_map: Dict[str, List[str]],
    ) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        for idx, entry in enumerate(raw_trends[: self.limit], start=1):
            title_info = entry.get("title", {})
            query = title_info.get("query")
            if not query and entry.get("entityNames"):
                query = entry["entityNames"][0]
            if not query:
                continue

            meta = interest_meta.get(query, TrendMeta())
            fallback_related: List[str] = []
            raw_related = entry.get("relatedQueries") or []
            for related in raw_related:
                if isinstance(related, dict) and related.get("query"):
                    fallback_related.append(related["query"])
                elif isinstance(related, str):
                    fallback_related.append(related)
            related_queries = related_query_map.get(query, fallback_related)

            item = {
                "rank": idx,
                "query": query,
                "search_volume": entry.get("formattedTraffic"),
                "traffic": parse_traffic(entry.get("formattedTraffic")),
                "category": categorize_query(query),
                "trend": meta.trend,
                "trend_duration_hours": meta.trend_duration_hours,
                "percent_change": round(meta.percent_change, 2),
                "trend_sparkline": meta.sparkline or [],
                "related_queries": related_queries[:5],
                "related_news": build_related_news(entry.get("articles", [])),
                "share_url": entry.get("shareUrl"),
                "snippet": (entry.get("articles") or [{}])[0].get("snippet"),
            }
            items.append(item)
        return items

    def _build_category_breakdown(self, items: Sequence[Dict[str, Any]]) -> Dict[str, int]:
        counts = Counter(item["category"] for item in items if item.get("category"))
        total = sum(counts.values()) or 1
        return {category: int(round((value / total) * 100)) for category, value in counts.items()}

    def _build_summary(
        self,
        trending: Sequence[Dict[str, Any]],
        breakout: Sequence[Dict[str, Any]],
        breakdown: Dict[str, int],
    ) -> Dict[str, Any]:
        top_category = max(breakdown, key=breakdown.get) if breakdown else None
        notable_topics = [item["query"] for item in trending[:5]]
        summary = {
            "total_trending_searches": len(trending),
            "total_breakout_searches": len(breakout),
            "top_category": top_category,
            "most_searched_term": trending[0]["query"] if trending else None,
            "notable_topics": notable_topics,
        }
        return summary


def build_related_news(articles: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    news_items: List[Dict[str, Any]] = []
    if not articles:
        return news_items
    for article in articles[:3]:
        news_items.append(
=======
        options.add_argument("--window-size=1600,1000")
        options.add_experimental_option(
            "prefs",
>>>>>>> b081fd5 (merging to main)
            {
                "download.default_directory": download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
            },
        )

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        url = f"https://trends.google.com/trending?geo={self.conf['geo']}"
        driver.get(url)
        logging.info("Waiting for Export button...")
        time.sleep(6)

        try:
            # The Export button lives inside a shadow DOM component.
            # We'll query all buttons and look for one that includes "Export".
            export_btn = driver.execute_script("""
                const btns = Array.from(document.querySelectorAll('button, div[role="button"]'));
                return btns.find(b => b.innerText && b.innerText.includes('Export'));
            """)
            if not export_btn:
                raise RuntimeError("Export button not found")

            driver.execute_script("arguments[0].click();", export_btn)
            time.sleep(1)

            # Click the "Download CSV" menu item
            csv_btn = driver.execute_script("""
                const items = Array.from(document.querySelectorAll('li, div[role="menuitem"]'));
                return items.find(i => i.innerText && i.innerText.includes('Download CSV'));
            """)
            if not csv_btn:
                raise RuntimeError("CSV option not found")

            driver.execute_script("arguments[0].click();", csv_btn)
            logging.info("Clicked CSV export option, waiting for download...")

            # Wait for the file to appear
            timeout = time.time() + 20
            csv_file = None
            while time.time() < timeout:
                files = list(Path(download_dir).glob("*.csv"))
                if files:
                    csv_file = files[0]
                    break
                time.sleep(1)

            if not csv_file:
                raise RuntimeError("No CSV file downloaded")

            # Read and parse CSV
            with open(csv_file, "r", encoding="utf-8") as f:
                text = f.read()

            driver.quit()
            logging.info(f"Successfully downloaded {csv_file.name}")

            trends = parse_trending_csv(text, self.conf["geo"])
            breakdown = self._category_breakdown(trends)
            summary = self._summary(trends, breakdown)

            return {
                "country": self.country,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "Selenium Export (Downloaded CSV)",
                "trending_searches": trends,
                "category_breakdown": breakdown,
                "summary": summary,
            }

        except Exception as e:
            logging.error(f"Selenium export failed: {e}")
            driver.quit()
            return {}

    # =====================================================
    # HELPERS
    # =====================================================
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


# ---------------------------------------------------------------------
# SAVE + CLI
# ---------------------------------------------------------------------

<<<<<<< HEAD
    # Calculate percent change from first to last value
    first, last = values[0], values[-1]
    percent_change = ((last - first) / max(first, 1)) * 100 if first > 0 else 0.0

    # Determine trend based on percent change
    trend = "steady"
    if percent_change > 15:
        trend = "rising"
    elif percent_change < -15:
        trend = "falling"

    # Calculate consecutive growth hours (looking at recent trend)
    duration = consecutive_growth_hours(values)

    # Debug logging to see what's happening
    logger.debug(f"Interest series analysis: first={first}, last={last}, change={percent_change:.2f}%, trend={trend}")

    return TrendMeta(
        trend=trend,
        percent_change=percent_change,
        trend_duration_hours=duration,
        sparkline=values[-12:],
    )


def consecutive_growth_hours(values: List[float]) -> int:
    """Calculate consecutive hours of growth/decline from the end of the series."""
    if len(values) < 2:
        return 0
    
    duration = 0
    # Look backwards from the most recent value
    for idx in range(len(values) - 1, 0, -1):
        if values[idx] > values[idx - 1]:
            duration += 1
        else:
            break
    
    # Also check for consecutive decline
    decline_duration = 0
    for idx in range(len(values) - 1, 0, -1):
        if values[idx] < values[idx - 1]:
            decline_duration += 1
        else:
            break
    
    # Return the longer duration (growth or decline)
    return max(duration, decline_duration)
=======
def save_output(country: str, data: Dict[str, Any], outdir: str = "./output"):
    if not data:
        logging.warning(f"No data to save for {country}")
        return
    path = Path(outdir) / country / f"{datetime.now().strftime('%Y-%m-%d')}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logging.info(f"Saved: {path}")


def main():
    parser = argparse.ArgumentParser(description="Scrape Google Trends (PyTrends + Selenium Fallback)")
    parser.add_argument("--country", required=True, help="Country name (e.g., USA, UK, India, Canada, Australia)")
    parser.add_argument("--output", default="./output", help="Output directory")
    parser.add_argument("--print", action="store_true", help="Print JSON output")
    args = parser.parse_args()
>>>>>>> b081fd5 (merging to main)

    scraper = GoogleTrendsScraper(args.country)
    data = scraper.fetch()
    save_output(scraper.country, data, args.output)

    if args.print:
        print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
