from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.planner_agent import PlannerAgent
from agents.sql_writer import SQLWriter
from agents.sql_critic import SQLCritic
from agents.executor import Executor

# Initialize agents
planner = PlannerAgent()
writer = SQLWriter()
critic = SQLCritic()
executor = Executor()

def should_retry(state: AgentState):
    if state.get("critic_error") or state.get("error"):
        if state["retry_count"] < 3:
            state["retry_count"] += 1
            return "retry"
    return "continue"

workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("planner", planner.plan)
workflow.add_node("writer", writer.write_sql)
workflow.add_node("critic", critic.validate)
workflow.add_node("executor", executor.execute)

# Build graph
workflow.set_entry_point("planner")
workflow.add_edge("planner", "writer")
workflow.add_edge("writer", "critic")

workflow.add_conditional_edges(
    "critic",
    should_retry,
    {
        "retry": "writer",
        "continue": "executor"
    }
)

workflow.add_edge("executor", END)

# Compile
app_graph = workflow.compile()
