# app/summary_manager.py
from src.rss_utils import fetch_recent_entries
from src.summarizer import Summarizer
from src.config import Config
from src.response_parser import extract_top_entries_from_summary
from src.logger import setup_logger

logger = setup_logger(__name__)

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
    
    def summarize_selected(self, entry, subject_area, audience_key, content_type):
        summary, cost_info = self.summarizer.summarize_entry(entry, subject_area, audience_key, content_type)
        return {
            "cost": cost_info,
            "summary": summary,
            "entry": entry
        }

    def summarize(self, subject_area, content_type, audience_key, days_limit=1, top_k=5, summarize_top_entries=False):
        feeds = Config.SUBJECT_AREAS[subject_area][content_type]
        yield "📡 Fetching new entries from {} RSS feed(s)...".format(len(feeds))

        entries = self.get_new_entries(feeds, days_limit=days_limit)
        total_entries = len(entries)

        if not entries:
            yield "⚠️ No new entries found."
            yield {
                "bulk_cost": None,
                "bulk_summary": "No new articles found.",
                "top_entries": [],
                "raw_entries": [],
                "total_entries": 0,
            }
            return

        yield f"📰 {total_entries} entries fetched. Preparing summaries..."
        yield "✍️ Summarizing chunks (this may take a few minutes)..."
        chunked_summaries, chunked_cost = self.summarizer.summarize_bulk_chunks(
            entries, subject_area, audience_key, content_type, top_k
        )
        yield f"✅ Chunked summaries completed. ({len(chunked_summaries)} chunks processed)"

        yield "🧠 Creating overall summary across all chunks..."
        bulk_summary, bulk_cost_info = self.summarizer.summarize_overall_summaries(
            entries, chunked_summaries, subject_area, audience_key, top_k
        )

        yield "🔎 Extracting top trending or impactful entries..."
        selected_entries, selected_urls = extract_top_entries_from_summary(
            bulk_summary, entries, max_count=top_k
        )

        total_cost_info = chunked_cost + bulk_cost_info

        top_entries = []
        if summarize_top_entries and selected_entries:
            yield "🧩 Summarizing top entries individually..."
            for i, entry in enumerate(selected_entries):
                yield f"   → Summarizing top entry {i+1}/{len(selected_entries)}..."
                summary, cost_info = self.summarizer.summarize_entry(
                    entry, subject_area, audience_key, content_type
                )
                top_entries.append({"cost": cost_info, "summary": summary, "entry": entry})
                total_cost_info += cost_info

        yield "✅ Summarization complete!"
        yield {
            "bulk_cost": total_cost_info,
            "bulk_summary": bulk_summary,
            "top_entries": top_entries,
            "raw_entries": entries,
            "total_entries": total_entries,
        }

    def summarize1(self, subject_area, content_type, audience_key, days_limit=1, top_k=5, summarize_top_entries=False):

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
            "raw_entries": entries,
            "total_entries": len(entries)
        }
