from app.config import Config
from app.prompt_templates import PROMPT_TEMPLATES 
from app.response_parser import extract_top_entries_from_summary

class Summarizer:
    def __init__(self, llm_client):
        self.llm = llm_client

    def get_system_prompt(self, subject_area, audience_key):
        aud_desc = Config.AUDIENCES.get(audience_key, "")
        return (
            f"You are a science writer producing summaries about **{subject_area}**. "
            f"Your audience is: {aud_desc}. Write clearly and engagingly."
        )

    def make_entry_messages(self, entry, subject_area, audience_key, content_type):
        sys_prompt = self.get_system_prompt(subject_area, audience_key)
        user_prompt = PROMPT_TEMPLATES[content_type]["entry"].format(
            subject_area=subject_area,
            title=entry["title"],
            summary=entry["summary"],
            link=entry["link"]
        ).strip()
        return [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}]

    def make_bulk_messages(self, entries, subject_area, audience_key, content_type, top_k=5, max_length=1000):
        sys_prompt = self.get_system_prompt(subject_area, audience_key)
        blocks = []
        for e in entries:
            blocks.append(f"Title: {e['title']}\nSummary: {e['summary']}\nLink: {e['link']}")
            user_prompt = PROMPT_TEMPLATES[content_type]["bulk"].format(
                subject_area=subject_area,
                blocks="\n\n".join(blocks),
                top_entries=top_k,
                summary_length=max_length
            ).strip()
        return [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}]

    def summarize_entry(self, entry, subject_area, audience_key, content_type):
        msg = self.make_entry_messages(entry, subject_area, audience_key, content_type)
        summary, cost = self.llm.chat(msg, return_cost_info=True)
        return summary, cost
    
    def summarize_bulk(self, entries, subject_area, audience_key, content_type, **kwargs):
        msg = self.make_bulk_messages(entries, subject_area, audience_key, content_type, **kwargs)
        summary, cost = self.llm.chat(msg, return_cost_info=True)
        top_entries = extract_top_entries_from_summary(summary, entries, max_count=kwargs.get("top_k", 5))
        return summary, cost, top_entries
