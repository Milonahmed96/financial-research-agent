# 📊 Financial Research Agent

An autonomous AI agent that researches any company and produces a structured
investment research report — without manual effort.

Built with **Claude AI** (Anthropic) · **LangGraph** · **Tavily** · **Streamlit**

---

## Live Demo

🚀 **[Try it on Hugging Face Spaces](#)** *(link added after deployment)*

---

## What It Does

Enter a company name. The agent autonomously:

1. Plans a research strategy
2. Searches the web across multiple queries
3. Fetches and reads relevant pages
4. Writes each report section as soon as it has sufficient data
5. Produces a downloadable PDF investment research report

All without you supervising a single step.

---

## Report Structure

Every report covers five sections in order:

| Section | What It Contains |
|---|---|
| 🏢 Company Overview | Business model, divisions, size, market position |
| 💰 Financial Performance | Revenue, profit, key ratios, growth trajectory |
| 📰 Recent Developments | News, acquisitions, strategic announcements |
| 🤖 Technology & AI Strategy | AI investments, digital transformation |
| 📈 Analyst Sentiment | Consensus ratings, price targets, outlook |

---

## Architecture

The agent uses the **ReAct pattern** (Reasoning + Acting):
```
Thought: I need to find HSBC's latest earnings results
Action:  web_search("HSBC Q4 2024 earnings revenue profit")
Observation: [search results returned]

Thought: I have revenue numbers. Now I need analyst ratings.
Action:  web_search("HSBC analyst rating outlook 2026")
Observation: [results returned]

Thought: I have enough data. Write the financials section.
Action:  write_section("financials", "HSBC reported revenue of $65.9bn...")
```

### Tech Stack

| Component | Tool |
|---|---|
| Agent orchestration | LangGraph |
| LLM backbone | Claude claude-sonnet-4-20250514 (Anthropic) |
| Web search | Tavily API |
| Web fetching | requests + BeautifulSoup |
| Frontend | Streamlit |
| Deployment | Hugging Face Spaces |

### Repository Structure
```
financial-research-agent/
├── agent/
│   ├── graph.py       # LangGraph state machine
│   ├── nodes.py       # ReAct node, memory summarisation
│   ├── tools.py       # web_search, web_fetch, write_section
│   └── prompts.py     # System prompt + ReAct instructions
├── app.py             # Streamlit frontend
├── run_agent.py       # Agent runner (called by Streamlit subprocess)
├── outputs/           # Generated reports (git-ignored)
├── FAILURE_ANALYSIS.md
└── README.md
```

---

## Running Locally
```bash
git clone https://github.com/Milonahmed96/financial-research-agent
cd financial-research-agent

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt
```

Create a `.env` file:
```
ANTHROPIC_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

Run the app:
```bash
streamlit run app.py
```

---

## Failure Analysis

Five failure modes were identified and documented during development:

| # | Failure Mode | Status |
|---|---|---|
| 1 | Infinite loop — agent repeats identical searches | ✅ Mitigated — step limit |
| 2 | Hallucinated citations — facts not from retrieved sources | ⚠️ Partial — no auto-verify |
| 3 | Context overflow — agent loses plan on long runs | ✅ Mitigated — memory summarisation |
| 4 | Tool misuse — write_section called without content | ✅ Mitigated — better error messages |
| 5 | Premature termination — finish called before all sections written | ✅ Mitigated — finish guard |

See [FAILURE_ANALYSIS.md](FAILURE_ANALYSIS.md) for full root cause analysis and production requirements.

---

## Portfolio Context

This project is **Project 6** of a 7-project AI Engineer preparation path.

| Project | Description |
|---|---|
| P1 — Rossmann Reborn | LightGBM forecasting package, R²=0.8679 |
| P2 — Beat Your Model | PyTorch LSTM, RMSPE=0.2871 |
| P3 — Predictions to Intervals | Conformal prediction, 90% coverage |
| P4 — Document Search RAG | 96% accuracy, live Streamlit app |
| P5 — Domain Fine-tuning | Phi-3-mini medical triage, HF published |
| **P6 — Financial Research Agent** | **This project** |
| P7 — Production System | Docker, CI/CD, AWS, drift monitoring |

---

## Disclaimer

This tool is intended for informational and research purposes only.
Reports are generated autonomously by an AI system and may contain inaccuracies.
This does not constitute financial advice. Always verify from primary sources
before making any financial decisions.

---

*Built by Milon Ahmed · MSc Data Science, University of Hertfordshire · March 2026*
