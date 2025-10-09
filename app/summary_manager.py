# app/summary_manager.py
from app.rss_utils import fetch_recent_entries
from app.summarizer import Summarizer
from app.config import Config

class SummaryManager:
    def __init__(self, llm_client):
        self.summarizer = Summarizer(llm_client)
        # Optionally load persistent seen-IDs or timestamps
        self.seen_links = set()

    def get_new_entries(self, feed_list, days_limit=1):
        entries = fetch_recent_entries(feed_list, days_limit=days_limit)
        # filter out seen ones
        new = [e for e in entries if e["link"] not in self.seen_links]
        # optionally update seen
        for e in new:
            self.seen_links.add(e["link"])
        return new

    def summarize(self, subject_area, content_type, audience_key, days_limit=1, top_k=5, bulk=True, summarize_top_entries=False):
        # Fetch the feeds directly
        feeds = Config.SUBJECT_AREAS[subject_area][content_type]

        entries = self.get_new_entries(feeds, days_limit=days_limit)
        if not entries:
            return {"bulk_cost": None, "bulk_summary": None, "top_entries": [], "raw_entries": []}

        # Bulk summary
        bulk_summary, bulk_cost_info, selected_entries = self.summarizer.summarize_bulk(
            entries, subject_area, audience_key, content_type, top_k=top_k
        )

        # Top entries + detailed summaries
        top_entries = []
        if summarize_top_entries and selected_entries:
            for entry in selected_entries:
                summary, cost_info = self.summarizer.summarize_entry(entry, subject_area, audience_key, content_type)
                top_entries.append({"cost": cost_info, "summary": summary,"entry": entry})

        return {
            "bulk_cost": bulk_cost_info,
            "bulk_summary": bulk_summary,
            "top_entries": top_entries,
            "raw_entries": selected_entries
        }
    
    def summarize_selected(self, entry, subject_area, audience_key, content_type):
        summary, cost_info = self.summarizer.summarize_entry(entry, subject_area, audience_key, content_type)
        return {
            "cost": cost_info,
            "summary": summary,
            "entry": entry
        }