import os

file_path = "pipelines/csv_pipeline.py"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace(
    'llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")\nlogger = logging.getLogger(__name__)',
    'llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")\nfrom utils.api_handler import get_llm, safe_llm_invoke\nlogger = logging.getLogger(__name__)'
)

text = text.replace(
    'llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")\r\nlogger = logging.getLogger(__name__)',
    'llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")\r\nfrom utils.api_handler import get_llm, safe_llm_invoke\r\nlogger = logging.getLogger(__name__)'
)

old_sample = '''            def truncate_value(v):
                if isinstance(v, str) and len(v) > 100:
                    return v[:100] + "..."
                return v
            
            sample = df.head(1).map(truncate_value).to_dict(orient="records")
            dtype_summary = df.dtypes.apply(lambda x: x.name).to_dict()'''

new_sample = '''            # Safest Hackathon Fix: Send only the CSV headers and the first 2 rows
            sample = df.head(2).to_csv(index=False)
            dtype_summary = df.dtypes.apply(lambda x: x.name).to_dict()'''

text = text.replace(old_sample, new_sample)
text = text.replace(old_sample.replace('\n', '\r\n'), new_sample.replace('\n', '\r\n'))

text = text.replace(
    'response = llm.invoke([cached_content, HumanMessage(content=task_prompt)])',
    'response = safe_llm_invoke(get_llm(), [cached_content, HumanMessage(content=task_prompt)])'
)

text = text.replace(
    'prompt_tokens = llm.get_num_tokens(full_prompt)',
    'prompt_tokens = get_llm().get_num_tokens(full_prompt)'
)

old_invoke = '''            response = llm.invoke([
                SystemMessage(content="Return strictly Python code. No markdown. No explanations."),
                HumanMessage(content=full_prompt)
            ])'''

new_invoke = '''            response = safe_llm_invoke(get_llm(), [
                SystemMessage(content="Return strictly Python code. No markdown. No explanations."),
                HumanMessage(content=full_prompt)
            ])'''

text = text.replace(old_invoke, new_invoke)
text = text.replace(old_invoke.replace('\n', '\r\n'), new_invoke.replace('\n', '\r\n'))

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Modified csv_pipeline.py successfully!")
