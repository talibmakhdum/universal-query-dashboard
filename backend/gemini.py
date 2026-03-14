import google.generativeai as genai
from typing import Dict, List, Any
import os
from dotenv import load_dotenv

load_dotenv()

class GeminiProcessor:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Define few-shot examples for NL to SQL conversion
        self.few_shot_examples = [
            {
                "question": "What is the average price?",
                "sql": "SELECT AVG(price) AS average_price FROM [TABLE_NAME]"
            },
            {
                "question": "Show me total sales by category",
                "sql": "SELECT category, SUM(sales) AS total_sales FROM [TABLE_NAME] GROUP BY category"
            },
            {
                "question": "What are the top 5 products by revenue?",
                "sql": "SELECT product, SUM(revenue) AS total_revenue FROM [TABLE_NAME] GROUP BY product ORDER BY total_revenue DESC LIMIT 5"
            },
            {
                "question": "How many records do we have?",
                "sql": "SELECT COUNT(*) AS record_count FROM [TABLE_NAME]"
            },
            {
                "question": "Show me sales over time",
                "sql": "SELECT date, SUM(sales) AS daily_sales FROM [TABLE_NAME] GROUP BY date ORDER BY date"
            },
            {
                "question": "What is the highest price?",
                "sql": "SELECT MAX(price) AS max_price FROM [TABLE_NAME]"
            },
            {
                "question": "Show me distribution by fuel type",
                "sql": "SELECT fuel_type, COUNT(*) AS count FROM [TABLE_NAME] GROUP BY fuel_type"
            },
            {
                "question": "What is the average mileage by year?",
                "sql": "SELECT year, AVG(mileage) AS avg_mileage FROM [TABLE_NAME] GROUP BY year"
            }
        ]
    
    def nl_to_sql(self, question: str, table_name: str, schema: Dict[str, str], history: List[Dict[str, str]]) -> str:
        """
        Convert natural language question to SQL query using Gemini.
        """
        # Build schema description
        schema_desc = "\n".join([f"- {col}: {dtype}" for col, dtype in schema.items()])
        
        # Build history context
        history_context = ""
        if history:
            history_context = "Previous questions and answers:\n"
            for item in history[-3:]:  # Use last 3 interactions
                history_context += f"Q: {item['question']}\nA: {item['insight']}\n"
        
        # Build few-shot examples with actual table name
        examples_text = "\n".join([
            f"Question: {ex['question']}\nSQL: {ex['sql'].replace('[TABLE_NAME]', table_name)}"
            for ex in self.few_shot_examples
        ])
        
        # Construct the prompt
        prompt = f"""
        You are an expert SQL query generator. Your task is to convert natural language questions into valid SQL SELECT queries.

        Database schema for table '{table_name}':
        {schema_desc}

        Examples of good conversions:
        {examples_text}

        {history_context}

        Question: {question}

        Instructions:
        - Generate only a SELECT statement that answers the question
        - Do not include any explanations or additional text
        - Use only the columns from the provided schema
        - If you cannot generate a valid query, respond with exactly 'CANNOT_ANSWER'
        - Ensure the query is safe and only performs read operations
        - Replace [TABLE_NAME] with the actual table name: {table_name}

        SQL Query:
        """
        
        try:
            response = self.model.generate_content(prompt)
            sql_query = response.text.strip()
            
            # Validate the response
            if sql_query.upper() == "CANNOT_ANSWER":
                return "CANNOT_ANSWER"
            
            # Basic validation: ensure it starts with SELECT
            if not sql_query.upper().strip().startswith("SELECT"):
                return "CANNOT_ANSWER"
            
            return sql_query
            
        except Exception as e:
            print(f"Error generating SQL: {e}")
            return "CANNOT_ANSWER"
    
    def generate_insight(self, data: List[Dict[str, Any]]) -> str:
        """
        Generate a business insight from the query results.
        """
        if not data:
            return "No data available to analyze."
        
        # Convert data to a more readable format for the model
        data_summary = str(data[:5])  # Take first 5 rows as sample
        
        prompt = f"""
        You are a business analyst. Summarize the following data in one clear, CEO-friendly sentence.
        Focus on the most important insight or trend.
        
        Data: {data_summary}
        
        Insight:
        """
        
        try:
            response = self.model.generate_content(prompt)
            insight = response.text.strip()
            
            # Ensure it's a proper sentence
            if insight and not insight.endswith('.'):
                insight += '.'
            
            return insight
            
        except Exception as e:
            print(f"Error generating insight: {e}")
            return "Data analysis completed successfully."