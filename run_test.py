from agent.graph import agent_graph

# Fresh state — no bleed from previous runs
state = {
    "company": "Barclays",  # switching company to force fresh research
    "messages": [],
    "memo_sections": {},
    "step_count": 0,
    "finished": False,
    "awaiting_approval": False,
    "error_log": [],
}

result = agent_graph.invoke(state)

print("\n=== FINAL STATE ===")
print(f"Steps:    {result['step_count']}")
print(f"Sections: {list(result['memo_sections'].keys())}")
for name, content in result['memo_sections'].items():
    print(f"\n[{name}] — {len(content)} chars")
    print(content[:200])