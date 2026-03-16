import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from agents.state import AgentState
from dotenv import load_dotenv

load_dotenv()

class SQLWriter:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        meta_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'metadata', 'metadata.json')
        with open(meta_path, 'r') as f:
            self.metadata = json.load(f)

    def write_sql(self, state: AgentState) -> AgentState:
        state["thought_process"].append("SQL Writer: Generating optimized SQL query...")
        
        history_context = ""
        if state.get("history"):
             history_context = "\nConversation History:\n" + "\n".join([f"User: {h['question']}\nSQL: {h.get('sql', 'N/A')}" for h in state["history"][-2:]])

        prompt = f"""
        Generate a single SQLite-compatible SQL query.
        
        Table: {state['table_name']}
        Schema: {state['schema']}
        Business Rules: {self.metadata['business_rules']}
        Planner's Plan: {state['planner_thought']}
        User Question: {state['question']}
        {history_context}
        
        Rules:
        - Return ONLY the SQL code block. No explanation.
        - Ensure columns match the schema exactly.
        - If the question mentions 'performance', look for 'M' models.
        - Use case-insensitive matching where appropriate using COLLATE NOCASE.
        
        SQL:
        """
        
        response = self.llm.invoke([
            SystemMessage(content="You are an expert SQL generator for SQLite."),
            HumanMessage(content=prompt)
        ])
        
        sql = response.content.replace('```sql', '').replace('```', '').strip()
        state["sql_query"] = sql
        return state
