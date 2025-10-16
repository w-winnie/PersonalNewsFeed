import time
import gradio as gr
from src.config import Config
from src.llm_client import LLMClient
from src.summary_manager import SummaryManager

session_mgr = None

# ----------------------------
# Backend Logic
# ----------------------------
def summarize_ui(api_key, subject_area, content_type, audience, days_limit):
    global session_mgr
    if not api_key:
        return "⚠️ Please enter a valid OpenAI API key.", gr.update(choices=[], visible=False), None, ""

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

    return bulk_with_cost, gr.update(choices=options, visible=True), raw_entries, f"{len(raw_entries)} entries listed."


def detailed_summary(raw_entries, selection, subject, audience, ctype):
    if not raw_entries:
        return "⚠️ No entries available. Run summarization first."
    if not selection:
        return "⚠️ Please select an entry."

    index = int(selection.split(".")[0]) - 1
    entry = raw_entries[index]
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

# ----------------------------
# UI Definition
# ----------------------------
with gr.Blocks(
    title="Science RSS Summarizer",
    theme=gr.themes.Default(primary_hue="blue", neutral_hue="gray"),
    css="""
        .gradio-container {max-width: 800px; margin: auto;}
        h1, h2, h3 {text-align: center;}
        .gr-button {width: 100%;}
        .loading-box {
            text-align: center;
            padding: 1.2em;
            border-radius: 8px;
            margin-top: 1em;
            font-weight: 500;
            opacity: 0.8;
            background: var(--block-background-fill);
            border: 1px solid var(--block-border-color);
        }
    """
) as ui:

    gr.Markdown("# 🧠 Science RSS Summarizer")
    gr.Markdown("Summarize **scientific news** or **research papers** using OpenAI’s GPT models.")

    with gr.Row():
        api_key = gr.Textbox(label="🔑 OpenAI API Key", type="password", placeholder="sk-...")
        days = gr.Slider(1, 7, value=1, step=1, label="📆 Days Window")

    with gr.Row():
        subject = gr.Dropdown(list(Config.SUBJECT_AREAS.keys()), label="🪐 Subject Area")
        ctype = gr.Dropdown(["news", "papers"], label="🗞️ Content Type")
        audience = gr.Dropdown(list(Config.AUDIENCES.keys()), label="🎯 Audience")

    summarize_btn = gr.Button("🔍 Summarize Latest", variant="primary")

    # Loading placeholder
    loading_box = gr.Markdown("", elem_classes=["loading-box"], visible=False)

    # Output blocks
    bulk_output = gr.Markdown(label="🧠 Overall Summary")
    top_dropdown = gr.Dropdown(label="🔝 Select a Top Entry", interactive=True, visible=False)
    raw_state = gr.State()
    status = gr.Textbox(label="Status", interactive=False, visible=False)
    detail_loading_box = gr.Markdown("", elem_classes=["loading-box"], visible=False)
    detail_out = gr.Markdown(label="📘 Detailed Entry Summary")

    # --------------------------
    # Animated loading simulation
    # --------------------------
    def show_loading(seconds=10, message="⏳ Generating summary"):
        """Show a placeholder box that animates while summarization runs."""
        for i in range(seconds):
            dots = "." * (i % 4)
            yield gr.update(visible=True, value=f"{message}{dots}")
            time.sleep(1)

    # --- Main summarize action ---
    summarize_btn.click(
        fn=show_loading,
        inputs=[],
        outputs=[loading_box],
        show_progress=False,
        queue=True
    ).then(
        fn=summarize_ui,
        inputs=[api_key, subject, ctype, audience, days],
        outputs=[bulk_output, top_dropdown, raw_state, status]
    ).then(
        fn=lambda: gr.update(visible=False),
        inputs=[],
        outputs=[loading_box]
    )

    # --- Detailed entry loading ---
    def show_detail_loading():
        for i in range(6):
            dots = "." * (i % 4)
            yield gr.update(visible=True, value=f"🧩 Summarizing selected article{dots}")
            time.sleep(1)

    top_dropdown.change(
        fn=show_detail_loading,
        inputs=[],
        outputs=[detail_loading_box],
        show_progress=False,
        queue=True
    ).then(
        fn=detailed_summary,
        inputs=[raw_state, top_dropdown, subject, audience, ctype],
        outputs=detail_out
    ).then(
        fn=lambda: gr.update(visible=False),
        inputs=[],
        outputs=[detail_loading_box]
    )

ui.launch()
