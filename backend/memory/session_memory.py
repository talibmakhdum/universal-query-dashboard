from typing import List, Dict, Any

class SessionMemory:
    def __init__(self):
        self.sessions: Dict[str, List[Dict[str, Any]]] = {}

    def update_memory(self, session_id: str, query_data: Dict[str, Any]):
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append(query_data)
        
        # Keep last 10 interactions
        if len(self.sessions[session_id]) > 10:
            self.sessions[session_id] = self.sessions[session_id][-10:]

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        return self.sessions.get(session_id, [])

memory_manager = SessionMemory()
