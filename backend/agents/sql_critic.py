from agents.state import AgentState

class SQLCritic:
    def validate(self, state: AgentState) -> AgentState:
        state["thought_process"].append("SQL Critic: Validating query for safety and correctness...")
        
        sql = state["sql_query"].upper()
        forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE", "ALTER"]
        
        for word in forbidden:
            if word in sql:
                state["critic_error"] = f"Security Violation: '{word}' is not allowed."
                state["thought_process"].append(f"Critic: {state['critic_error']}")
                return state
        
        if not sql.strip().startswith("SELECT"):
             state["critic_error"] = "Invalid Query: Must be a SELECT statement."
             state["thought_process"].append(f"Critic: {state['critic_error']}")
             return state

        state["critic_error"] = None
        return state
