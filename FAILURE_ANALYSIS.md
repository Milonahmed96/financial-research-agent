\# Failure Analysis — Financial Research Agent



\## Overview

During development and testing of the Financial Research Agent, five distinct failure modes

were observed and documented. Each is described below with its root cause, how it manifests,

and the mitigation implemented.



\---



\## Failure Mode 1 — Infinite Loop



\*\*What happens:\*\*

The agent calls `web\_search` repeatedly with near-identical queries, making no progress

toward writing sections.



\*\*Example observed:\*\*

```

Action: web\_search — "HSBC 2024 financial results"

Action: web\_search — "HSBC 2024 financial results revenue"

Action: web\_search — "HSBC financial results 2024 revenue profit"

```



\*\*Root cause:\*\*

Claude interprets each new search as progress even when results are repetitive.

Without a hard step limit, the agent loops indefinitely.



\*\*Mitigation implemented:\*\*

\- `MAX\_STEPS = 20` hard limit in `agent/graph.py`

\- Early termination when all 5 sections are written

\- Guard in `run\_agent.py` that breaks the loop on completion



\*\*Remaining risk:\*\*

Step limit forces approval with incomplete sections if research takes too long.



\---



\## Failure Mode 2 — Hallucinated Citations



\*\*What happens:\*\*

The agent writes a section containing specific figures or facts not found in any

retrieved search result — drawn from Claude's training data instead.



\*\*Example observed:\*\*

Agent wrote "Barclays reported revenue of £24.3 billion" when search results

only mentioned profit figures. The revenue number came from Claude's training

data, not from the retrieved content.



\*\*Root cause:\*\*

When retrieved context is sparse or truncated, Claude fills gaps using training

knowledge. The agent has no mechanism to verify that every claim in a section

came from a retrieved source.



\*\*Mitigation implemented:\*\*

\- Prompt instructs agent to use retrieved data only

\- `web\_fetch` truncation kept at 2,000 chars to prevent context overflow



\*\*Remaining risk:\*\*

No automated citation verification. A production system would require a

verification step that checks each claim against retrieved URLs.



\---



\## Failure Mode 3 — Context Overflow



\*\*What happens:\*\*

After many research steps, the message history grows too large. Claude loses

track of its research plan, forgets which sections it has written, and begins

rewriting already-completed sections.



\*\*Example observed:\*\*

At step 16+, agent rewrote `company\_overview` and `financials` sections it had

already written at steps 6 and 8, wasting 4 steps and never reaching

`ai\_initiatives` or `analyst\_sentiment`.



\*\*Root cause:\*\*

Each step appends two messages (assistant + observation) to history. After 15+

steps the context becomes unwieldy and Claude loses coherence.



\*\*Mitigation implemented:\*\*

\- `summarise\_memory()` fires every 8 steps, compressing history into a summary

\- Summary explicitly lists sections already written

\- Re-injects system prompt after each summary to restore format instructions



\*\*Remaining risk:\*\*

Summarisation itself can lose details. A production system would use a

persistent external memory store instead of in-context summarisation.



\---



\## Failure Mode 4 — Tool Misuse



\*\*What happens:\*\*

The agent calls `write\_section` without the required pipe separator between

section name and content, causing the tool to return an error and the step

to be wasted.



\*\*Example observed:\*\*

```

Action: write\_section

Action Input: analyst\_sentiment

```

Instead of:

```

Action: write\_section

Action Input: analyst\_sentiment|Analysts maintain a Buy consensus...

```



\*\*Root cause:\*\*

After memory summarisation, the system prompt is re-injected but Claude

occasionally reverts to writing just the section name without content,

particularly when it has been blocked from finishing multiple times.



\*\*Mitigation implemented:\*\*

\- Prompt includes explicit CORRECT/WRONG examples of pipe format

\- Error message now instructs Claude to retry immediately with correct format

\- Guard blocks `finish` when sections are missing, forcing continued writing



\*\*Remaining risk:\*\*

Claude occasionally misformats on the first attempt then self-corrects.

A production system would parse more flexibly using regex rather than

requiring exact pipe formatting.



\---



\## Failure Mode 5 — Premature Termination



\*\*What happens:\*\*

The agent calls `finish` before all 5 required sections are written,

claiming completion when sections are missing.



\*\*Example observed:\*\*

Agent called `finish` at step 4 claiming all 5 sections were complete

when `memo\_sections` was empty — hallucinating that it had written content

it had not actually written.



\*\*Root cause:\*\*

Claude's training leads it to be helpful and complete tasks. When the

context suggested research had been done (from a previous run's summary),

Claude concluded the task was done even without verifying actual section content.



\*\*Mitigation implemented:\*\*

\- `should\_continue()` guard in `agent/graph.py` checks actual `memo\_sections`

&#x20; dict before allowing finish

\- Missing sections are listed explicitly in the error observation

\- Agent is forced to continue until all 5 keys exist in `memo\_sections`



\*\*Remaining risk:\*\*

Agent can write very short or low-quality sections just to pass the guard.

A production system would enforce minimum content length per section.



\---



\## Summary Table



| # | Failure Mode | Frequency | Severity | Status |

|---|---|---|---|---|

| 1 | Infinite loop | Common | High | Mitigated — step limit |

| 2 | Hallucinated citations | Occasional | Medium | Partial — no auto-verify |

| 3 | Context overflow | Common on long runs | High | Mitigated — summarisation |

| 4 | Tool misuse | Occasional | Low | Mitigated — better error messages |

| 5 | Premature termination | Common early | High | Mitigated — finish guard |



\---



\## What Would Be Required for Production



1\. \*\*Citation verification\*\* — automated check that every claim maps to a retrieved URL

2\. \*\*Flexible tool parsing\*\* — regex-based parsing instead of strict pipe format

3\. \*\*External memory store\*\* — vector database instead of in-context summarisation

4\. \*\*Content quality check\*\* — minimum length and keyword validation per section

5\. \*\*Retry logic\*\* — automatic retry with different search queries on empty results

6\. \*\*Cost monitoring\*\* — track tokens and API cost per research run

7\. \*\*Rate limiting\*\* — queue requests to prevent API quota exhaustion



\---



\*Documented during P6 development · Milon Ahmed · March 2026\*

