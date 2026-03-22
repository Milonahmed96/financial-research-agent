# 📊 Financial Research Agent

> Autonomous investment research powered by **Claude AI** · **LangGraph** · **Tavily**

[![Live Demo](https://img.shields.io/badge/🚀%20Live%20Demo-Hugging%20Face%20Spaces-blue?style=for-the-badge)](https://huggingface.co/spaces/Milon96/financial-research-agent)
[![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic%20AI-green?style=for-the-badge)](https://github.com/langchain-ai/langgraph)
[![Claude](https://img.shields.io/badge/Claude-Sonnet%204-orange?style=for-the-badge)](https://anthropic.com)

---

## What It Does

Enter any company name. The agent **autonomously**:

1. Plans a targeted research strategy
2. Searches the web across multiple queries
3. Reads and extracts information from relevant pages
4. Writes each section of the report as soon as it has sufficient data
5. Delivers a downloadable **PDF investment research report**

No manual effort. No supervision. 2–3 minutes end to end.

---

## Live Demo

🚀 **[Try it now on Hugging Face Spaces](https://huggingface.co/spaces/Milon96/financial-research-agent)**

---

## Report Structure

Every report covers five sections in a fixed professional order:

| # | Section | What It Contains |
|---|---|---|
| 1 | 🏢 **Company Overview** | Business model, divisions, size, market position |
| 2 | 💰 **Financial Performance** | Revenue, profit, key ratios, growth trajectory |
| 3 | 📰 **Recent Developments** | News, acquisitions, strategic announcements |
| 4 | 🤖 **Technology & AI Strategy** | AI investments, digital transformation |
| 5 | 📈 **Analyst Sentiment** | Consensus ratings, price targets, market outlook |

---

## Architecture

The agent uses the **ReAct pattern** (Reasoning + Acting) — it reasons before every action, executes a tool, observes the result, and adapts its plan accordingly.

```
Thought: I need to find HSBC's latest earnings results.
Action:  web_search("HSBC Q4 2024 earnings revenue profit")
Observation: [search results returned — revenue $65.9bn found]

Thought: I have revenue. Now I need analyst sentiment.
Action:  web_search("HSBC analyst rating outlook 2026")
Observation: [results — consensus Buy rating, 14 analysts]

Thought: I have enough data. Write the financials section.
Action:  write_section("financials", "HSBC reported revenue of $65.9bn...")
Observation: Section 'financials' written successfully.

Thought: 4 sections done. Research AI initiatives next.
...
```

### System Design

```
User Input (company name)
        │
        ▼
   LangGraph State Machine
        │
   ┌────▼────┐     ┌──────────────┐     ┌───────────────┐
   │  Plan   │────▶│  ReAct Loop  │────▶│  Write Memo   │
   │Research │     │ (up to 20    │     │  Sections     │
   └─────────┘     │  steps)      │     └───────┬───────┘
                   │              │             │
                   │  ┌─────────┐ │             ▼
                   │  │ Memory  │ │      PDF Report
                   │  │Summary  │ │      Download
                   │  │(every 8 │ │
                   │  │ steps)  │ │
                   │  └─────────┘ │
                   └──────────────┘
```

### Tech Stack

| Component | Technology | Purpose |
|---|---|---|
| Agent Orchestration | LangGraph | Stateful graph with conditional routing |
| LLM Backbone | Claude Sonnet (Anthropic API) | Reasoning and writing |
| Web Search | Tavily API | Real-time web search for agents |
| Web Fetching | requests + BeautifulSoup | Full page content extraction |
| Frontend | Gradio | Public web interface |
| Deployment | Hugging Face Spaces (Docker) | Live public deployment |
| PDF Generation | ReportLab | Professional downloadable reports |

---

## Repository Structure

```
financial-research-agent/
├── agent/
│   ├── __init__.py
│   ├── graph.py          # LangGraph state machine — the agent brain
│   ├── nodes.py          # ReAct node, memory summarisation, finish guard
│   ├── tools.py          # web_search, web_fetch, write_section
│   └── prompts.py        # System prompt + ReAct instructions for Claude
├── tests/
│   ├── test_tools.py     # Unit tests for all three tools
│   └── test_graph.py     # Integration tests for graph nodes
├── evaluation/
│   └── eval_harness.py   # Task completion rate measurement
├── outputs/              # Generated reports (git-ignored)
├── app_gradio.py         # Gradio frontend (Hugging Face Spaces)
├── app.py                # Streamlit frontend (local use)
├── run_agent.py          # Agent runner called by Streamlit subprocess
├── Dockerfile            # Docker config for HF Spaces deployment
├── FAILURE_ANALYSIS.md   # Documented failure modes and mitigations
├── requirements.txt
└── README.md
```

---

## Running Locally

### Prerequisites
- Python 3.11+
- Anthropic API key ([console.anthropic.com](https://console.anthropic.com))
- Tavily API key ([tavily.com](https://tavily.com)) — free tier available

### Setup

```bash
git clone https://github.com/Milonahmed96/financial-research-agent
cd financial-research-agent

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=your_anthropic_key_here
TAVILY_API_KEY=your_tavily_key_here
```

### Run the Streamlit App

```bash
streamlit run app.py
```

### Run the Agent Directly

```bash
python run_agent.py HSBC
```

### Run Tests

```bash
pytest tests/ -v
```

---

## Key Engineering Decisions

**Why LangGraph over plain LangChain?**
LangGraph provides a stateful graph where each node has access to the full agent state — memo sections written, messages history, step count, error log. This makes conditional routing, memory summarisation, and the finish guard straightforward to implement.

**Why ReAct over direct tool calling?**
Explicit Thought steps before every Action dramatically improves reliability. Without reasoning steps, the agent acts impulsively — fetching PDFs, retrying blocked sites, finishing before all sections are written.

**Why subprocess for the Streamlit frontend?**
Streamlit blocks on long-running calls. Running the agent as a subprocess with stdout redirected to a file allows the UI to poll for progress without freezing.

**Why memory summarisation every 8 steps?**
Each ReAct step appends two messages to history. Without compression, a 20-step run produces 40+ messages — the agent loses its research plan. Summarising every 8 steps keeps context manageable while preserving key findings.

---

## Failure Analysis

Five failure modes were identified, documented, and mitigated during development:

| # | Failure Mode | Frequency | Status |
|---|---|---|---|
| 1 | **Infinite loop** — agent repeats identical searches | Common | ✅ Mitigated — 20-step hard limit |
| 2 | **Hallucinated citations** — facts not from retrieved sources | Occasional | ⚠️ Partial — no automated verification |
| 3 | **Context overflow** — agent loses plan on long runs | Common | ✅ Mitigated — memory summarisation every 8 steps |
| 4 | **Tool misuse** — write_section called without content | Occasional | ✅ Mitigated — instructive error messages + format examples |
| 5 | **Premature termination** — finish called before all sections written | Common early | ✅ Mitigated — finish guard checks actual memo_sections dict |

See [FAILURE_ANALYSIS.md](FAILURE_ANALYSIS.md) for full root cause analysis, observed examples, and production requirements.

---

## Portfolio Context

This is **Project 6** of a 7-project AI Engineer preparation path targeting AI Engineer roles in London (£48K–£62K) from August 2026.

| Project | Description | Key Result |
|---|---|---|
| P1 — Rossmann Reborn | Production Python package from notebook | LightGBM R²=0.8679, 59 unit tests |
| P2 — Beat Your Model | PyTorch LSTM from scratch | RMSPE=0.2871, beats Keras baseline |
| P3 — Predictions to Intervals | Calibrated uncertainty quantification | 90% conformal coverage, 3 methods |
| P4 — Document Search RAG | End-to-end RAG system with evaluation | 96% accuracy, live Streamlit app |
| P5 — Domain Fine-tuning | QLoRA fine-tuned LLM on medical triage | 64% accuracy, 100% EMERGENCY recall |
| **P6 — Financial Research Agent** | **Multi-step autonomous research agent** | **Live HF Spaces deployment** |
| P7 — Production System | Full MLOps: Docker, CI/CD, AWS | Coming soon |

---

## Disclaimer

This tool is intended for **informational and research purposes only**. Reports are generated autonomously by an AI system and may contain inaccuracies. This does not constitute financial advice. Always verify information from primary sources before making any financial decisions.

---

*Built by **Milon Ahmed** · MSc Data Science, University of Hertfordshire · March 2026*  
*Prepared with Claude · [claude.ai](https://claude.ai)*
