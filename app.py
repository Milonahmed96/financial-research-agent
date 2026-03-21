import streamlit as st
import json
import os
import subprocess
import time
import sys

st.set_page_config(
    page_title="Financial Research Agent",
    page_icon="📊",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stTitle { color: #1B3A5C; }
    .section-card {
        background: white;
        border-radius: 10px;
        padding: 20px 25px;
        margin-bottom: 20px;
        border-left: 4px solid #2E75B6;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }
    .section-title {
        color: #1B3A5C;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .section-content {
        color: #333;
        font-size: 0.97rem;
        line-height: 1.7;
    }
    .metric-box {
        background: #1B3A5C;
        color: white;
        border-radius: 8px;
        padding: 14px 20px;
        text-align: center;
    }
    .log-line { font-size: 0.82rem; color: #555; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 📊 Financial Research Agent")
st.markdown("*Autonomous investment research powered by Claude AI · LangGraph · Tavily*")
st.divider()

col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("""
    ### What is this?
    The **Financial Research Agent** is an autonomous AI system that researches any company
    and produces a structured investment research report — without any manual effort on your part.

    Simply enter a company name, click **Research**, and the agent autonomously searches the web,
    analyses findings, and writes a professional five-section report in 2–3 minutes.

    ### What the report covers
    🏢 **Company Overview** — business model, divisions, and market position  
    💰 **Financial Performance** — revenue, profit, key ratios, and growth  
    📰 **Recent Developments** — news, acquisitions, and strategic announcements  
    🤖 **Technology & AI Strategy** — AI investments and digital transformation  
    📈 **Analyst Sentiment** — consensus ratings, price targets, and outlook
    """)

with col2:
    st.markdown("""
    ### How to use it
    **Step 1** — Type a company name in the search box below  
    *(e.g. HSBC, Barclays, Revolut, JPMorgan, Apple)*

    **Step 2** — Click the **Research** button

    **Step 3** — Wait 2–3 minutes while the agent works autonomously

    **Step 4** — Review the report and download as **PDF** or **Markdown**

    ### How it works
    The agent runs a **ReAct loop** — it reasons about what to search,
    calls web search and fetch tools, reads results, and writes each
    section as soon as it has enough data. Up to 20 autonomous steps per report.

    > ⚠️ *For informational purposes only. Does not constitute financial advice.
    Always verify from primary sources before making financial decisions.*
    """)

st.divider()

# ── Session state ─────────────────────────────────────────────────────────────
defaults = {
    "process": None,
    "company": None,
    "memo_loaded": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Section display order ─────────────────────────────────────────────────────
SECTION_ORDER = [
    "company_overview",
    "financials",
    "recent_news",
    "ai_initiatives",
    "analyst_sentiment",
]

SECTION_ICONS = {
    "company_overview":  "🏢",
    "financials":        "💰",
    "recent_news":       "📰",
    "ai_initiatives":    "🤖",
    "analyst_sentiment": "📈",
}

SECTION_LABELS = {
    "company_overview":  "Company Overview",
    "financials":        "Financials",
    "recent_news":       "Recent News",
    "ai_initiatives":    "AI Initiatives",
    "analyst_sentiment": "Analyst Sentiment",
}

# ── Input panel ───────────────────────────────────────────────────────────────
with st.container():
    col1, col2 = st.columns([4, 1])
    with col1:
        company = st.text_input(
            "Enter a company name to research",
            placeholder="e.g. HSBC, Barclays, Revolut, JPMorgan, Goldman Sachs",
            disabled=st.session_state.process is not None,
            label_visibility="collapsed"
        )
    with col2:
        run_button = st.button(
            "🔍  Research",
            disabled=st.session_state.process is not None or not company,
            use_container_width=True,
            type="primary"
        )

st.caption("The agent autonomously searches the web, analyses findings, and writes a structured investment memo.")
st.divider()

# ── Launch agent ──────────────────────────────────────────────────────────────
if run_button and company:
    os.makedirs("outputs", exist_ok=True)
    for fname in ["outputs/latest_result.json", "outputs/progress.txt"]:
        if os.path.exists(fname):
            os.remove(fname)

    st.session_state.company = company
    st.session_state.memo_loaded = False

    process = subprocess.Popen(
        [sys.executable, "run_agent.py", company],
        stdout=open("outputs/progress.txt", "w", encoding="utf-8"),
        stderr=subprocess.STDOUT
    )
    st.session_state.process = process
    st.rerun()

# ── Polling ───────────────────────────────────────────────────────────────────
if st.session_state.process is not None:
    process = st.session_state.process
    result_path = "outputs/latest_result.json"
    poll = process.poll()

    if poll is None:
        # Still running
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class='metric-box'>
                <div style='font-size:0.8rem;opacity:0.8'>Researching</div>
                <div style='font-size:1.3rem;font-weight:700'>{st.session_state.company}</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='metric-box'>
                <div style='font-size:0.8rem;opacity:0.8'>Status</div>
                <div style='font-size:1.3rem;font-weight:700'>⏳ Running</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class='metric-box'>
                <div style='font-size:0.8rem;opacity:0.8'>Est. time</div>
                <div style='font-size:1.3rem;font-weight:700'>2–3 min</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("&nbsp;")

        # Live log
        if os.path.exists("outputs/progress.txt"):
            with open("outputs/progress.txt", "r", encoding="utf-8", errors="ignore") as f:
                log = f.read()
            if log.strip():
                with st.expander("📜 Live research log", expanded=True):
                    lines = [l for l in log.split("\n") if l.strip()]
                    for line in lines[-25:]:
                        if "--- Step" in line:
                            st.markdown(f"**{line}**")
                        elif "Thought:" in line:
                            st.markdown(f"💭 `{line}`")
                        elif "Action:" in line:
                            st.markdown(f"⚡ `{line}`")
                        elif "Obs:" in line:
                            st.markdown(f"👁️ `{line[:120]}`")
                        elif "write_section" in line:
                            st.markdown(f"✅ **{line}**")
                        elif "memory" in line.lower():
                            st.markdown(f"🧠 `{line}`")
                        elif "runner" in line.lower():
                            st.markdown(f"🏁 **{line}**")

        time.sleep(4)
        st.rerun()

    else:
        # Finished
        st.session_state.process = None
        if os.path.exists(result_path):
            st.session_state.memo_loaded = True
            st.rerun()
        else:
            st.error("Agent finished but no results were saved.")
            if os.path.exists("outputs/progress.txt"):
                with open("outputs/progress.txt", "r", encoding="utf-8", errors="ignore") as f:
                    st.code(f.read())

# ── Display memo ──────────────────────────────────────────────────────────────
if st.session_state.memo_loaded:
    result_path = "outputs/latest_result.json"
    with open(result_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    sections = data.get("memo_sections", {})
    company_name = data.get("company", "")
    step_count = data.get("step_count", 0)

    # Summary bar
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class='metric-box'>
            <div style='font-size:0.8rem;opacity:0.8'>Company</div>
            <div style='font-size:1.3rem;font-weight:700'>{company_name}</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class='metric-box'>
            <div style='font-size:0.8rem;opacity:0.8'>Research Steps</div>
            <div style='font-size:1.3rem;font-weight:700'>{step_count}</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class='metric-box'>
            <div style='font-size:0.8rem;opacity:0.8'>Sections</div>
            <div style='font-size:1.3rem;font-weight:700'>{len(sections)} / 5</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("&nbsp;")
    st.markdown(f"## 📋 Research Memo: {company_name}")
    st.divider()

    # Display sections in fixed order
    for key in SECTION_ORDER:
        if key in sections:
            icon = SECTION_ICONS[key]
            label = SECTION_LABELS[key]
            content = sections[key]
            st.markdown(f"""
            <div class='section-card'>
                <div class='section-title'>{icon} {label}</div>
                <div class='section-content'>{content}</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # Download
    memo_text = f"# Financial Research Memo: {company_name}\n\n"
    memo_text += f"*Research steps: {step_count} | Sections: {len(sections)}/5*\n\n---\n\n"
    for key in SECTION_ORDER:
        if key in sections:
            memo_text += f"## {SECTION_LABELS[key]}\n\n{sections[key]}\n\n"

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="⬇️  Download Memo (.md)",
            data=memo_text,
            file_name=f"{company_name}_research_memo.md",
            mime="text/markdown",
            use_container_width=True
        )
    with col2:
        if st.button("🔁  Research Another Company", use_container_width=True):
            st.session_state.memo_loaded = False
            st.session_state.company = None
            st.rerun()