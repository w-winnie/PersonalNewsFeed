# app/main.py

import argparse

from src.llm_client import LLMClient
from src.summary_manager import SummaryManager
from src.config import Config


def main():
    parser = argparse.ArgumentParser(description="Generate summaries from scientific RSS feeds.")
    parser.add_argument("--subject", choices=Config.SUBJECT_AREAS.keys(), default="astrophysics", help="Subject area (astrophysics, ai)")
    parser.add_argument("--content_type", choices=Config.CONTENT_TYPES, default="news", help="Content type (news or papers)")
    parser.add_argument("--audience", choices=Config.AUDIENCES.keys(), default="general", help="Target audience (general, astro_enthusiasts, ai_enthusiasts)")
    parser.add_argument("--days", type=int, default=1, help="How many days back to fetch entries")
    parser.add_argument("--top", type=int, default=5, help="How many top entries to show")
    parser.add_argument("--api_key", type=str, required=False, help="OpenAI API Key (or set OPENAI_API_KEY env)")

    args = parser.parse_args()

    print(f"\n Generating summary for subject: {args.subject}, content type: {args.content_type}, audience: {args.audience}")

    llm = LLMClient(api_key=args.api_key)
    manager = SummaryManager(llm)

    result = manager.summarize(
        subject_area=args.subject,
        content_type=args.content_type,
        audience_key=args.audience,
        days_limit=args.days,
        top_k=args.top,
        bulk=True,
        summarize_top_entries=True
    )

    bulk = result.get("bulk_summary")
    top_entries = result.get("top_entries", [])
    cost = result.get("bulk_cost")

    if not bulk:
        print("⚠️ No new entries found.")
        return
    
    print(f"💰 Estimated cost for overall analysis: ${cost:.4f}")
    print("\n🧠 OVERALL SUMMARY:\n")
    print(bulk)

    print("\n🔝 TOP ENTRIES:")
    for i, item in enumerate(top_entries, start=1):
        entry = item["entry"]
        summary = item["summary"]
        print(f"\n{i}. {entry['title']}")
        print(f"📅 Title {entry['published'].strftime('%Y-%m-%d')}")
        print(f"🔗 Link {entry['link']}")
        print(f"💰 Cost: ${item['cost']:.4f}")
        print("📝 Item Summary:")
        print(summary)
        print("-" * 80)

if __name__ == "__main__":
    main()
