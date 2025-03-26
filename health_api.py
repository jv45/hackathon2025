import time
import threading
import requests
import numpy as np
from flask import Flask, request, jsonify
from sklearn.ensemble import IsolationForest
from autogen import ConversableAgent
from autogen.coding import LocalCommandLineCodeExecutor

app = Flask(__name__)

PROMETHEUS_URL = "http://localhost:9090"
WINDOW_SIZE = 10
STD_DEV_THRESHOLD = 2
FETCH_INTERVAL = 10  # Interval in seconds to fetch metrics

# Dictionary to store metric values for anomaly detection
metric_values_dict = {}

# Create a local command line code executor
executor = LocalCommandLineCodeExecutor(timeout=10, work_dir=".")

# Create an agent with code executor configuration
code_executor_agent = ConversableAgent(
    "code_executor_agent",
    llm_config=False,
    code_execution_config={"executor": executor},
    human_input_mode="NEVER",
)

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

def check_for_anomalies(metric_name, metric_values):
    """Check for anomalies using Isolation Forest and Standard Deviation methods."""
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
    
    return anomalies[-1] if anomalies else False

def send_to_agent(metric_name, metric_value):
    """Send anomaly details to the agent."""
    try:
        message = f"Anomaly detected for metric: {metric_name}, value: {metric_value}"
        print(f"Sending to agent: {message}")
        code_executor_agent.handle_message(message)
    except Exception as e:
        print(f"Exception while sending data to agent: {e}")

def log_anomaly(metric_name, metric_value):
    """Log the anomaly details."""
    print(f"Logging anomaly: Metric: {metric_name}, Value: {metric_value}")

def trigger_alert(metric_name, metric_value):
    """Trigger an alert for the detected anomaly."""
    print(f"Triggering alert: Metric: {metric_name}, Value: {metric_value}")
    # Example: Integrate with an alerting system (e.g., email, Slack, etc.)

def prefill_metric_data(metrics):
    """Pre-fill metric_values_dict with dummy data for testing."""
    for metric_name in metrics:
        if metric_name not in metric_values_dict:
            metric_values_dict[metric_name] = [1.0] * WINDOW_SIZE  # Pre-fill with dummy values

def monitoring_agent():
    """Background thread to monitor Prometheus metrics for anomalies."""
    while True:
        metrics = get_all_metrics()
        for metric_name in metrics:
            metric_value = fetch_metric_data(metric_name)
            if metric_value is not None:
                if metric_name not in metric_values_dict:
                    metric_values_dict[metric_name] = []
                metric_values_dict[metric_name].append(metric_value)
                if len(metric_values_dict[metric_name]) > WINDOW_SIZE:
                    metric_values_dict[metric_name].pop(0)
                if len(metric_values_dict[metric_name]) == WINDOW_SIZE:
                    is_anomaly = check_for_anomalies(metric_name, metric_values_dict[metric_name])
                    if is_anomaly:
                        print(f"Anomaly detected for {metric_name}: {metric_value}")
                        log_anomaly(metric_name, metric_value)
                        send_to_agent(metric_name, metric_value)
                        trigger_alert(metric_name, metric_value)
        time.sleep(FETCH_INTERVAL)

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

@app.route('/check_health', methods=['GET'])
def check_health():
    """Endpoint to check the health of all available metrics."""
    appid = request.args.get('appid')
    simulate_anomaly = request.args.get('simulate_anomaly', 'false').lower() == 'true'

    if not appid:
        return jsonify({"error": "appid is required"}), 400

    # Fetch all available metrics
    all_metrics = get_all_metrics()
    if not all_metrics:
        return jsonify({"error": "No metrics available in Prometheus"}), 404

    # Pre-fill data if simulate_anomaly is enabled
    if simulate_anomaly:
        print("Simulating anomalies: Pre-filling metric data for demo purposes.")
        prefill_metric_data(all_metrics)

    # Analyze each metric
    results = []
    for metric_name in all_metrics:
        metric_value = fetch_metric_data(metric_name)
        if metric_value is not None:
            if metric_name not in metric_values_dict:
                metric_values_dict[metric_name] = []
            metric_values_dict[metric_name].append(metric_value)
            if len(metric_values_dict[metric_name]) > WINDOW_SIZE:
                metric_values_dict[metric_name].pop(0)

            # Simulate anomaly if the flag is set
            if simulate_anomaly:
                print(f"Simulating anomaly for metric: {metric_name}")
                is_anomaly = True
                health_status = "Unhealthy"
                log_anomaly(metric_name, metric_value)
                send_to_agent(metric_name, metric_value)
            elif len(metric_values_dict[metric_name]) == WINDOW_SIZE:
                is_anomaly = check_for_anomalies(metric_name, metric_values_dict[metric_name])
                health_status = "Unhealthy" if is_anomaly else "Healthy"
                if is_anomaly:
                    log_anomaly(metric_name, metric_value)
                    send_to_agent(metric_name, metric_value)
            else:
                is_anomaly = False  # Default to no anomaly if insufficient data
                health_status = "Insufficient data"

            results.append({
                "metric_name": metric_name,
                "metric_value": metric_value,
                "health_status": health_status,
                "anomaly_detected": is_anomaly
            })

    if not results:
        return jsonify({"error": "No valid data found for metrics"}), 404

    return jsonify({"appid": appid, "metrics": results})

if __name__ == "__main__":
    print("Starting the monitoring agent...")
    # Start the monitoring agent in a background thread
    monitoring_thread = threading.Thread(target=monitoring_agent, daemon=True)
    monitoring_thread.start()
    print("Monitoring agent started.")

    print("Starting the Flask app...")
    # Start the Flask app
    app.run(host='0.0.0.0', port=6075, debug=True)