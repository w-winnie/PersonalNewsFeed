#minimalistic app
import gradio as gr
from src.config import Config
from src.llm_client import LLMClient
from src.summary_manager import SummaryManager

# Global manager initialized after user enters API key
session_mgr = None

def summarize_ui(api_key, subject_area, content_type, audience, days_limit):
    global session_mgr
    if not api_key:
        return "⚠️ Please enter a valid OpenAI API key.", "", None, None

    try:
        llm = LLMClient(api_key=api_key)
        session_mgr = SummaryManager(llm)

        result = session_mgr.summarize(
            subject_area,
            content_type,
            audience,
            days_limit=days_limit,
            top_k=5,
            bulk=True,
            summarize_top_entries=False
        )

        bulk = result.get("bulk_summary") or "No new articles found."
        cost = result.get("bulk_cost", 0.0)
        bulk_with_cost = f"💰 **Estimated cost:** ${cost:.4f}\n\n" + bulk

        raw_entries = result.get("raw_entries", [])
        options = [f"{idx+1}. {e['title']}" for idx, e in enumerate(raw_entries)]

        return bulk_with_cost, "\n".join(options), raw_entries, f"{len(raw_entries)} entries listed."

    except Exception as e:
        return f"❌ Error: {str(e)}", "", None, ""

def detailed_summary(raw_entries, index, subject, audience, ctype):
    if not raw_entries:
        return "⚠️ No entries available. Run summarization first."
    if not isinstance(index, int) or index < 1 or index > len(raw_entries):
        return "⚠️ Please enter a valid entry number."

    entry = raw_entries[index - 1]
    if not session_mgr:
        return "⚠️ Internal error: Session not initialized."

    result = session_mgr.summarize_selected(entry, subject, audience, ctype)
    return f"""
        ### {entry['title']}
        📅 {entry['published'].strftime('%Y-%m-%d')}
        🔗 [Link]({entry['link']})

        **Summary:**
        {result['summary']}

        💰 Cost: ${result['cost']:.4f}
    """

with gr.Blocks() as ui:
    gr.Markdown("# 📰 Science RSS Summarizer")
    gr.Markdown("Summarize scientific news or research papers using OpenAI's GPT model.")

    with gr.Row():
        api_key = gr.Textbox(label="OpenAI API Key", type="password", placeholder="sk-...")
        subject = gr.Dropdown(list(Config.SUBJECT_AREAS.keys()), label="Subject Area")
        ctype = gr.Dropdown(["news", "papers"], label="Content Type")
        audience = gr.Dropdown(list(Config.AUDIENCES.keys()), label="Audience")
        days = gr.Slider(1, 7, value=1, step=1, label="Days Window")

    summarize_btn = gr.Button("🔍 Summarize Latest")

    bulk_output = gr.Markdown()
    top_list = gr.Textbox(label="Top Entries", lines=5)
    status = gr.Textbox(label="Status", interactive=False)
    raw_state = gr.State()

    summarize_btn.click(
        fn=summarize_ui,
        inputs=[api_key, subject, ctype, audience, days],
        outputs=[bulk_output, top_list, raw_state, status]
    )

    gr.Markdown("## 🔎 View Detailed Summary of a Top Entry")
    top_select = gr.Number(label="Enter Entry Number", value=1, precision=0)
    detail_btn = gr.Button("Show Entry Summary")
    detail_out = gr.Markdown()

    detail_btn.click(
        fn=detailed_summary,
        inputs=[raw_state, top_select, subject, audience, ctype],
        outputs=detail_out
    )

ui.launch()
