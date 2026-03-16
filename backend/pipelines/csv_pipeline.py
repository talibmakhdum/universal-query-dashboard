import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import os
import json

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

async def run_csv_query(file_path: str, question: str):
    df = pd.read_csv(file_path)
    
    # Basic info for LLM
    columns = list(df.columns)
    sample = df.head(3).to_dict(orient="records")
    
    prompt = f"""
    You are an expert data analyst. You have a pandas DataFrame with columns: {columns}
    Sample Data: {sample}
    
    Question: {question}
    
    Return the result as a list of dictionaries in JSON format: {{"result": [{{...}}, {{...}}], "insight": "string"}}
    """
    
    response = llm.invoke([
        SystemMessage(content="You are a data assistant. Return JSON only."),
        HumanMessage(content=prompt)
    ])
    
    try:
        clean_res = response.content.replace('```json', '').replace('```', '').strip()
        data = json.loads(clean_res)
        return {
            "success": True,
            "data": data.get("result"),
            "insight": data.get("insight"),
            "chartType": "bar"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to analyze CSV: {str(e)}"
        }
