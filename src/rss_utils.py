# app/rss_utils.py
import feedparser
from bs4 import BeautifulSoup
import logging
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

def parse_feed(feed_url, cutoff_dt):
    try:
        feed = feedparser.parse(feed_url)
    except Exception as e:
        logger.warning(f"Failed to download {feed_url}: {e}")
        return []
    results = []
    for entry in getattr(feed, "entries", []):
        if hasattr(entry, "published_parsed"):
            published = datetime(*entry.published_parsed[:6])
            if published > cutoff_dt:
                text = BeautifulSoup(entry.get("summary", ""), "html.parser").get_text()
                results.append({
                    "title": entry.get("title"),
                    "link": entry.get("link"),
                    "published": published,
                    "summary": text,
                })
    logger.info(f"From {feed_url}, got {len(results)} new entries")
    return results

def fetch_recent_entries(feed_urls, days_limit=1, max_workers=5):
    cutoff = datetime.utcnow() - timedelta(days=days_limit)
    entries = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(parse_feed, url, cutoff): url for url in feed_urls}
        for fut in as_completed(futures):
            url = futures[fut]
            try:
                res = fut.result()
            except Exception as e:
                logger.warning(f"Error parsing feed {url}: {e}")
                res = []
            entries.extend(res)
    # sort and dedupe if needed
    entries.sort(key=lambda e: e["published"], reverse=True)
    return entries


# def fetch_rss_entries(feed_urls, days_limit=1):
#     entries = []
#     cutoff_date = datetime.utcnow() - timedelta(days=days_limit)

#     for url in feed_urls:
#         try:
#             feed = feedparser.parse(url)
#             logger.info(f"Fetched feed: {url} with {len(feed.entries)} entries")

#             for entry in feed.entries:
#                 if hasattr(entry, 'published_parsed'):
#                     published = datetime(*entry.published_parsed[:6])
#                     if published > cutoff_date:
#                         entries.append({
#                             'title': entry.title,
#                             'link': entry.link,
#                             'published': published,
#                             'summary': BeautifulSoup(entry.summary, 'html.parser').text
#                         })
#         except Exception as e:
#             logger.warning(f"Failed to parse {url}: {str(e)}")

#     logger.info(f"Collected {len(entries)} entries after filtering")
#     return sorted(entries, key=lambda x: x['published'], reverse=True)
