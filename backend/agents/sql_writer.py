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
        
        # Enhanced context building
        history_context = self._build_history_context(state)
        business_context = self._build_business_context()
        schema_context = self._build_schema_context(state['schema'])
        
        prompt = f"""
        You are an expert SQL architect specializing in SQLite optimization and business rule compliance.
        
        ## CONTEXT
        Table: {state['table_name']}
        {schema_context}
        {business_context}
        {history_context}
        
        ## PLANNER'S STRATEGY
        {state['planner_thought']}
        
        ## USER REQUIREMENT
        Question: {state['question']}
        
        ## CRITICAL REQUIREMENTS
        1. STRICTLY follow the provided schema - no invented column names
        2. Apply all relevant business rules from metadata
        3. Optimize for performance (use indexes, avoid unnecessary operations)
        4. Handle edge cases (NULL values, empty results, data type mismatches)
        5. Use appropriate SQL patterns:
           - Case-insensitive matching with COLLATE NOCASE
           - Proper date/time handling
           - Aggregation best practices
           - Subquery optimization when needed
        
        ## BUSINESS RULES TO ENFORCE
        - Price is always in USD - ensure currency consistency
        - VehicleID is primary key - use for joins when needed
        - Electric vehicles have EngineSize 0.0 - filter accordingly
        - M series models indicate performance - prioritize in relevant queries
        
        ## OUTPUT REQUIREMENTS
        - Return ONLY the SQL query in a single code block
        - No explanations, comments, or additional text
        - Ensure query is syntactically correct and executable
        - Include appropriate error handling patterns where relevant
        
        Generate the optimized SQL query:
        """
        
        response = self.llm.invoke([
            SystemMessage(content="You are a senior database architect generating production-ready SQL queries."),
            HumanMessage(content=prompt)
        ])
        
        sql = response.content.replace('```sql', '').replace('```', '').strip()
        state["sql_query"] = sql
        state["thought_process"].append(f"SQL Writer: Generated query with {len(sql.split())} tokens")
        return state

    def _build_history_context(self, state: AgentState) -> str:
        """Build conversation history context for better follow-up queries."""
        if not state.get("history"):
            return "No conversation history available."
        
        history_items = []
        for i, h in enumerate(state["history"][-3:], 1):  # Last 3 interactions
            history_items.append(f"Interaction {i}:")
            history_items.append(f"  User: {h['question']}")
            if 'sql' in h:
                history_items.append(f"  Generated SQL: {h['sql']}")
            if 'insight' in h:
                history_items.append(f"  Insight: {h['insight']}")
        
        return f"## CONVERSATION HISTORY\n" + "\n".join(history_items) + "\n"

    def _build_business_context(self) -> str:
        """Build business context from metadata."""
        rules = self.metadata.get('business_rules', [])
        metrics = self.metadata.get('metrics', {})
        
        context = ["## BUSINESS CONTEXT"]
        if rules:
            context.append("Business Rules:")
            for rule in rules:
                context.append(f"  • {rule}")
        
        if metrics:
            context.append("\nAvailable Metrics:")
            for metric, definition in metrics.items():
                context.append(f"  • {metric}: {definition}")
        
        return "\n".join(context)

    def _build_schema_context(self, schema: str) -> str:
        """Build enhanced schema context with column analysis."""
        if not schema:
            return "Schema information not available."
        
        columns = [col.strip() for col in schema.split(',')]
        context = ["## SCHEMA ANALYSIS"]
        
        # Categorize columns
        text_columns = []
        numeric_columns = []
        date_columns = []
        
        for col in columns:
            col_name = col.split('(')[0].strip()
            col_type = col.split('(')[1].replace(')', '').strip() if '(' in col else 'TEXT'
            
            if any(keyword in col_name.lower() for keyword in ['id', 'name', 'model', 'type']):
                text_columns.append(f"  • {col_name} ({col_type}) - Text/Identifier field")
            elif any(keyword in col_name.lower() for keyword in ['price', 'cost', 'amount', 'value']):
                numeric_columns.append(f"  • {col_name} ({col_type}) - Numeric/Monetary field")
            elif any(keyword in col_name.lower() for keyword in ['date', 'time', 'year']):
                date_columns.append(f"  • {col_name} ({col_type}) - Date/Time field")
            else:
                context.append(f"  • {col_name} ({col_type}) - {col_type} field")
        
        if text_columns:
            context.extend(["\nText/Identifier Fields:", "\n".join(text_columns)])
        if numeric_columns:
            context.extend(["\nNumeric/Monetary Fields:", "\n".join(numeric_columns)])
        if date_columns:
            context.extend(["\nDate/Time Fields:", "\n".join(date_columns)])
        
        return "\n".join(context)
