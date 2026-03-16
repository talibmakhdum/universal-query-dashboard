# agent_graph.py

from langgraph import LangGraph

# Initialize the LangGraph workflow
workflow = LangGraph()

# Define agents
planner = workflow.add_agent('planner')
sql_writer = workflow.add_agent('sql_writer')
sql_critic = workflow.add_agent('sql_critic')
executor = workflow.add_agent('executor')

# Define the self-correction loop
planner.set_next_agent(sql_writer)
sql_writer.set_next_agent(sql_critic)
sql_critic.set_next_agent(executor)
executor.set_prediction_loop(planner)

# Execute the workflow
workflow.run()