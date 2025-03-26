import time
import requests
import numpy as np
from sklearn.ensemble import IsolationForest

PROMETHEUS_URL = "http://prometheus:9090/api/v1/query?query=process_cpu_seconds_total"
MASTER_AGENT_URL = "http://master-agent:port/endpoint"  # Replace with actual URL and endpoint
WINDOW_SIZE = 100  # Number of data points to train the model
STD_DEV_THRESHOLD = 2  # Number of standard deviations to flag an anomaly

# List to store the metric values for training the model
metric_values = []

def fetch_metrics():
    while True:
        try:
            print(f"Fetching metrics from {PROMETHEUS_URL}")
            response = requests.get(PROMETHEUS_URL)
            response.raise_for_status()
            data = response.json()
            # Extract and print the metric value
            if data['status'] == 'success' and data['data']['result']:
                metric_value = float(data['data']['result'][0]['value'][1])
                print("Fetched Metric Value:", metric_value)
                # Add the metric value to the list
                metric_values.append(metric_value)
                # Keep only the last WINDOW_SIZE values
                if len(metric_values) > WINDOW_SIZE:
                    metric_values.pop(0)
                # Check for anomalies if we have enough data points
                if len(metric_values) == WINDOW_SIZE:
                    check_for_anomalies(metric_value)
            else:
                print("No data found for the metric.")
        except requests.exceptions.RequestException as e:
            print(f"Exception occurred: {e}")
            print("Retrying in 5 seconds...")
        time.sleep(5)

def check_for_anomalies(metric_value):
    # Train the Isolation Forest model
    model = IsolationForest(contamination=0.1)
    model.fit(np.array(metric_values).reshape(-1, 1))
    # Predict anomalies
    prediction = model.predict([[metric_value]])
    mean = np.mean(metric_values)
    std_dev = np.std(metric_values)
    is_anomaly = False

    if prediction[0] == -1:
        print(f"Isolation Forest detected anomaly! Metric Value: {metric_value}")
        is_anomaly = True

    if abs(metric_value - mean) > STD_DEV_THRESHOLD * std_dev:
        print(f"Standard Deviation detected anomaly! Metric Value: {metric_value}, Mean: {mean}, Std Dev: {std_dev}")
        is_anomaly = True

    if is_anomaly:
        print("Anomaly detected")
        send_to_master_agent(metric_value)

def send_to_master_agent(metric_value):
    try:
        response = requests.post(MASTER_AGENT_URL, json={"metric_value": metric_value})
        response.raise_for_status()
        print("Successfully sent data to master agent.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send data to master agent: {e}")

if __name__ == "__main__":
    print("Starting Prometheus polling agent...")
    fetch_metrics()