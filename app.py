# app.py
from fastapi import FastAPI
import gradio as gr

with gr.Blocks() as demo:
    gr.Markdown("# Hello from Gradio + FastAPI 🚀")

api = FastAPI()

@api.get("/api/hello")
def hello():
    return {"msg": "Hello API"}

app = gr.mount_gradio_app(api, demo, path="/")
