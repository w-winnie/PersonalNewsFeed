import re
from urllib.parse import urlparse, urlunparse

def normalize_url(url):
    """Strip trailing slashes and UTM params for better matching."""
    parsed = urlparse(url)
    clean_path = parsed.path.rstrip("/")
    return urlunparse(parsed._replace(query="", path=clean_path))

def extract_top_entries_from_summary(summary, entries, max_count=5):
    """Extract top entries robustly from the bulk summary."""
    pattern = r"Top Source Links:\s*(.*?)(?:\n\n|\Z)"
    match = re.search(pattern, summary, re.DOTALL | re.IGNORECASE)
    if not match:
        return []

    section = match.group(1)
    top_entries = []

    # Normalize entry links for comparison
    entry_map = {normalize_url(e["link"]): e for e in entries}

    lines = [l.strip() for l in section.strip().splitlines() if l.strip()]

    for line in lines:
        # Normalize all dash types to " - "
        line = re.sub(r"\s*[–—]\s*", " - ", line)
        
        # Extract URL directly via regex
        url_match = re.search(r"https?://[^\s)]+", line)
        if not url_match:
            continue

        url = normalize_url(url_match.group(0))
        entry = entry_map.get(url)

        if entry and entry not in top_entries:
            top_entries.append(entry)

        if len(top_entries) >= max_count:
            break

    return top_entries
