from src.config import Config
from src.prompt_templates import BASE_BULK_TEMPLATE, BASE_ENTRY_TEMPLATE, SYSTEM_PROMPT_TEMPLATE
from src.token_utils import estimate_tokens

class Summarizer:
    def __init__(self, llm_client):
        self.llm = llm_client

    def get_system_prompt(self, subject_area, audience_key):
        aud_desc = Config.AUDIENCES.get(audience_key, "")
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            subject_area=subject_area,
            audience_description=aud_desc
        )
        return system_prompt
    
    def make_entry_messages(self, entry, subject_area, audience_key, content_type, max_length):
        sys_prompt = self.get_system_prompt(subject_area, audience_key)
        user_prompt = BASE_ENTRY_TEMPLATE.format(
            subject_area=subject_area,
            content_type=content_type,
            title=entry["title"],
            summary=entry["summary"],
            link=entry["link"],
            summary_length=max_length
            ).strip()
        return [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}]

    def make_bulk_messages(self, blocks, subject_area, audience_key, content_type, top_k, max_length):
        sys_prompt = self.get_system_prompt(subject_area, audience_key)
        user_prompt = BASE_BULK_TEMPLATE.format(
            content_type=content_type,
            subject_area=subject_area,
            blocks="\n\n".join(blocks),
            top_entries=top_k,
            summary_length=max_length
        ).strip()
        return [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}]
    
    # SUMMARIZE SINGLE ENTRY
    def summarize_entry(self, entry, subject_area, audience_key, content_type):
        msg = self.make_entry_messages(entry, subject_area, audience_key, content_type, max_length=300)
        summary, cost = self.llm.chat(msg, return_cost_info=True)
        return summary, cost
    
    # SUMMARIZE BULK ENTRIES - CHUNK ENTRIES
    def chunk_entries(self, model, entries, token_limit=6000):
        chunks, current, current_tokens = [], [], 0
        for e in entries:
            block = f"Title: {e['title']}\nSummary: {e['summary']}\nLink: {e['link']}"
            tokens = estimate_tokens(model, block)
            if current_tokens + tokens > token_limit and current:
                chunks.append(current)
                current = [e]
                current_tokens = tokens
            else:
                current.append(e)
                current_tokens += tokens
        if current:
            chunks.append(current)
        return chunks

    def summarize_bulk_chunks(self, entries, subject_area, audience_key, content_type, top_k):
        chunked_summaries, chunked_cost = [], 0
        entry_chunks = self.chunk_entries(self.llm.model, entries)
        for chunk in entry_chunks:
            chunk_blocks = [f"Title: {e['title']}\nSummary: {e['summary']}\nLink: {e['link']}" for e in chunk]
            msg = self.make_bulk_messages(
                blocks=chunk_blocks, 
                subject_area=subject_area, 
                audience_key=audience_key,
                content_type=content_type,
                top_k=top_k,
                max_length=1000
            )
            summary, cost = self.llm.chat(msg, return_cost_info=True)
            chunked_summaries.append(summary)
            chunked_cost += cost
        # chunked_summary = "\n\n---\n\n".join(chunked_summaries)
        # unique_top_entries, unique_urls = extract_top_entries_from_summary(chunked_summary, entries, max_count=top_k*len(entry_chunks))
        return chunked_summaries, chunked_cost #,unique_top_entries, unique_urls
    
    def summarize_overall_summaries(self, entries, chunked_summaries, subject_area, audience_key, top_k):
        msg = self.make_bulk_messages(
                blocks=chunked_summaries, 
                audience_key=audience_key,
                subject_area=subject_area,
                content_type='summaries',
                top_k=top_k,
                max_length=2000
            )
        summary, cost = self.llm.chat(msg, return_cost_info=True)
        
        return summary, cost



