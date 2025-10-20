import time
import gradio as gr
from src.config import Config
from src.llm_client import LLMClient
from src.summary_manager import SummaryManager
import pandas as pd 
import io
# from src.response_parser import export_entries_to_csv
import tempfile
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

session_mgr = None

# ----------------------------
# Helper Functions
# ----------------------------
def get_feeds(subject, ctype):
    """Display RSS feeds dynamically based on dropdown selections."""
    if not subject or not ctype:
        return "_Select both Subject Area and Content Type to see feeds._"
    feeds = Config.SUBJECT_AREAS.get(subject, {}).get(ctype, [])
    if not feeds:
        return "_No feeds configured for this selection._"
    return "\n".join([f"- {url}" for url in feeds])

def export_table_to_csv(dataframe):
    csv_buffer = io.StringIO()
    dataframe.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue()

def handle_export(entry_table_df):
    if isinstance(entry_table_df, pd.DataFrame) and not entry_table_df.empty:
        csv_str = export_table_to_csv(entry_table_df)

        output_dir = "exports"
        os.makedirs(output_dir, exist_ok=True)  

        path = os.path.join(output_dir, "exported_entries.csv")
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(csv_str)
        return path

    return None

# ----------------------------
# Main Summarization
# ----------------------------
def summarize_ui(api_key, subject_area, content_type, audience, days_limit, top_entries):
    global session_mgr
    if not api_key:
        return (
            "⚠️ Please enter a valid OpenAI API key.",
            gr.update(choices=[], visible=False),
            None,
            "⚠️ Missing API key.",
            "",
            gr.update(visible=False),
        )

    llm = LLMClient(api_key=api_key)
    session_mgr = SummaryManager(llm)

    feeds = Config.SUBJECT_AREAS[subject_area][content_type]
    feed_list_md = "\n".join([f"- {url}" for url in feeds]) or "_No feeds configured._"

    yield (
        "",
        gr.update(choices=[], visible=False),
        None,
        "Starting summarization......",
        feed_list_md,
        gr.update(visible=True, value="⏳ Working..."),
        []
    )

    progress_text = ""
    result_obj = None

    # Run summarization and stream progress messages
    for result in session_mgr.summarize(
        subject_area=subject_area,
        content_type=content_type,
        audience_key=audience,
        days_limit=days_limit,
        top_k=top_entries,
        summarize_top_entries=False
    ):
        if isinstance(result, str):
            progress_text += result + "\n"
            yield (
                gr.update(),  # bulk_output
                gr.update(choices=[], visible=False),
                None,
                f"### Progress Log\n{progress_text}",
                feed_list_md,
                gr.update(visible=True, value=result),
                []
            )
        elif isinstance(result, dict):
            result_obj = result

    # Process results
    if result_obj:
        bulk = result_obj.get("bulk_summary") or "No new articles found."
        cost = result_obj.get("bulk_cost", 0.0)
        total_entries = result_obj.get("total_entries", 0)
        raw_entries = result_obj.get("raw_entries", [])

        bulk_with_cost = f"💰 **Estimated cost:** ${cost:.4f}\n\n{bulk}"
        options = [f"{idx+1}. {e['title']}" for idx, e in enumerate(raw_entries)]
        status_msg = f"✅ Top **{len(raw_entries)} of {total_entries} entries processed** from {len(feeds)} feed(s)."
        progress_log = f"### Progress Log\n{progress_text}"

        # table_data = [{
        #     "title": e.get("title"),
        #     "published": e.get("published"),
        #     "link": e.get("link"),
        #     "Summary": e.get("summary", "")
        # } for e in raw_entries]

        table_data = pd.DataFrame([{
            "Title": e.get("title", ""),
            "Published": str(e.get("published", "")),
            "Link": e.get("link", ""),
            "Summary": e.get("summary", "")
        } for e in raw_entries])


        yield (
            bulk_with_cost,
            gr.update(choices=options, visible=True),
            raw_entries,
            f"{status_msg}\n\n{progress_log}",
            feed_list_md,
            gr.update(visible=False),
            table_data 
        )


# ----------------------------
# Single Entry Summarization
# ----------------------------
def detailed_summary(raw_entries, selection, subject, audience, ctype):
    """Summarize a single selected entry."""
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
📅 {entry.get('published', '')}
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
        .gradio-container {max-width: 850px; margin: auto;}
        h1, h2, h3 {text-align: center;}
        .gr-button {width: 100%;}
        .loading-box {
            text-align: center;
            padding: 1.2em;
            border-radius: 8px;
            margin-top: 1em;
            font-weight: 500;
            opacity: 0.9;
            background: var(--block-background-fill);
            border: 1px solid var(--block-border-color);
        }
        #entry-table .wrap {
            white-space: normal !important;
        }
        #entry-table td {
            word-break: break-word;
            max-width: 200px;
        }

    """,
) as ui:

    gr.Markdown("# 🧠 Science RSS Summarizer")
    gr.Markdown("Summarize **scientific news** or **research papers** from configured RSS feeds.")

    with gr.Row():
        api_key = gr.Textbox(label="🔑 OpenAI API Key", type="password", placeholder="sk-...")
        days = gr.Slider(1, 7, value=1, step=1, label="Days Window")
        top = gr.Slider(5, 30, value=5, step=1, label="Top Entries")

    with gr.Row():
        subject = gr.Dropdown(list(Config.SUBJECT_AREAS.keys()), label="🪐 Subject Area")
        ctype = gr.Dropdown(["news", "papers"], label="🗞️ Content Type")
        audience = gr.Dropdown(list(Config.AUDIENCES.keys()), label="🎯 Audience")

    # Feeds display BEFORE summarization
    gr.Markdown("### 📡 RSS Feeds to Fetch")
    feeds_preview = gr.Markdown("_Select a subject and type to load feeds._")

    subject.change(fn=get_feeds, inputs=[subject, ctype], outputs=feeds_preview)
    ctype.change(fn=get_feeds, inputs=[subject, ctype], outputs=feeds_preview)

    # --- Main action and progress area ---
    summarize_btn = gr.Button("🔍 Summarize Latest", variant="primary")
    loading_box = gr.Markdown("", elem_classes=["loading-box"], visible=False)
    status = gr.Markdown(label="📊 Progress Log", visible=True)
    # status = gr.Textbox(label="📊 Progress Log", lines=20, visible=True)


    # --- Results ---
    bulk_output = gr.Markdown(label="🧠 Overall Summary")
    top_dropdown = gr.Dropdown(label="🔝 Select an Entry", interactive=True, visible=False)
    summarize_entry_btn = gr.Button("🧩 Summarize This Entry", variant="secondary", visible=False)
    raw_state = gr.State()
    detail_out = gr.Markdown(label="📘 Detailed Entry Summary")
    # entry_table = gr.Dataframe(label="📋 All Retrieved Entries", interactive=False)
    entry_table = gr.Dataframe(
        label="📋 All Retrieved Entries",
        interactive=False,
        headers=["Title", "Published", "Link", "Summary"],
        row_count=10,
        col_count=(4, "fixed"),
        wrap=True,
        # max_rows=50,
        elem_id="entry-table"
    )

    with gr.Row():
        export_btn = gr.Button("📁 Export Table as CSV")
        download_csv = gr.File(label="Download CSV", interactive=False)

    summarize_btn.click(
        fn=summarize_ui,
        inputs=[api_key, subject, ctype, audience, days, top],
        outputs=[bulk_output, top_dropdown, raw_state, status, feeds_preview, loading_box, entry_table],
        show_progress=False,
        queue=True,
    )

    def toggle_summary_button(selection):
        """Show the button only when an entry is selected."""
        return gr.update(visible=bool(selection))

    top_dropdown.change(
        fn=toggle_summary_button,
        inputs=[top_dropdown],
        outputs=[summarize_entry_btn],
    )

    summarize_entry_btn.click(
        fn=detailed_summary,
        inputs=[raw_state, top_dropdown, subject, audience, ctype],
        outputs=detail_out,
    )

    export_btn.click(fn=handle_export, inputs=[entry_table], outputs=[download_csv])


# ui.launch()

# ---------- API MODELS ----------
class SummarizeRequest(BaseModel):
    api_key: str
    subject_area: str
    content_type: str
    audience: str
    days_limit: int = 1
    top_entries: int = 5

class SummarizeEntryRequest(BaseModel):
    api_key: str
    selection: int  # 1-based index from the UI list, or pass the raw entry index you prefer
    subject_area: str
    content_type: str
    audience: str

# ---------- FASTAPI APP ----------
app = FastAPI()

# CORS: allow your proxy Space and later your WordPress origin to fetch JSON
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten later to only your domains
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Gradio UI at the root path
# app = gr.mount_gradio_app(app, ui, path="/")

# ---------- HELPERS ----------
def _run_bulk_summarize(req: SummarizeRequest):
    # reuse your existing code paths; run once and collect final result
    llm = LLMClient(api_key=req.api_key)
    mgr = SummaryManager(llm)

    result_obj = None
    for result in mgr.summarize(
        subject_area=req.subject_area,
        content_type=req.content_type,
        audience_key=req.audience,
        days_limit=req.days_limit,
        top_k=req.top_entries,
        summarize_top_entries=False
    ):
        if isinstance(result, dict):
            result_obj = result

    if not result_obj:
        return {
            "bulk_summary": "No new articles found.",
            "bulk_cost": 0.0,
            "total_entries": 0,
            "entries": []
        }

    # Normalize to a stable JSON shape the proxy/WordPress can consume
    entries = [{
        "title": e.get("title", ""),
        "published": str(e.get("published", "")),
        "link": e.get("link", ""),
        "summary": e.get("summary", "")
    } for e in result_obj.get("raw_entries", [])]

    return {
        "bulk_summary": result_obj.get("bulk_summary") or "No new articles found.",
        "bulk_cost": float(result_obj.get("bulk_cost", 0.0)),
        "total_entries": int(result_obj.get("total_entries", 0)),
        "entries": entries
    }

# ---------- API ROUTES ----------
@app.post("/api/summarize")
def api_summarize(req: SummarizeRequest):
    try:
        if not req.api_key:
            raise HTTPException(status_code=400, detail="Missing API key")
        return _run_bulk_summarize(req)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/summarize_entry")
def api_summarize_entry(req: SummarizeEntryRequest):
    try:
        if not req.api_key:
            raise HTTPException(status_code=400, detail="Missing API key")

        llm = LLMClient(api_key=req.api_key)
        mgr = SummaryManager(llm)

        # We need an entry to summarize; a simple approach is to re-fetch the same bulk
        bulk = _run_bulk_summarize(SummarizeRequest(
            api_key=req.api_key,
            subject_area=req.subject_area,
            content_type=req.content_type,
            audience=req.audience,
            days_limit=1,
            top_entries=10
        ))

        entries = bulk.get("entries", [])
        idx = max(0, min(len(entries)-1, req.selection - 1))
        entry = entries[idx] if entries else None
        if not entry:
            raise HTTPException(status_code=404, detail="No entries found")

        # Prepare the shape expected by your existing summarize_selected()
        raw_like = {
            "title": entry["title"],
            "published": entry["published"],
            "link": entry["link"],
            "summary": entry.get("summary", "")
        }

        result = mgr.summarize_selected(
            raw_like,
            req.subject_area,
            req.audience,
            req.content_type
        )

        return {
            "title": entry["title"],
            "published": entry["published"],
            "link": entry["link"],
            "summary": result.get("summary", ""),
            "cost": float(result.get("cost", 0.0))
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app = gr.mount_gradio_app(app, ui, path="/")
