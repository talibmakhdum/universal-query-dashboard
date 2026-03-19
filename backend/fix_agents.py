import os

def process_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Generic replace:
    # 1. Import at top
    if "from utils.api_handler import get_llm, safe_llm_invoke" not in text:
        text = "from utils.api_handler import get_llm, safe_llm_invoke\n" + text
        
    # 2. Replaces instances of self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    for variant in ['\n', '\r\n']:
        old = 'self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")'
        text = text.replace(old, '# using api_handler get_llm now')

    # 3. Replace self.llm.invoke( with safe_llm_invoke(get_llm(),
    text = text.replace('self.llm.invoke(', 'safe_llm_invoke(get_llm(), ')
    text = text.replace('self.llm.invoke ([', 'safe_llm_invoke(get_llm(), [')
    text = text.replace('self.llm.invoke ( [', 'safe_llm_invoke(get_llm(), [')

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

process_file("agents/sql_writer.py")
process_file("agents/planner_agent.py")
process_file("agents/executor.py") # if it uses llm
print("Fixed agents")
