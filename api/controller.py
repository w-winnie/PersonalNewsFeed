# api/controller.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
# import gradio as gr
from src.llm_client import LLMClient
from src.summary_manager import SummaryManager

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
