import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import google.generativeai as genai
import os
import json
import traceback
import logging
from memory.session_memory import memory_manager

# Configure genai for Context Caching
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")
logger = logging.getLogger(__name__)

# Global dict to store context caches
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
        
        # 2. Build schema and check caching
        if file_path not in CSV_SCHEMA_CACHES:
            columns = list(df.columns)
            
            def truncate_value(v):
                if isinstance(v, str) and len(v) > 100:
                    return v[:100] + "..."
                return v
            
            sample = df.head(1).applymap(truncate_value).to_dict(orient="records")
            dtype_summary = df.dtypes.apply(lambda x: x.name).to_dict()
            
            schema_str = ", ".join([f"{col}({dtype_summary[col]})" for col in columns])
            if len(columns) > 50:
                schema_str = f"{len(columns)} columns (showing first 50): " + schema_str[:500] + "..."
            
            # The fixed part of the prompt to cache
            schema_prompt_part = f"""
You are a senior data scientist. Pandas DataFrame 'df':
- {len(df)} rows × {len(df.columns)} columns
- Columns & types: {schema_str}
- Sample (truncated): {sample}
"""
            # Create Gemini Context Cache
            cached_content = None
            if api_key:
                try:
                    # Context caching requires a minimum token size (~32k tokens depending on model limits).
                    # If this tiny schema doesn't fit the min req, it will naturally throw an exception
                    # which we catch, defaulting to standard prefix string insertion.
                    cached_content = genai.caching.CachedContent.create(
                        model='models/gemini-2.0-flash-exp',
                        display_name=f"csv_cache_{os.path.basename(file_path)}",
                        system_instruction="Return strictly Python code. No markdown. No explanations.",
                        contents=[schema_prompt_part],
                        ttl=3600 # 1 hour
                    )
                    logger.info(f"Successfully created Context Cache for {os.path.basename(file_path)}")
                except Exception as e:
                    logger.warning(f"Could not use context caching (possibly due to token count or limits): {str(e)}")
                
            CSV_SCHEMA_CACHES[file_path] = {
                "schema_prompt": schema_prompt_part,
                "cached_content": cached_content
            }
        
        cache_data = CSV_SCHEMA_CACHES[file_path]
        prompt_prefix = cache_data["schema_prompt"]
        cached_content = cache_data["cached_content"]
        
        # 3. Dynamic Task Prompt
        task_prompt = f"""
{history_str}

User Question: {question}

Write a Python snippet to answer this. 
1. Perform any necessary filtering, aggregation, or calculation.
2. Store the primary result in a variable called 'result' as a list of dictionaries.
3. Store a brief insight about the findings in a variable called 'insight' (string).
4. Recommend a chart type ('bar', 'line', 'pie', 'kpi', or 'none') in a variable 'chart_type'.

Return ONLY valid Python code. No ```python blocks.
"""
        # Execute LLM Call
        response = None
        
        if cached_content:
            try:
                # Attempt to use cache via standard list syntax (supported in recent versions)
                response = llm.invoke([cached_content, HumanMessage(content=task_prompt)])
                code = response.content.replace('```python', '').replace('```', '').strip()
            except Exception as e:
                logger.warning(f"Failed to invoke LLM with cached content object: {e}")
                
        if not response:
            # Fallback path (no cache or cache invocation failed)
            full_prompt = prompt_prefix + "\n" + task_prompt
            
            # Token limit safety fallback on sample string length
            # Add monitoring log for token count
            try:
                prompt_tokens = llm.get_num_tokens(full_prompt)
            except:
                prompt_tokens = len(full_prompt) // 4 + 1000
                
            logger.info(f"CSV Pipeline prompt token count: {prompt_tokens}")
            
            if prompt_tokens > 30000:
                # Remove sample from schema prompt
                safe_prefix = prompt_prefix.split("- Sample ")[0] + "- Sample: Not provided due to length constraints.\n"
                full_prompt = safe_prefix + "\n" + task_prompt

            response = llm.invoke([
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
