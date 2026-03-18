from typing import TypedDict
from langgraph.graph import StateGraph, END
from agent.nodes import run_one_react_step

MAX_STEPS = 20


class AgentState(TypedDict):
    company:            str
    messages:           list
    memo_sections:      dict
    step_count:         int
    finished:           bool
    awaiting_approval:  bool
    error_log:          list


def should_continue(state: AgentState) -> str:
    """
    Decide what to do after each step:
    - If finished flag is set → go to approval checkpoint
    - If step limit reached  → go to approval checkpoint
    - Otherwise              → run another step
    """
    if state["finished"]:
        return "approval"
    if state["step_count"] >= MAX_STEPS:
        print(f"[graph] Step limit {MAX_STEPS} reached — forcing approval")
        return "approval"
    return "continue"


def approval_checkpoint(state: AgentState) -> AgentState:
    """
    Show the user what the agent found and ask for approval.
    """
    print("\n" + "="*60)
    print("APPROVAL CHECKPOINT")
    print("="*60)
    print(f"Company researched: {state['company']}")
    print(f"Steps taken: {state['step_count']}")
    print(f"Sections written: {list(state['memo_sections'].keys())}")
    print("\nSections preview:")
    for name, content in state['memo_sections'].items():
        print(f"\n  [{name}]")
        print(f"  {content[:150]}...")
    print("\n" + "="*60)

    answer = input("Approve and write final memo? (y/n): ").strip().lower()
    if answer == "y":
        state["awaiting_approval"] = False
    else:
        print("[graph] Rejected — running more research steps")
        state["awaiting_approval"] = True
        state["finished"] = False

    return state


def after_approval(state: AgentState) -> str:
    """
    After approval checkpoint:
    - If approved → write memo
    - If rejected → continue research
    """
    if state["awaiting_approval"]:
        return "continue"
    return "write_memo"


def write_final_memo(state: AgentState) -> AgentState:
    """
    Write all memo sections to a markdown file in outputs/.
    """
    import os
    os.makedirs("outputs", exist_ok=True)

    company = state["company"].replace(" ", "_")
    filepath = f"outputs/{company}_research_memo.md"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Financial Research Memo: {state['company']}\n\n")
        f.write(f"*Steps taken: {state['step_count']}*\n\n")
        f.write("---\n\n")
        for section_name, content in state["memo_sections"].items():
            title = section_name.replace("_", " ").title()
            f.write(f"## {title}\n\n")
            f.write(content)
            f.write("\n\n")

    print(f"\n[graph] Memo written to {filepath}")
    state["finished"] = True
    return state


def build_graph():
    """
    Build and compile the LangGraph agent graph.
    """
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("react_step",    run_one_react_step)
    graph.add_node("approval",      approval_checkpoint)
    graph.add_node("write_memo",    write_final_memo)

    # Entry point
    graph.set_entry_point("react_step")

    # After each ReAct step — continue or go to approval
    graph.add_conditional_edges(
        "react_step",
        should_continue,
        {
            "continue":  "react_step",
            "approval":  "approval",
        }
    )

    # After approval — write memo or continue research
    graph.add_conditional_edges(
        "approval",
        after_approval,
        {
            "continue":  "react_step",
            "write_memo": "write_memo",
        }
    )

    # After writing memo — done
    graph.add_edge("write_memo", END)

    return graph.compile()


# Compiled graph — import this in app.py and tests
agent_graph = build_graph()