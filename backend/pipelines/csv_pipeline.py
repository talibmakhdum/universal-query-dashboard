import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import os
import json
import traceback

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

async def run_csv_query(file_path: str, question: str):
    """
    Analyzes CSV by letting the LLM generate Python code to process the full dataframe.
    This ensures mathematical accuracy on large datasets.
    """
    try:
        df = pd.read_csv(file_path)
        
        # Meta-information for code generation
        columns = list(df.columns)
        sample = df.head(2).to_dict(orient="records")
        dtype_summary = df.dtypes.apply(lambda x: x.name).to_dict()
        
        prompt = f"""
        You are a senior data scientist. You have a pandas DataFrame 'df' with:
        Columns: {columns}
        Data types: {dtype_summary}
        Sample: {sample}
        
        User Question: {question}
        
        Write a Python snippet to answer this. 
        1. Perform any necessary filtering, aggregation, or calculation.
        2. Store the primary result in a variable called 'result' as a list of dictionaries.
        3. Store a brief insight about the findings in a variable called 'insight' (string).
        4. Recommend a chart type ('bar', 'line', 'pie', 'kpi', or 'none') in a variable 'chart_type'.
        
        Return ONLY valid Python code. No ```python blocks.
        """
        
        response = llm.invoke([
            SystemMessage(content="Return strictly Python code. No markdown. No explanations."),
            HumanMessage(content=prompt)
        ])
        
        code = response.content.replace('```python', '').replace('```', '').strip()
        
        # execution context
        exec_globals = {"df": df, "pd": pd}
        exec_locals = {}
        
        # Execute the generated code
        exec(code, exec_globals, exec_locals)
        
        return {
            "success": True,
            "data": exec_locals.get("result", []),
            "insight": exec_locals.get("insight", "Analysis complete."),
            "chartType": exec_locals.get("chart_type", "bar"),
            "code_executed": code
        }
        
    except Exception as e:
        print(f"CSV Analysis Error: {traceback.format_exc()}")
        return {
            "success": False,
            "error": f"Failed to analyze CSV dataset: {str(e)}"
        }
