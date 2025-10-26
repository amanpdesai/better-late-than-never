#!/usr/bin/env python3
"""
Google Trends scraper that relies solely on free endpoints (pytrends + Trends web API)
to capture what every country is searching for right now.

Example:
    python scraper.py --country USA --limit 20 --output ../output
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

import pandas as pd
import requests
from pytrends.request import TrendReq
from bs4 import BeautifulSoup


DEFAULT_TREND_LIMIT = 20
MAX_INTEREST_BATCH = 5
REQUEST_TIMEOUT = 12
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
)


COUNTRY_CONFIG: Dict[str, Dict[str, Any]] = {
    "USA": {
        "geo": "US",
        "pn": "united_states",
        "hl": "en-US",
        "tz_offset": -300,
        "timezone_label": "America/New_York",
    },
    "UK": {
        "geo": "GB",
        "pn": "united_kingdom",
        "hl": "en-GB",
        "tz_offset": 0,
        "timezone_label": "Europe/London",
    },
    "INDIA": {
        "geo": "IN",
        "pn": "india",
        "hl": "en-IN",
        "tz_offset": 330,
        "timezone_label": "Asia/Kolkata",
    },
    "CANADA": {
        "geo": "CA",
        "pn": "canada",
        "hl": "en-CA",
        "tz_offset": -300,
        "timezone_label": "America/Toronto",
    },
    "AUSTRALIA": {
        "geo": "AU",
        "pn": "australia",
        "hl": "en-AU",
        "tz_offset": 600,
        "timezone_label": "Australia/Sydney",
    },
    "GERMANY": {
        "geo": "DE",
        "pn": "germany",
        "hl": "de-DE",
        "tz_offset": 60,
        "timezone_label": "Europe/Berlin",
    },
    "FRANCE": {
        "geo": "FR",
        "pn": "france",
        "hl": "fr-FR",
        "tz_offset": 60,
        "timezone_label": "Europe/Paris",
    },
    "JAPAN": {
        "geo": "JP",
        "pn": "japan",
        "hl": "ja-JP",
        "tz_offset": 540,
        "timezone_label": "Asia/Tokyo",
    },
    "BRAZIL": {
        "geo": "BR",
        "pn": "brazil",
        "hl": "pt-BR",
        "tz_offset": -180,
        "timezone_label": "America/Sao_Paulo",
    },
    "MEXICO": {
        "geo": "MX",
        "pn": "mexico",
        "hl": "es-419",
        "tz_offset": -360,
        "timezone_label": "America/Mexico_City",
    },
    "SPAIN": {
        "geo": "ES",
        "pn": "spain",
        "hl": "es-ES",
        "tz_offset": 60,
        "timezone_label": "Europe/Madrid",
    },
    "ITALY": {
        "geo": "IT",
        "pn": "italy",
        "hl": "it-IT",
        "tz_offset": 60,
        "timezone_label": "Europe/Rome",
    },
}

COUNTRY_ALIASES = {
    "US": "USA",
    "UNITED STATES": "USA",
    "UNITED STATES OF AMERICA": "USA",
    "UK": "UK",
    "UNITED KINGDOM": "UK",
    "GREAT BRITAIN": "UK",
}

CATEGORY_KEYWORDS = {
    "sports": ["match", "vs", "league", "cup", "fc", "nba", "nfl", "fifa", "olympic", "cricket"],
    "entertainment": ["movie", "film", "series", "song", "music", "concert", "actor", "actress"],
    "news": ["attack", "election", "policy", "government", "president", "minister", "law"],
    "technology": ["iphone", "android", "ai", "tech", "update", "app", "software", "launch"],
    "business": ["stock", "market", "earnings", "ipo", "share", "crypto", "bitcoin"],
    "science": ["nasa", "space", "science", "discovery"],
    "health": ["covid", "vaccine", "flu", "virus", "disease", "health"],
}


logger = logging.getLogger("google_trends_scraper")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


@dataclass
class TrendMeta:
    trend: str = "unknown"
    percent_change: float = 0.0
    trend_duration_hours: int = 0
    sparkline: Optional[List[int]] = None


class GoogleTrendsHTTPClient:
    """Lightweight client to hit the free Google Trends web endpoints."""

    DAILY_URL = "https://trends.google.com/trends/api/dailytrends"

    def __init__(self, geo: str, hl: str, tz_offset: int):
        self.geo = geo
        self.hl = hl
        self.tz_offset = tz_offset
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": USER_AGENT,
                "Accept": "application/json, text/plain, */*",
                "Referer": f"https://trends.google.com/trends/trendingsearches/daily?geo={geo}",
            }
        )
        # Prefetch cookies so the API doesn't instantly 404.
        try:
            self.session.get(
                "https://trends.google.com/",
                params={"geo": self.geo},
                timeout=REQUEST_TIMEOUT,
            )
        except requests.RequestException as exc:
            logger.debug("Bootstrap cookie fetch failed: %s", exc)

    def fetch_daily_trends(self) -> List[Dict[str, Any]]:
        """Return today's trending searches for the configured country."""
        params = {
            "hl": self.hl,
            "tz": self.tz_offset,
            "geo": self.geo,
            "ns": 15,
        }

        try:
            response = self.session.get(
                self.DAILY_URL, params=params, timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.warning("Daily trends request failed: %s", exc)
            return []

        payload = self._parse_response(response.text)
        days = payload.get("default", {}).get("trendingSearchesDays", [])
        if not days:
            return []
        return days[0].get("trendingSearches", [])

    @staticmethod
    def _parse_response(raw_text: str) -> Dict[str, Any]:
        """Google prefixes JSON with )]}',, strip it before loading."""
        sanitized = raw_text.lstrip(")]}', \n")
        try:
            return json.loads(sanitized)
        except json.JSONDecodeError:
            logger.warning("Unable to parse Google Trends payload")
            return {}


class GoogleTrendsScraper:
    """Coordinates fetching + enrichment for a single country."""

    def __init__(self, country: str, limit: int = DEFAULT_TREND_LIMIT):
        canonical = COUNTRY_ALIASES.get(country.strip().upper(), country.strip().upper())
        if canonical not in COUNTRY_CONFIG:
            raise ValueError(
                f"Unsupported country '{country}'. "
                f"Available: {', '.join(sorted(COUNTRY_CONFIG))}"
            )
        self.country_key = canonical
        self.config = COUNTRY_CONFIG[canonical]
        self.limit = limit
        self.pytrends = TrendReq(
            hl=self.config["hl"], tz=self.config.get("tz_offset", 0), geo=self.config["geo"]
        )
        self.http_client = GoogleTrendsHTTPClient(
            geo=self.config["geo"],
            hl=self.config["hl"],
            tz_offset=self.config.get("tz_offset", 0),
        )

    def run(self) -> Dict[str, Any]:
        logger.info("Fetching Google Trends data for %s", self.country_key)

        raw_trends = self.http_client.fetch_daily_trends()
        if not raw_trends:
            logger.warning("No raw trends returned for %s", self.country_key)
            raw_trends = self._fetch_via_selenium()

        trending_queries = self._extract_queries(raw_trends)
        interest_meta = self._build_interest_meta(trending_queries)
        related_query_map = self._fetch_related_queries(trending_queries)
        breakout_searches = self._build_breakout_list(related_query_map)
        geographic_distribution = self._build_geographic_distribution(trending_queries)

        trending_searches = self._build_trending_items(
            raw_trends, interest_meta, related_query_map
        )
        category_breakdown = self._build_category_breakdown(trending_searches)
        summary = self._build_summary(trending_searches, breakout_searches, category_breakdown)

        timestamp = datetime.now(timezone.utc).isoformat()
        result = {
            "country": self.country_key,
            "category": "google_trends",
            "timestamp": timestamp,
            "last_updated": timestamp,
            "trending_searches": trending_searches,
            "breakout_searches": breakout_searches,
            "category_breakdown": category_breakdown,
            "geographic_distribution": geographic_distribution,
            "summary": summary,
            "sources": [
                "Google Trends Daily",
                "PyTrends interest_over_time",
                "PyTrends related_queries",
            ],
        }
        return result

    def _extract_queries(self, raw_trends: List[Dict[str, Any]]) -> List[str]:
        queries = []
        for entry in raw_trends[: self.limit]:
            title_info = entry.get("title", {})
            query = title_info.get("query")
            if not query and entry.get("entityNames"):
                query = entry["entityNames"][0]
            if query:
                queries.append(query)
        return queries

    def _fetch_via_selenium(self) -> List[Dict[str, Any]]:
        """Fallback to headless Selenium scraping if the public API is unavailable."""
        logger.info("Falling back to Selenium scraping for %s", self.country_key)
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
        except ImportError as exc:  # pragma: no cover - selenium optional
            logger.error("Selenium is required for the fallback path: %s", exc)
            return []

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
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
            {
                "title": article.get("title"),
                "source": article.get("source"),
                "url": article.get("url"),
                "published_at": article.get("timeAgo"),
            }
        )
    return news_items


def analyze_interest_series(series: pd.Series) -> TrendMeta:
    values = series.astype(float).tolist()
    if not values:
        return TrendMeta(trend="unknown", percent_change=0.0, trend_duration_hours=0, sparkline=[])

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


def categorize_query(query: str) -> str:
    query_lower = query.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in query_lower for keyword in keywords):
            return category
    return "general"


def parse_traffic(traffic_str: Optional[str]) -> Optional[int]:
    if not traffic_str:
        return None
    normalized = traffic_str.replace("+", "").strip()
    match = re.match(r"([0-9,.]+)\s*([KkMmBb]?)", normalized)
    if not match:
        return None
    value = float(match.group(1).replace(",", ""))
    suffix = match.group(2).upper()
    multiplier = {"": 1, "K": 1_000, "M": 1_000_000, "B": 1_000_000_000}.get(suffix, 1)
    return int(value * multiplier)


def chunked(seq: Sequence[Any], size: int) -> Iterable[List[Any]]:
    for idx in range(0, len(seq), size):
        yield list(seq[idx : idx + size])


def text_or_none(node: Optional[Any]) -> Optional[str]:
    if node is None:
        return None
    return node.get_text(strip=True) or None


def html_unescape(value: str) -> str:
    return (
        value.replace("&amp;", "&")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
    )


def dedupe_preserve(items: List[str]) -> List[str]:
    seen = set()
    result = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def save_output(country: str, data: Dict[str, Any], output_dir: str) -> Path:
    directory = Path(output_dir).joinpath(country)
    directory.mkdir(parents=True, exist_ok=True)
    filename = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d_%H%M%S')}.json"
    path = directory / filename
    with path.open("w", encoding="utf-8") as fp:
        json.dump(data, fp, indent=2)
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape Google Trends data (free sources only).")
    parser.add_argument("--country", required=True, help="Country name or ISO code (e.g., USA, UK, India)")
    parser.add_argument("--limit", type=int, default=DEFAULT_TREND_LIMIT, help="Number of trending searches to capture")
    parser.add_argument("--output", type=str, default="../output", help="Where to store JSON output")
    parser.add_argument(
        "--print",
        dest="should_print",
        action="store_true",
        help="Print the collected data to stdout (useful for debugging)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scraper = GoogleTrendsScraper(country=args.country, limit=args.limit)
    data = scraper.run()
    output_path = save_output(scraper.country_key, data, args.output)
    logger.info("Saved Google Trends data to %s", output_path)
    if args.should_print:
        print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
