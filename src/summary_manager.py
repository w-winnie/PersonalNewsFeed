# app/summary_manager.py
from src.rss_utils import fetch_recent_entries
from src.summarizer import Summarizer
from src.config import Config
from src.response_parser import extract_top_entries_from_summary

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

        chunked_summaries, chunked_cost = self.summarizer.summarize_bulk_chunks(entries, subject_area, audience_key, content_type, top_k)

        bulk_summary, bulk_cost_info = self.summarizer.summarize_overall_summaries(entries, chunked_summaries, subject_area, audience_key, top_k)

        selected_entries, selected_urls = extract_top_entries_from_summary(bulk_summary, entries, max_count=top_k)

        total_cost_info = chunked_cost + bulk_cost_info
    
        top_entries = []
        if summarize_top_entries and selected_entries:
            for entry in selected_entries:
                summary, cost_info = self.summarizer.summarize_entry(entry, subject_area, audience_key, content_type)
                top_entries.append({"cost": cost_info, "summary": summary,"entry": entry})
                total_cost_info += cost_info

        return {
            "bulk_cost": total_cost_info,
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