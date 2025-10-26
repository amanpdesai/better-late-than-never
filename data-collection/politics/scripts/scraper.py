"""
POLITICS DATA SCRAPER — Free-Source Aggregator (v7, no election)
================================================================

Purpose:
    Collect live political context per country (leaders, government type,
    official updates, and sentiment) using 100% free public data.

Data Sources:
    • Wikipedia (infobox + global heads-of-state list)
    • Official Government RSS feeds
    • Google News site-restricted fallback
    • Google News for political sentiment

Suggested Refresh:
    Every ~6 hours via cron or scheduler.

CLI:
    python scraper.py --country "USA" --output ./output --markdown
"""

import os
import re
import json
import time
import argparse
import requests
import feedparser

from datetime import datetime, timezone
from typing import Any, Dict, List
from bs4 import BeautifulSoup
from pygooglenews import GoogleNews

# ---------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------

COUNTRY_ALIASES = {
    'US': 'United States', 'USA': 'United States',
    'UK': 'United Kingdom', 'GB': 'United Kingdom',
    'IN': 'India', 'CA': 'Canada', 'AU': 'Australia'
}

# Official government news RSS feeds
GOV_FEEDS = {
    'United States': 'https://www.whitehouse.gov/briefing-room/feed/',
    'United Kingdom': 'https://www.gov.uk/government/announcements.atom',
    'India': 'https://pib.gov.in/rss.aspx?mod=latestrelease',
    'Canada': 'https://www.canada.ca/en/news/web-feeds/news.rss',
    'Australia': 'https://www.pm.gov.au/media/rss.xml',
}

# Fallback domains for Google News site-restricted searches
DOMAIN_MAP = {
    'United States': 'whitehouse.gov',
    'United Kingdom': 'gov.uk',
    'India': 'pib.gov.in',
    'Canada': 'canada.ca',
    'Australia': 'pm.gov.au'
}

POSITIVE = ['agreement','deal','reform','support','passes','approves','approved','signed','backs','wins']
NEGATIVE = ['protest','scandal','crisis','dispute','veto','rejects','controversy','divided',
            'impeachment','corruption','allegations','indicted','violence','unrest','deadlock','fails']

REQUESTS_TIMEOUT = 15
MAX_ITEMS = 8

# ---------------------------------------------------------------------
# UTILITIES
# ---------------------------------------------------------------------

def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def requests_get(url: str) -> requests.Response:
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/125.0.0.0 Safari/537.36'
        )
    }
    resp = requests.get(url, headers=headers, timeout=REQUESTS_TIMEOUT)
    resp.raise_for_status()
    return resp

# ---------------------------------------------------------------------
# 1) Wikipedia — leadership, government type, legislature
# ---------------------------------------------------------------------

def parse_infobox(table: BeautifulSoup) -> Dict[str,str]:
    out: Dict[str,str] = {}
    for tr in table.find_all('tr'):
        th = tr.find('th')
        td = tr.find('td')
        if not th or not td:
            continue
        key = th.get_text(strip=True).lower()
        val = td.get_text(" ", strip=True).split('[')[0]
        if 'president' in key and 'vice' not in key:
            out['president'] = val
        elif 'prime minister' in key:
            out['prime_minister'] = val
        elif 'monarch' in key:
            out['monarch'] = val
        elif 'government' in key:
            out['government_type'] = val
        elif 'legislature' in key:
            out['legislature'] = val
    return out

def scrape_wikipedia(country: str) -> Dict[str,str]:
    log(f"Fetching Wikipedia data for {country}")
    variants = [
        f"https://en.wikipedia.org/wiki/Politics_of_{country.replace(' ','_')}",
        f"https://en.wikipedia.org/wiki/Government_of_{country.replace(' ','_')}",
        f"https://en.wikipedia.org/wiki/{country.replace(' ','_')}"
    ]
    for url in variants:
        try:
            resp = requests_get(url)
            soup = BeautifulSoup(resp.text, 'html.parser')
            box = soup.find('table', class_='infobox')
            if box:
                info = parse_infobox(box)
                if info:
                    return info
        except Exception as e:
            log(f"✗ Wikipedia error at {url}: {e}")
            continue
    return {}

def enhance_leadership_if_missing(country: str, data: Dict[str,str]) -> Dict[str,str]:
    """If president or prime_minister missing, fill from global list of heads of state/government."""
    if data.get('president') and data.get('prime_minister'):
        return data
    try:
        log(f"Enhancing leadership info from global list for {country}")
        url = "https://en.wikipedia.org/wiki/List_of_current_heads_of_state_and_government"
        resp = requests_get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        table = soup.find('table', class_='wikitable')
        if not table:
            return data
        for tr in table.find_all('tr'):
            cols = [c.get_text(" ", strip=True) for c in tr.find_all(['td','th'])]
            if cols and country.lower() in cols[0].lower():
                if not data.get('president') and len(cols) > 1:
                    data['president'] = cols[1].split('(')[0].strip()
                if not data.get('prime_minister') and len(cols) > 2:
                    data['prime_minister'] = cols[2].split('(')[0].strip()
                break
    except Exception as e:
        log(f"✗ Leadership enhancer failed: {e}")
    return data

# ---------------------------------------------------------------------
# 2) Government RSS feeds + Google fallback for policies
# ---------------------------------------------------------------------

def scrape_government_rss(country: str) -> List[Dict[str,str]]:
    url = GOV_FEEDS.get(country)
    if not url:
        log(f"⚠ No feed configured for {country}")
        return []
    log(f"Fetching government feed for {country}")
    try:
        resp = requests_get(url)
        feed = feedparser.parse(resp.content)
        out: List[Dict[str,str]] = []
        for e in feed.entries[:MAX_ITEMS]:
            out.append({
                'title': e.get('title',''),
                'url': e.get('link',''),
                'published_at': e.get('published', e.get('updated',''))
            })
        if out:
            log(f"✓ Found {len(out)} official updates via RSS.")
        return out
    except Exception as e:
        log(f"✗ RSS error: {e}")
        return []

def scrape_recent_policies_via_google(country: str) -> List[Dict[str,str]]:
    domain = DOMAIN_MAP.get(country)
    if not domain:
        log(f"⚠ No domain fallback for {country}")
        return []
    gn = GoogleNews(lang='en', country='US')
    query = f"site:{domain} (policy OR 'press release' OR statement OR 'executive order')"
    log(f"Querying Google News for official updates: {query}")
    results: List[Dict[str,str]] = []
    try:
        feed = gn.search(query)
        for e in feed.get('entries', [])[:MAX_ITEMS]:
            results.append({
                'title': e.get('title',''),
                'url': e.get('link',''),
                'source': getattr(e.source, 'title', 'Official Site'),
                'published_at': getattr(e, 'published', '')
            })
        log(f"✓ Found {len(results)} items via Google News fallback for {domain}")
    except Exception as e:
        log(f"✗ Google News official update search failed: {e}")
    return results

# ---------------------------------------------------------------------
# 3) Political news + sentiment
# ---------------------------------------------------------------------

def analyze_sentiment(text: str) -> str:
    t = text.lower()
    if any(k in t for k in NEGATIVE): return 'negative'
    if any(k in t for k in POSITIVE): return 'positive'
    return 'neutral'

def scrape_news(country: str) -> List[Dict[str,Any]]:
    log(f"Gathering political news for {country}")
    results: List[Dict[str,Any]] = []
    try:
        gn = GoogleNews(lang='en', country='US')
        queries = [f"{country} politics", f"{country} government", f"{country} parliament legislature"]
        seen = set()
        for q in queries:
            feed = gn.search(q)
            for e in feed.get('entries', [])[:MAX_ITEMS*2]:
                url = getattr(e, 'link', '')
                title = getattr(e, 'title', '')
                if not url or not title or url in seen:
                    continue
                seen.add(url)
                src = getattr(getattr(e, 'source', None), 'title', 'Unknown')
                published = getattr(e, 'published', '')
                sent = analyze_sentiment(title)
                results.append({'headline': title, 'source': src, 'url': url,
                                'published': published, 'sentiment': sent})
                if len(results) >= MAX_ITEMS:
                    break
            if len(results) >= MAX_ITEMS:
                break
        log(f"✓ Found {len(results)} political news items.")
    except Exception as e:
        log(f"✗ News scraping failed: {e}")
    return results

def summarize_sentiment(items: List[Dict[str,Any]]) -> Dict[str,Any]:
    if not items:
        return {'overall': 'neutral', 'score': 50}
    pos = sum(1 for i in items if i.get('sentiment') == 'positive')
    neg = sum(1 for i in items if i.get('sentiment') == 'negative')
    total = len(items)
    score = int(((pos - neg) / total) * 50 + 50)
    overall = 'positive' if score > 60 else 'negative' if score < 40 else 'neutral'
    return {'overall': overall, 'score': score}

# ---------------------------------------------------------------------
# 4) Orchestrator
# ---------------------------------------------------------------------

def scrape_politics(country: str) -> Dict[str,Any]:
    log(f"=== {country.upper()} ===")
    # Leadership & government
    wiki_data = scrape_wikipedia(country)
    wiki_data = enhance_leadership_if_missing(country, wiki_data)

    # Official updates
    gov_updates = scrape_government_rss(country)
    if not gov_updates:
        gov_updates = scrape_recent_policies_via_google(country)

    # Political news + sentiment
    news_items = scrape_news(country)
    sentiment = summarize_sentiment(news_items)
    key_issues = [n['headline'] for n in news_items[:5]]
    controversies = [n for n in news_items if n.get('sentiment') == 'negative'][:5]

    result = {
        'country': country,
        'category': 'politics',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'leadership_and_government': wiki_data,
        'recent_and_upcoming': {
            'recent_policies': gov_updates
        },
        'political_climate': {
            'key_issues': key_issues,
            'controversies': controversies,
            'recent_headlines': news_items
        },
        'summary': {
            'overall_sentiment': sentiment['overall'],
            'sentiment_score': sentiment['score'],
            'total_items': len(gov_updates) + len(news_items)
        }
    }
    log("✓ Scrape complete.")
    return result

# ---------------------------------------------------------------------
# 5) Markdown summary
# ---------------------------------------------------------------------

def render_markdown(r: Dict[str,Any]) -> str:
    c = r.get('country','')
    lg = r.get('leadership_and_government', {})
    rec = r.get('recent_and_upcoming', {})
    pol = r.get('political_climate', {})
    summ = r.get('summary', {})

    lines = [
        f"# {c} — Politics Snapshot",
        f"_Generated: {r.get('timestamp','')}_",
        "",
        "## Leadership & Government"
    ]
    for k, v in lg.items():
        lines.append(f"- **{k.replace('_',' ').title()}**: {v}")
    lines.append("")
    lines.append("## Recent Official Updates")
    if rec.get('recent_policies'):
        for p in rec['recent_policies'][:MAX_ITEMS]:
            title = p.get('title','').strip()
            url = p.get('url','')
            date = p.get('published_at','')
            lines.append(f"- [{title}]({url}) — _{date}_")
    else:
        lines.append("- None found.")
    lines.append("")
    lines.append("## Key Issues (From Headlines)")
    for h in (pol.get('key_issues', []) or []):
        lines.append(f"- {h}")
    if not pol.get('key_issues'):
        lines.append("- (none)")
    lines.append("")
    lines.append("## Political Climate")
    lines.append(f"- Overall sentiment: **{summ.get('overall_sentiment','neutral')}** ({summ.get('sentiment_score',50)}/100)")
    lines.append("")
    lines.append("## Latest Headlines")
    if pol.get('recent_headlines'):
        for h in pol['recent_headlines'][:MAX_ITEMS]:
            head = h.get('headline','')
            url = h.get('url','')
            src = h.get('source','')
            published = h.get('published','')
            sent = h.get('sentiment','')
            lines.append(f"- [{head}]({url}) — _{src} ({sent})_")
    else:
        lines.append("- (none)")
    lines.append("")
    return "\n".join(lines)

# ---------------------------------------------------------------------
# 6) CLI
# ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='Scrape politics data using 100% free sources.')
    parser.add_argument('--country', required=True, type=str, help='Country name (e.g., "United States", "United Kingdom")')
    parser.add_argument('--output', default='../output', type=str, help='Output directory')
    parser.add_argument('--markdown', action='store_true', help='Also write a Markdown summary file')
    args = parser.parse_args()

    canonical = COUNTRY_ALIASES.get(args.country.strip().upper(), args.country.strip().title())
    report = scrape_politics(canonical)

    outdir = os.path.join(args.output, canonical.replace(" ", "_"))
    os.makedirs(outdir, exist_ok=True)
    json_path = os.path.join(outdir, f"{datetime.now().strftime('%Y-%m-%d')}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    log(f"📁 JSON saved to: {json_path}")

    if args.markdown:
        md_path = os.path.join(outdir, f"{datetime.now().strftime('%Y-%m-%d')}.md")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(render_markdown(report))
        log(f"📝 Markdown saved to: {md_path}")

if __name__ == '__main__':
    main()