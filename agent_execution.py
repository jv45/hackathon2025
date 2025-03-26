import os
from autogen import ConversableAgent
from autogen.coding import LocalCommandLineCodeExecutor

FileToExecute = "healthcheck.py" # Mention File to Execute

# Create a temporary directory to store the code files.
temp_dir = os.getcwd()

# Create a local command line code executor.
executor = LocalCommandLineCodeExecutor(
    timeout=10,  # Timeout for each code execution in seconds.
    work_dir=temp_dir,  # Use the temporary directory to store the code files.
)

# Create an agent with code executor configuration.

code_executor_agent = ConversableAgent(
    "code_executor_agent",
    llm_config=False,  # Turn off LLM for this agent.
    code_execution_config={"executor": executor},  # Use the local command line code executor.
    human_input_mode="NEVER",  # Always take human input for this agent for safety.
)



print("Executing the Python script")
script = open(FileToExecute, "r").read()# command to run
#message_with_code_block= "Execute a python script HealthCheck.py"
message_with_code_block = f"""This is a message with code block.
The code block is below:
```python
{script}
```
This is the end of the message.
"""

# Generate a reply for the given code.
reply = code_executor_agent.generate_reply(messages=[{"role": "user", "content": message_with_code_block}])
print(reply)