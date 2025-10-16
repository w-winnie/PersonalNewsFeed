import re
from urllib.parse import urlparse, urlunparse
from difflib import SequenceMatcher

def normalize_url(url):
    """Strip trailing slashes and UTM params for better matching."""
    parsed = urlparse(url)
    clean_path = parsed.path.rstrip("/")
    return urlunparse(parsed._replace(query="", path=clean_path))

def extract_top_entries_from_summary(summary, entries, max_count=5):
    # pattern = r"Top Sources:\s*(.*?)(?=\n\n|\n---|\Z)"
    pattern = r"(?i)#?\s*Top Sources\s*\n+([\s\S]*?)(?=\n{2,}|---|\Z)"

    matches = re.findall(pattern, summary, re.DOTALL | re.IGNORECASE)

    entry_map = {normalize_url(e["link"]): e for e in entries}

    top_entries = []
    top_urls = set()

    for section in matches:
        # lines = [l.strip() for l in section.strip().splitlines() if l.strip()]
        lines = re.split(r'\n?\s*\d+\.\s+', section.strip())
        lines = [line.strip() for line in lines if line.strip()]

        for line in lines:
            # Normalize all dash types to " - "
            line = re.sub(r"\s*[–—]\s*", " - ", line) 
            # Find URL by regex search
            url_match = re.search(r"https?://[^\s)]+", line) 
            # Skip the entry if cant find URL (no fuzzy matching allowed)
            if not url_match:
                continue
            # Normalize URLs
            url = normalize_url(url_match.group(0)) 
            # Search URL in entries    
            entry = entry_map.get(url) 
            # Add entry if not already added
            if entry and url not in top_urls: 
                top_entries.append(entry)
                top_urls.add(url)
            # Stop if reached max count
            if len(top_entries) >= max_count:
                break
        # if len(top_entries) >= max_count:
        #     break

    return top_entries, top_urls