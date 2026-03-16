from typing import List, Dict, Any, Optional
import json
import hashlib
from datetime import datetime, timedelta

class SessionMemory:
    def __init__(self, max_history_length: int = 15, context_window_hours: int = 24):
        self.sessions: Dict[str, List[Dict[str, Any]]] = {}
        self.max_history_length = max_history_length
        self.context_window_hours = context_window_hours
        self.session_metadata: Dict[str, Dict[str, Any]] = {}

    def update_memory(self, session_id: str, query_data: Dict[str, Any]):
        """Update session memory with new query data."""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
            self._init_session_metadata(session_id)
        
        # Add metadata to query data
        enriched_data = self._enrich_query_data(query_data, session_id)
        self.sessions[session_id].append(enriched_data)
        
        # Update session metadata
        self._update_session_metadata(session_id, enriched_data)
        
        # Clean up old entries and maintain size limits
        self._cleanup_session(session_id)

    def get_history(self, session_id: str, include_context: bool = True) -> List[Dict[str, Any]]:
        """Get conversation history for a session."""
        if session_id not in self.sessions:
            return []
        
        # Check if session has expired
        if self._is_session_expired(session_id):
            self._clear_expired_session(session_id)
            return []
        
        history = self.sessions[session_id]
        
        if include_context and len(history) > 1:
            # Return summarized context for long conversations
            if len(history) > 8:
                return self._get_summarized_context(history)
            else:
                return history[-8:]  # Return last 8 interactions
        else:
            return history

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of the session for context."""
        if session_id not in self.session_metadata:
            return {}
        
        metadata = self.session_metadata[session_id]
        return {
            "session_id": session_id,
            "total_queries": metadata["total_queries"],
            "last_activity": metadata["last_activity"],
            "common_topics": metadata["common_topics"],
            "query_types": metadata["query_types"],
            "session_duration": str(datetime.now() - metadata["session_start"])
        }

    def clear_session(self, session_id: str):
        """Clear all memory for a specific session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
        if session_id in self.session_metadata:
            del self.session_metadata[session_id]

    def get_all_sessions(self) -> List[str]:
        """Get all active session IDs."""
        return list(self.sessions.keys())

    def _init_session_metadata(self, session_id: str):
        """Initialize metadata for a new session."""
        self.session_metadata[session_id] = {
            "session_start": datetime.now(),
            "last_activity": datetime.now(),
            "total_queries": 0,
            "common_topics": [],
            "query_types": {},
            "session_active": True
        }

    def _enrich_query_data(self, query_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Add metadata to query data."""
        enriched = query_data.copy()
        enriched.update({
            "timestamp": datetime.now().isoformat(),
            "query_id": self._generate_query_id(query_data.get("question", "")),
            "session_id": session_id
        })
        return enriched

    def _update_session_metadata(self, session_id: str, query_data: Dict[str, Any]):
        """Update session metadata based on new query."""
        metadata = self.session_metadata[session_id]
        metadata["last_activity"] = datetime.now()
        metadata["total_queries"] += 1
        
        # Track query types
        question = query_data.get("question", "").lower()
        if "sales" in question or "revenue" in question:
            metadata["query_types"]["sales"] = metadata["query_types"].get("sales", 0) + 1
        elif "inventory" in question or "stock" in question:
            metadata["query_types"]["inventory"] = metadata["query_types"].get("inventory", 0) + 1
        elif "performance" in question or "speed" in question:
            metadata["query_types"]["performance"] = metadata["query_types"].get("performance", 0) + 1
        elif "trend" in question or "time" in question or "date" in question:
            metadata["query_types"]["trends"] = metadata["query_types"].get("trends", 0) + 1
        
        # Update common topics
        topics = self._extract_topics(question)
        metadata["common_topics"].extend(topics)
        # Keep only unique topics
        metadata["common_topics"] = list(set(metadata["common_topics"]))

    def _cleanup_session(self, session_id: str):
        """Clean up session data to maintain size limits."""
        session_data = self.sessions[session_id]
        
        # Remove entries older than context window
        cutoff_time = datetime.now() - timedelta(hours=self.context_window_hours)
        self.sessions[session_id] = [
            entry for entry in session_data 
            if datetime.fromisoformat(entry["timestamp"]) > cutoff_time
        ]
        
        # Limit history length
        if len(self.sessions[session_id]) > self.max_history_length:
            self.sessions[session_id] = self.sessions[session_id][-self.max_history_length:]

    def _is_session_expired(self, session_id: str) -> bool:
        """Check if session has expired based on inactivity."""
        if session_id not in self.session_metadata:
            return True
        
        last_activity = self.session_metadata[session_id]["last_activity"]
        expiration_time = datetime.now() - timedelta(hours=self.context_window_hours)
        return last_activity < expiration_time

    def _clear_expired_session(self, session_id: str):
        """Clear an expired session."""
        self.clear_session(session_id)

    def _get_summarized_context(self, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get summarized context for long conversations."""
        if len(history) <= 8:
            return history
        
        # Keep first 2 and last 6 interactions, summarize the middle
        first_two = history[:2]
        last_six = history[-6:]
        
        # Create a summary of the middle section
        middle_summary = {
            "type": "summary",
            "content": f"Conversation continued with {len(history) - 8} additional interactions",
            "timestamp": datetime.now().isoformat(),
            "query_id": "summary",
            "session_id": history[0].get("session_id", "")
        }
        
        return first_two + [middle_summary] + last_six

    def _generate_query_id(self, question: str) -> str:
        """Generate a unique ID for a query."""
        return hashlib.md5(question.encode()).hexdigest()[:8]

    def _extract_topics(self, question: str) -> List[str]:
        """Extract topics from a question."""
        topics = []
        question_lower = question.lower()
        
        topic_keywords = {
            "sales": ["sales", "revenue", "income", "profit"],
            "inventory": ["inventory", "stock", "available", "count"],
            "performance": ["performance", "speed", "fast", "quick"],
            "trends": ["trend", "time", "date", "when", "over time"],
            "comparison": ["compare", "vs", "versus", "difference"],
            "details": ["details", "information", "about", "describe"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                topics.append(topic)
        
        return topics

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about memory usage."""
        return {
            "active_sessions": len(self.sessions),
            "total_queries": sum(len(session) for session in self.sessions.values()),
            "max_history_length": self.max_history_length,
            "context_window_hours": self.context_window_hours,
            "session_metadata_count": len(self.session_metadata)
        }

# Create global instance
memory_manager = SessionMemory()
