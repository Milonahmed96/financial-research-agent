import gradio as gr
import json
import os
import sys
from agent.graph import MAX_STEPS
from agent.nodes import run_one_react_step

SECTION_ORDER = [
    "company_overview",
    "financials",
    "recent_news",
    "ai_initiatives",
    "analyst_sentiment",
]

SECTION_LABELS = {
    "company_overview":  "🏢 Company Overview",
    "financials":        "💰 Financial Performance",
    "recent_news":       "📰 Recent Developments",
    "ai_initiatives":    "🤖 Technology & AI Strategy",
    "analyst_sentiment": "📈 Analyst Sentiment",
}

def run_research(company):
    if not company.strip():
        yield "Please enter a company name.", "", "", "", "", ""
        return

    state = {
        "company": company.strip(),
        "messages": [],
        "memo_sections": {},
        "step_count": 0,
        "finished": False,
        "awaiting_approval": False,
        "error_log": [],
    }

    required = set(SECTION_ORDER)
    step = 0

    while step < MAX_STEPS:
        state = run_one_react_step(state)
        step += 1

        written = set(state["memo_sections"].keys())
        status = f"⏳ Step {step}/{MAX_STEPS} — Sections complete: {len(written)}/5"

        # Yield current progress
        sections = state["memo_sections"]
        yield (
            status,
            sections.get("company_overview", ""),
            sections.get("financials", ""),
            sections.get("recent_news", ""),
            sections.get("ai_initiatives", ""),
            sections.get("analyst_sentiment", ""),
        )

        if state.get("finished") or required.issubset(written):
            break

    sections = state["memo_sections"]
    status = f"✅ Research complete — {len(sections)}/5 sections — {state['step_count']} steps"

    yield (
        status,
        sections.get("company_overview", "*(not found)*"),
        sections.get("financials", "*(not found)*"),
        sections.get("recent_news", "*(not found)*"),
        sections.get("ai_initiatives", "*(not found)*"),
        sections.get("analyst_sentiment", "*(not found)*"),
    )


# ── Gradio UI ─────────────────────────────────────────────────────────────────
with gr.Blocks(theme=gr.themes.Soft(), title="Financial Research Agent") as demo:

    gr.Markdown("""
    # 📊 Financial Research Agent
    *Autonomous investment research powered by Claude AI · LangGraph · Tavily*

    ---

    ### What is this?
    The **Financial Research Agent** autonomously researches any company and produces a
    structured investment research report — without any manual effort on your part.

    ### How to use it
    1. Enter a company name below *(e.g. HSBC, Barclays, Revolut, JPMorgan)*
    2. Click **Research** — the agent begins working autonomously
    3. Watch each section appear as the agent completes it
    4. Research takes **2–3 minutes**

    ### What the report covers
    🏢 Company Overview · 💰 Financial Performance · 📰 Recent Developments · 🤖 AI Strategy · 📈 Analyst Sentiment

    > ⚠️ *For informational purposes only. Does not constitute financial advice.*
    """)

    with gr.Row():
        company_input = gr.Textbox(
            label="Company Name",
            placeholder="e.g. HSBC, Barclays, Revolut, JPMorgan, Goldman Sachs",
            scale=4
        )
        research_btn = gr.Button("🔍 Research", variant="primary", scale=1)

    status_box = gr.Textbox(
        label="Status",
        value="Enter a company name and click Research to begin.",
        interactive=False
    )

    gr.Markdown("---")
    gr.Markdown("## Investment Research Report")

    overview_box   = gr.Textbox(label="🏢 Company Overview",         lines=5, interactive=False)
    financials_box = gr.Textbox(label="💰 Financial Performance",     lines=5, interactive=False)
    news_box       = gr.Textbox(label="📰 Recent Developments",       lines=5, interactive=False)
    ai_box         = gr.Textbox(label="🤖 Technology & AI Strategy",  lines=5, interactive=False)
    analyst_box    = gr.Textbox(label="📈 Analyst Sentiment",         lines=5, interactive=False)

    gr.Markdown("---")
    gr.Markdown("*Built by Milon Ahmed · MSc Data Science, University of Hertfordshire · March 2026*")

    research_btn.click(
        fn=run_research,
        inputs=[company_input],
        outputs=[status_box, overview_box, financials_box, news_box, ai_box, analyst_box],
    )

demo.launch()