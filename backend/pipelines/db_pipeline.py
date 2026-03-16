from agents.agent_graph import app_graph
from utils.db import DBUtils
from utils.charts import suggest_chart
from memory.session_memory import memory_manager

db = DBUtils()

async def run_db_query(question: str, table_name: str, session_id: str):
    # Get schema
    schema = db.get_table_schema(table_name)
    history = memory_manager.get_history(session_id)
    
    # Initialize state
    initial_state = {
        "question": question,
        "table_name": table_name,
        "schema": schema,
        "history": history,
        "retry_count": 0,
        "thought_process": [],
        "sql_query": None,
        "planner_thought": None,
        "critic_error": None,
        "result": None,
        "error": None
    }
    
    # Run graph
    final_state = app_graph.invoke(initial_state)
    
    # Suggest chart
    chart_type = suggest_chart(final_state.get("result", []))
    
    # Update memory if successful
    if final_state.get("result"):
        memory_manager.update_memory(session_id, {
            "question": question,
            "sql": final_state["sql_query"]
        })
        
    return {
        "success": final_state.get("error") is None,
        "data": final_state.get("result"),
        "sql": final_state["sql_query"],
        "chartType": chart_type,
        "thought_process": final_state["thought_process"],
        "error": final_state.get("error")
    }
