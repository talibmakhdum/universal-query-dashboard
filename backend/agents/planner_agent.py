import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from agents.state import AgentState
from dotenv import load_dotenv

load_dotenv()

class PlannerAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")
        
        # Load metadata
        meta_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'metadata', 'metadata.json')
        with open(meta_path, 'r') as f:
            self.metadata = json.load(f)

    def plan(self, state: AgentState) -> AgentState:
        state["thought_process"].append("Planner: Analyzing your question and selecting relevant tables...")
        
        prompt = f"""
        You are the Planner for an Agentic SQL system.
        Context:
        - Tables available: {state.get('table_name', 'Not specified')}
        - Business Rules: {self.metadata['business_rules']}
        - User Question: {state['question']}
        
        Your job:
        1. Confirm if the question can be answered with the available data.
        2. Create a step-by-step plan for the SQL Writer.
        
        Respond only with the plan string.
        """
        
        response = self.llm.invoke([
            SystemMessage(content="You are a senior data architect planning a query."),
            HumanMessage(content=prompt)
        ])
        
        state["planner_thought"] = response.content
        return state
