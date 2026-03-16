from typing import TypedDict

class AgentState(TypedDict):
    id: str
    name: str
    status: str
    last_active: str