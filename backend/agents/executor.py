from agents.state import AgentState
from utils.db import DBUtils

class Executor:
    def __init__(self):
        self.db = DBUtils()

    def execute(self, state: AgentState) -> AgentState:
        state["thought_process"].append("Executor: Running query on database...")
        
        try:
            results = self.db.execute_query(state["sql_query"])
            state["result"] = results
            state["error"] = None
            state["thought_process"].append(f"Executor: Successfully retrieved {len(results)} rows.")
        except Exception as e:
            state["error"] = str(e)
            state["thought_process"].append(f"Executor Error: {state['error']}")
            
        return state
