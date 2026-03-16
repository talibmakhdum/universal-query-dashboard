from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    question: str
    table_name: Optional[str]
    schema: Optional[str]
    planner_thought: Optional[str]
    sql_query: Optional[str]
    critic_error: Optional[str]
    result: Optional[List[Dict[str, Any]]]
    error: Optional[str]
    thought_process: List[str]  # List of status messages for the UI
    retry_count: int
    history: List[Dict[str, Any]]
