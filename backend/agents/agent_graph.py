from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.planner_agent import PlannerAgent
from agents.sql_writer import SQLWriter
from agents.sql_critic import SQLCritic
from agents.executor import Executor

# Initialize agents with enhanced configurations
planner = PlannerAgent()
writer = SQLWriter()
critic = SQLCritic()
executor = Executor(max_retries=3, timeout_seconds=30)

def should_retry(state: AgentState):
    """Determine if the workflow should retry based on errors."""
    if state.get("critic_error") or state.get("error"):
        if state["retry_count"] < 3:
            state["retry_count"] += 1
            # Add retry reason to thought process
            if state.get("critic_error"):
                state["thought_process"].append(f"Retry {state['retry_count']}: SQL Critic found issues - {state['critic_error']}")
            elif state.get("error"):
                state["thought_process"].append(f"Retry {state['retry_count']}: Execution failed - {state['error']}")
            return "retry"
    return "continue"

def should_continue(state: AgentState):
    """Determine if execution should continue or end."""
    if state.get("error"):
        # If we have an execution error, we're done
        return "end"
    elif state.get("result") is not None:
        # If we have results, we're done
        return "end"
    else:
        # If no error but no results, something went wrong
        return "end"

workflow = StateGraph(AgentState)

# Add nodes with enhanced error handling
workflow.add_node("planner", planner.plan)
workflow.add_node("writer", writer.write_sql)
workflow.add_node("critic", critic.validate)
workflow.add_node("executor", executor.execute)

# Build graph with enhanced flow
workflow.set_entry_point("planner")

# Planner -> Writer (always)
workflow.add_edge("planner", "writer")

# Writer -> Critic (always)
workflow.add_edge("writer", "critic")

# Critic -> Conditional retry or execution
workflow.add_conditional_edges(
    "critic",
    should_retry,
    {
        "retry": "writer",
        "continue": "executor"
    }
)

# Executor -> Conditional end
workflow.add_conditional_edges(
    "executor",
    should_continue,
    {
        "end": END
    }
)

# Compile with enhanced configuration
app_graph = workflow.compile()
