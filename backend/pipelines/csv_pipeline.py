import pandas as pd
from langchain_core.messages import SystemMessage, HumanMessage
import os
import json
import traceback
import logging
from memory.session_memory import memory_manager
from utils.api_handler import get_llm, safe_llm_invoke

logger = logging.getLogger(__name__)

# Global dict to store schema prompt caches (in-memory, per-file)
CSV_SCHEMA_CACHES = {}

async def run_csv_query(file_path: str, question: str, session_id: str = "default"):
    """
    Analyzes CSV by letting the LLM generate Python code to process the full dataframe.
    This ensures mathematical accuracy on large datasets.
    """
    try:
        df = pd.read_csv(file_path)
        
        # 1. Fetch Chat History (Summarized to prevent token explosion)
        history = memory_manager.get_history(session_id, include_context=True)
        history_str = ""
        if history:
            history_str = "Conversation History:\n"
            for entry in history[-5:]: # last 5 exchanges
                if entry.get("type") == "summary":
                    history_str += f"- [Summary]: {entry.get('content')}\n"
                else:
                    q = entry.get("question", "")
                    # Limit insight text length from history
                    a = str(entry.get("insight", ""))[:150]
                    history_str += f"- Question: {q}\n- Insight: {a}\n"
        
        # 2. Build schema prompt (cached in-memory per file path)
        if file_path not in CSV_SCHEMA_CACHES:
            columns = list(df.columns)
            
            # Safest Hackathon Fix: Send only the CSV headers and the first 2 rows
            sample = df.head(2).to_csv(index=False)
            dtype_summary = df.dtypes.apply(lambda x: x.name).to_dict()
            
            schema_str = ", ".join([f"{col}({dtype_summary[col]})" for col in columns])
            if len(columns) > 50:
                schema_str = f"{len(columns)} columns (showing first 50): " + schema_str[:500] + "..."
            
            schema_prompt_part = f"""
You are a senior data scientist. Pandas DataFrame 'df':
- {len(df)} rows x {len(df.columns)} columns
- Columns & types: {schema_str}
- Sample (truncated): {sample}
"""
            CSV_SCHEMA_CACHES[file_path] = schema_prompt_part
        
        prompt_prefix = CSV_SCHEMA_CACHES[file_path]
        
        # 3. Dynamic Task Prompt
        task_prompt = f"""
{history_str}

User Question: {question}

Write a Python snippet to answer this. 
1. Perform any necessary filtering, aggregation, or calculation.
2. Store the primary result in a variable called 'result' as a list of dictionaries.
3. Store a brief insight about the findings in a variable called 'insight' (string).
4. Recommend a chart type ('bar', 'line', 'pie', 'kpi', or 'none') in a variable 'chart_type'.
5. Do NOT use the deprecated DataFrame.applymap() or DataFrame.apply() methods. Use DataFrame.map() instead if needed.

Return ONLY valid Python code. No ```python blocks.
"""
        # Build the full prompt
        full_prompt = prompt_prefix + "\n" + task_prompt
        
        # Token limit safety fallback
        try:
            prompt_tokens = get_llm().get_num_tokens(full_prompt)
        except:
            prompt_tokens = len(full_prompt) // 4 + 1000
            
        logger.info(f"CSV Pipeline prompt token count: {prompt_tokens}")
        
        if prompt_tokens > 30000:
            # Remove sample from schema prompt
            safe_prefix = prompt_prefix.split("- Sample ")[0] + "- Sample: Not provided due to length constraints.\n"
            full_prompt = safe_prefix + "\n" + task_prompt

        response = safe_llm_invoke(get_llm(), [
            SystemMessage(content="Return strictly Python code. No markdown. No explanations."),
            HumanMessage(content=full_prompt)
        ])
        code = response.content.replace('```python', '').replace('```', '').strip()
        
        # execution context
        exec_globals = {"df": df, "pd": pd}
        exec_locals = {}
        
        # Execute the generated code
        exec(code, exec_globals, exec_locals)
        
        # Extract variables
        data = exec_locals.get("result", [])
        insight = exec_locals.get("insight", "Analysis complete.")
        chart_type = exec_locals.get("chart_type", "bar")
        
        # 4. Update session memory for CSV queries
        memory_manager.update_memory(session_id, {
            "question": question,
            "insight": insight,
            "code": code
        })
        
        return {
            "success": True,
            "data": data,
            "insight": insight,
            "chartType": chart_type,
            "code_executed": code
        }
        
    except Exception as e:
        logger.error(f"CSV Analysis Error: {traceback.format_exc()}")
        return {
            "success": False,
            "error": f"Failed to analyze CSV dataset: {str(e)}"
        }
