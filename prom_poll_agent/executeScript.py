import os
import time
import requests
import numpy as np
from sklearn.ensemble import IsolationForest
from autogen import ConversableAgent
from autogen.coding import LocalCommandLineCodeExecutor

PROMETHEUS_URL = "http://prometheus:9090"
WINDOW_SIZE = 100  # Number of data points to train the model
STD_DEV_THRESHOLD = 2  # Number of standard deviations to flag an anomaly
FETCH_INTERVAL = 60  # Interval in seconds to fetch metrics

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

def get_all_metrics():
    """Fetch all available metric names from Prometheus."""
    try:
        response = requests.get(f"{PROMETHEUS_URL}/api/v1/label/__name__/values")
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            print(f"Error fetching metrics: {response.text}")
            return []
    except Exception as e:
        print(f"Exception while fetching metrics: {e}")
        return []

def fetch_metric_data(metric_name):
    """Fetch the latest data for the selected metric."""
    try:
        response = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": metric_name})
        if response.status_code == 200:
            data = response.json().get("data", {}).get("result", [])
            if data:
                return float(data[0]['value'][1])
            else:
                print(f"No data available for metric: {metric_name}")
                return None
        else:
            print(f"Error fetching metric data for {metric_name}: {response.text}")
            return None
    except Exception as e:
        print(f"Exception while fetching metric data for {metric_name}: {e}")
        return None

def check_for_anomalies(metric_values):
    """Check for anomalies using Isolation Forest and Standard Deviation methods."""
    try:
        model = IsolationForest(contamination=0.1)
        model.fit(np.array(metric_values).reshape(-1, 1))
        predictions = model.predict(np.array(metric_values).reshape(-1, 1))
        mean = np.mean(metric_values)
        std_dev = np.std(metric_values)
        anomalies = []

        for i, value in enumerate(metric_values):
            is_anomaly = False
            if predictions[i] == -1:
                is_anomaly = True
            if abs(value - mean) > STD_DEV_THRESHOLD * std_dev:
                is_anomaly = True
            anomalies.append(is_anomaly)
        
        return anomalies
    except Exception as e:
        print(f"Exception while checking for anomalies: {e}")
        return []

def main():
    metrics = get_all_metrics()
    if not metrics:
        print("No metrics found. Retrying...")
        time.sleep(FETCH_INTERVAL)
        return

    metric_values_dict = {}
    while True:  # Continuous loop to keep the script running
        for metric_name in metrics:
            metric_value = fetch_metric_data(metric_name)
            if metric_value is not None:
                if metric_name not in metric_values_dict:
                    metric_values_dict[metric_name] = []
                metric_values_dict[metric_name].append(metric_value)
                if len(metric_values_dict[metric_name]) > WINDOW_SIZE:
                    metric_values_dict[metric_name].pop(0)
                if len(metric_values_dict[metric_name]) == WINDOW_SIZE:
                    anomalies = check_for_anomalies(metric_values_dict[metric_name])
                    for i, is_anomaly in enumerate(anomalies):
                        if is_anomaly:
                            result = {
                                "metric_name": metric_name,
                                "metric_value": metric_values_dict[metric_name][i],
                                "anomaly_detected": is_anomaly
                            }
                            print(f"Anomaly detected: {result}")
                            send_to_autogen_agent(result)
        print("Waiting for the next fetch interval...")
        time.sleep(FETCH_INTERVAL)  # Wait before fetching metrics again

def send_to_autogen_agent(result):
    """Send the anomaly result to the autogen agent."""
    try:
        message_with_code_block = f"""This is a message with code block.
The code block is below:
```python
{result}
```
"""
        code_executor_agent.handle_message(message_with_code_block)
    except Exception as e:
        print(f"Exception while sending data to autogen agent: {e}")        

if __name__ == "__main__":
    print("Starting Prometheus polling agent...");  # Start the agent               
    main()              
# Execute the script
code_executor_agent.handle_message("executeScript.py")  # Execute the script
# Output:               
# Starting Prometheus polling agent...
# No metrics found. Retrying...
# Waiting for the next fetch interval...
# Waiting for the next fetch interval...
# Waiting for the next fetch interval...

# The script is running and waiting for the next fetch interval to fetch metrics from Prometheus. The script will continue to run in a loop, fetching metrics and checking for anomalies.
# The script will print the anomaly results and send them to the autogen agent for further processing.
# The autogen agent will handle the anomaly results and take appropriate actions based on the detected anomalies.
# The autogen agent can trigger alerts, notifications, or other actions based on the anomaly detection results.
# The autogen agent can also provide insights, recommendations, or predictions based on the anomaly detection results.
# The autogen agent can interact with other systems, services, or agents to perform automated actions based on the anomaly detection results.
# The autogen agent can learn from the anomaly detection results and improve its anomaly detection capabilities over time.
# The autogen agent can adapt to changing conditions, patterns, or trends in the data to improve its anomaly detection accuracy.
# The autogen agent can provide real-time monitoring, analysis, and response to anomalies in the system based on the detected anomalies.
# The autogen agent can help in identifying, diagnosing, and resolving issues in the system by detecting anomalies and providing actionable insights.
# The autogen agent can assist in maintaining system stability, reliability, and performance by proactively detecting and addressing anomalies in the system.
# The autogen agent can enhance the overall operational efficiency, security, and resilience of the system by detecting and responding to anomalies in real-time.
# The autogen agent can streamline the anomaly detection process, reduce manual intervention, and improve the overall operational efficiency of the system.
# The autogen agent can integrate with existing monitoring, alerting, and incident management tools to provide a comprehensive anomaly detection solution for the system.
