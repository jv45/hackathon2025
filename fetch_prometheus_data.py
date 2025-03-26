import requests

# Prometheus server URL
PROMETHEUS_URL = "http://localhost:9090"
##PROMETHEUS_URL = "https://e742-2406-7400-98-79f0-58e3-9b48-242c-a6a2.ngrok-free.app/"

def get_all_metrics():
    """Fetch all available metric names from Prometheus."""
    response = requests.get(f"{PROMETHEUS_URL}/api/v1/label/__name__/values")
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        print("Error fetching metrics:", response.text)
        return []

def fetch_metric_data(metric_name):
    """Fetch the latest data for the selected metric."""
    response = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": metric_name})
    if response.status_code == 200:
        data = response.json().get("data", {}).get("result", [])
        
        if data:
            for item in data:
                metric_value = item['value'][1]
                result_str = f"Metric: {item['metric']}, Value: {item['value']}"
                print(result_str)
                print(f"Metric Value: {metric_value}")
        else:
            print("No data available for this metric.")
    else:
        print("Error fetching metric data:", response.text)

def main():
    """Main function to list metrics and allow user selection."""
    print("Fetching available metrics...")
    metrics = get_all_metrics()
    
    if not metrics:
        print("No metrics found.")
        return
    
    print("\nAvailable Metrics:")
    for i, metric in enumerate(metrics):
        print(f"{i + 1}. {metric}")

    try:
        choice = int(input("\nEnter the number of the metric you want to fetch data for: ")) - 1
        if 0 <= choice < len(metrics):
            selected_metric = metrics[choice]
            print(f"\nFetching data for: {selected_metric}")
            fetch_metric_data(selected_metric)
        else:
            print("Invalid selection.")
    except ValueError:
        print("Please enter a valid number.")

if __name__ == "__main__":
    main()
