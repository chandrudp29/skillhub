---
name: agent-builder
description: Build production-ready LLM agents with LangGraph, tool use, memory, streaming, and error handling. Use when designing or implementing an AI agent, multi-agent system, or agentic workflow.
version: 1.0.0
agents: [claude, cursor, codex, gemini]
tags: [agent, langgraph, llm, tools, memory, streaming, multi-agent]
---

# Agent Builder

A structured approach to building LLM agents that work in production — not just demos.

## When to Use

- "Build an agent that can X"
- "Design a multi-agent system for Y"
- "My agent keeps failing / looping / hallucinating tools"
- Before building any agentic workflow

## The Production Agent Checklist

Before writing code, answer these:
1. **What does the agent need to DO?** (specific tasks, not "be helpful")
2. **What TOOLS does it need?** (web search, code execution, DB query, API calls)
3. **What should it STOP doing?** (scope boundaries)
4. **How does it FAIL gracefully?** (tool errors, context limits, bad outputs)
5. **How is it EVALUATED?** (what does success look like, measurably?)

## Architecture Patterns

### Single Agent with Tools (start here)
```python
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic

model = ChatAnthropic(model="claude-sonnet-4-6")
tools = [web_search, code_executor, db_query]

agent = create_react_agent(model, tools)
result = agent.invoke({"messages": [("user", "Research X and summarize")]})
```

Use when: single task type, clear tool set, < 10 tools.

### Stateful Agent with Memory (LangGraph)
```python
from langgraph.graph import StateGraph, MessagesState
from langgraph.checkpoint.memory import MemorySaver

def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": [response]}

def call_tools(state: MessagesState):
    # execute tool calls from last message
    ...

graph = StateGraph(MessagesState)
graph.add_node("agent", call_model)
graph.add_node("tools", call_tools)
graph.add_edge("tools", "agent")
graph.add_conditional_edges("agent", should_continue)

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)

# Run with thread_id for persistent memory across calls
config = {"configurable": {"thread_id": "user-123"}}
app.invoke({"messages": [("user", "Continue from last time...")]}, config)
```

Use when: multi-turn conversations, stateful workflows, need to pause/resume.

### Multi-Agent (Supervisor Pattern)
```python
from langgraph.graph import StateGraph

def supervisor(state):
    # decide which specialist agent to call next
    decision = model.invoke(SUPERVISOR_PROMPT + str(state["messages"]))
    return {"next": decision.content}

def researcher(state): ...
def coder(state): ...
def reviewer(state): ...

graph = StateGraph(OverallState)
graph.add_node("supervisor", supervisor)
graph.add_node("researcher", researcher)
graph.add_node("coder", coder)
graph.add_node("reviewer", reviewer)

# Supervisor routes to specialists
graph.add_conditional_edges("supervisor", lambda s: s["next"], {
    "researcher": "researcher",
    "coder": "coder",
    "reviewer": "reviewer",
    "FINISH": END,
})
```

Use when: tasks require different expertise, parallelism is valuable, one agent can't handle everything.

## Tool Design

A good tool has:
- **Clear name**: `search_web`, not `tool1`
- **Precise description**: what it does, what it returns, when to use it vs others
- **Strong input validation**: reject bad inputs before calling external APIs
- **Structured output**: return dicts, not raw strings
- **Error handling**: return error info instead of raising exceptions (agents can retry)

```python
from langchain_core.tools import tool
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    query: str = Field(description="Search query. Be specific — include key terms.")
    max_results: int = Field(default=5, description="Number of results (1-10)")

@tool(args_schema=SearchInput)
def search_web(query: str, max_results: int = 5) -> dict:
    """Search the web for current information. Use for recent events, 
    documentation, and facts not in training data. Returns title, URL, snippet."""
    try:
        results = _do_search(query, max_results)
        return {"results": results, "count": len(results)}
    except Exception as e:
        return {"error": str(e), "results": []}  # agent can handle this
```

## Streaming

Always stream in production — users abandon non-streaming agents:

```python
async for event in app.astream_events(
    {"messages": [("user", message)]},
    config=config,
    version="v2",
):
    kind = event["event"]
    if kind == "on_chat_model_stream":
        chunk = event["data"]["chunk"].content
        if chunk:
            print(chunk, end="", flush=True)
    elif kind == "on_tool_start":
        print(f"\n[Using tool: {event['name']}...]")
```

## Production Hardening

**Prevent infinite loops:**
```python
graph = graph.compile(
    checkpointer=checkpointer,
    interrupt_before=["tools"],  # human-in-the-loop for tool calls
)
# Or set recursion limit
config = {"recursion_limit": 25}
```

**Cost control:**
```python
from langchain_core.callbacks import BaseCallbackHandler

class CostTracker(BaseCallbackHandler):
    def on_llm_end(self, response, **kwargs):
        usage = response.llm_output.get("usage", {})
        total_tokens = usage.get("total_tokens", 0)
        if total_tokens > 50_000:
            raise Exception("Token budget exceeded")
```

**Observability:**
```python
from langsmith import Client
# Set LANGCHAIN_TRACING_V2=true, LANGCHAIN_API_KEY in env
# Every agent run is automatically traced
```

## Common Agent Failures

| Failure | Cause | Fix |
|---|---|---|
| Infinite tool loop | Agent can't recognize task is done | Add explicit "task complete" tool or check |
| Wrong tool chosen | Tool descriptions overlap or are vague | Rewrite tool descriptions, add "use X not Y when..." |
| Context overflow | Pasting full docs into every call | RAG retrieval or summarization before agent call |
| Hallucinated tool args | Model fills in missing args | Validate inputs strictly, return helpful errors |
| Non-deterministic behavior | No temperature control | Set temperature=0 for tool-calling steps |

## Evaluation Before Shipping

Don't ship an agent you haven't evaluated. Minimum bar:

```python
test_cases = [
    {"input": "Research topic X", "expected_tool": "search_web"},
    {"input": "Write code for Y", "expected_tool": "code_executor"},
    {"input": "harmful request", "expected_behavior": "refusal"},
]
for case in test_cases:
    result = agent.invoke({"messages": [("user", case["input"])]})
    # assert expected behavior
```
