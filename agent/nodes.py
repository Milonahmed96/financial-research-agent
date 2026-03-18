import os
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
from agent.tools import web_search, web_fetch, write_section
from agent.prompts import SYSTEM_PROMPT

load_dotenv()

# Initialise Claude once at module level
_llm = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    max_tokens=1024,
)


def parse_react_response(response: str) -> tuple[str, str, str]:
    """
    Parse Claude's ReAct response into (thought, action, action_input).
    Returns empty strings if parsing fails.
    """
    thought = ""
    action = ""
    action_input = ""

    for line in response.strip().split("\n"):
        if line.startswith("Thought:"):
            thought = line[len("Thought:"):].strip()
        elif line.startswith("Action:"):
            action = line[len("Action:"):].strip().lower()
        elif line.startswith("Action Input:"):
            action_input = line[len("Action Input:"):].strip()

    return thought, action, action_input


def execute_action(action: str, action_input: str, state: dict) -> str:
    """
    Execute the action Claude decided on and return the observation.
    """
    if action == "web_search":
        results = web_search(action_input)
        if not results:
            return "No results found for that query."
        observation = ""
        for i, r in enumerate(results[:3], 1):
            observation += f"{i}. {r['title']}\n   URL: {r['url']}\n   {r['content'][:200]}\n\n"
        return observation.strip()

    elif action == "web_fetch":
        return web_fetch(action_input)

    elif action == "write_section":
        if "|" not in action_input:
            return "[write_section error] Input must be: section_name|content"
        name, content = action_input.split("|", 1)
        write_section(state["memo_sections"], name.strip(), content.strip())
        return f"Section '{name.strip()}' written successfully."

    elif action == "finish":
        return "FINISH"

    else:
        return f"[error] Unknown action: '{action}'. Use web_search, web_fetch, write_section, or finish."


def run_one_react_step(state: dict) -> dict:
    """
    Run one full ReAct cycle:
    1. Build messages from history
    2. Call Claude
    3. Parse response
    4. Execute action
    5. Append observation to messages
    6. Return updated state
    """
    company = state["company"]
    messages = state["messages"]

    # First step — add the system prompt and initial user message
    if len(messages) == 0:
        messages = [
            {"role": "user", "content": SYSTEM_PROMPT.format(company=company)}
        ]

    # Call Claude
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    lc_messages = []
    for m in messages:
        if m["role"] == "user":
            lc_messages.append(HumanMessage(content=m["content"]))
        elif m["role"] == "assistant":
            lc_messages.append(AIMessage(content=m["content"]))

    response = _llm.invoke(lc_messages)
    response_text = response.content

    # Parse
    thought, action, action_input = parse_react_response(response_text)

    # Print for debugging
    print(f"\n--- Step {state['step_count'] + 1} ---")
    print(f"Thought: {thought}")
    print(f"Action:  {action}")
    print(f"Input:   {action_input}")

    # Execute
    observation = execute_action(action, action_input, state)
    print(f"Obs:     {observation[:200]}")

    # Update messages
    messages.append({"role": "assistant", "content": response_text})
    messages.append({"role": "user", "content": f"Observation: {observation}"})

    # Update state
    state["messages"] = messages
    state["step_count"] = state["step_count"] + 1

    if observation == "FINISH":
        state["finished"] = True

    return state