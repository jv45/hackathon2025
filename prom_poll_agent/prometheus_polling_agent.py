import time
import requests
import numpy as np
from sklearn.ensemble import IsolationForest
import json

PROMETHEUS_URL = "http://prometheus:9090"
MASTER_AGENT_URL = "http://master-agent:port/endpoint"  # Replace with actual URL and endpoint
WINDOW_SIZE = 100  # Number of data points to train the model
STD_DEV_THRESHOLD = 2  # Number of standard deviations to flag an anomaly

# Dictionary to store the metric values for training the model
metric_values_dict = {}

def get_all_metrics():
    """Fetch all available metric names from Prometheus."""
    response = requests.get(f"{PROMETHEUS_URL}/api/v1/label/__name__/values")
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        print("Error fetching metrics:", response.text)
        return []

def fetch_metrics():
    """Fetch data for all available metrics and evaluate anomalies."""
    metrics = get_all_metrics()
    if not metrics:
        print("No metrics found.")
        return

    while True:
        results = []
        for metric_name in metrics:
            try:
                print(f"Fetching metrics for {metric_name} from {PROMETHEUS_URL}")
                response = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": metric_name})
                response.raise_for_status()
                data = response.json()
                # Extract and print the metric value
                if data['status'] == 'success' and data['data']['result']:
                    metric_value = float(data['data']['result'][0]['value'][1])
                    print(f"Fetched Metric Value for {metric_name}: {metric_value}")
                    # Add the metric value to the list
                    if metric_name not in metric_values_dict:
                        metric_values_dict[metric_name] = []
                    metric_values_dict[metric_name].append(metric_value)
                    # Keep only the last WINDOW_SIZE values
                    if len(metric_values_dict[metric_name]) > WINDOW_SIZE:
                        metric_values_dict[metric_name].pop(0)
                    # Check for anomalies if we have enough data points
                    if len(metric_values_dict[metric_name]) == WINDOW_SIZE:
                        is_anomaly = check_for_anomalies(metric_name, metric_value)
                        result = {
                            "metric_name": metric_name,
                            "metric_value": metric_value,
                            "anomaly_detected": is_anomaly
                        }
                        results.append(result)
                else:
                    print(f"No data found for the metric {metric_name}.")
            except requests.exceptions.RequestException as e:
                print(f"Exception occurred while fetching {metric_name}: {e}")
                print("Retrying in 5 seconds...")
            time.sleep(5)
        
        # Print results in JSON format
        print(json.dumps(results, indent=4))
        time.sleep(60)  # Wait for 1 minute before fetching the metrics again

def check_for_anomalies(metric_name, metric_value):
    # Train the Isolation Forest model
    model = IsolationForest(contamination=0.1)
    model.fit(np.array(metric_values_dict[metric_name]).reshape(-1, 1))
    # Predict anomalies
    prediction = model.predict([[metric_value]])
    mean = np.mean(metric_values_dict[metric_name])
    std_dev = np.std(metric_values_dict[metric_name])
    is_anomaly = False

    if prediction[0] == -1:
        print(f"Isolation Forest detected anomaly for {metric_name}! Metric Value: {metric_value}")
        is_anomaly = True

    if abs(metric_value - mean) > STD_DEV_THRESHOLD * std_dev:
        print(f"Standard Deviation detected anomaly for {metric_name}! Metric Value: {metric_value}, Mean: {mean}, Std Dev: {std_dev}")
        is_anomaly = True

    if is_anomaly:
        print(f"Anomaly detected for {metric_name}")
        send_to_master_agent(metric_name, metric_value)

    return is_anomaly

def send_to_master_agent(metric_name, metric_value):
    try:
        response = requests.post(MASTER_AGENT_URL, json={"metric_name": metric_name, "metric_value": metric_value})
        response.raise_for_status()
        print(f"Successfully sent data for {metric_name} to master agent.")
    except requests.exceptions.RequestException as e:
        print(f"Exception occurred while sending data to master agent: {e}")

if __name__ == "__main__":
    print("Starting Prometheus polling agent...")
    fetch_metrics()