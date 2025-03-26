# hackathon2025


Collecting workspace information### Project Summary: Health Monitoring and Anomaly Detection System

This project is a **health monitoring and anomaly detection system** designed to monitor system metrics (like CPU, memory, and disk usage) and application metrics from Prometheus. It uses **machine learning models** to detect anomalies in real-time and provides APIs for health checks and anomaly reporting.

---

### Key Components and Technologies Used:

1. **Technologies:**
   - **Python 3.11**: Core programming language.
   - **Flask**: Web framework for building APIs.
   - **Prometheus**: Monitoring and alerting toolkit for collecting metrics.
   - **Docker**: Containerization for deployment.
   - **scikit-learn**: Machine learning library for anomaly detection.
   - **psutil**: Library for system health monitoring.
   - **Prometheus Client**: For exposing metrics to Prometheus.

2. **Machine Learning Model:**
   - **Isolation Forest**:
     - A tree-based unsupervised anomaly detection algorithm.
     - Identifies anomalies by isolating data points in a feature space.
     - Configured with a contamination rate of `0.1` (10% of data points are assumed to be anomalies).

3. **Deployment Tools:**
   - **Docker Compose**: Orchestrates multiple services (Flask app, Prometheus, and AI agent).
   - **Prometheus.yml**: Configures Prometheus to scrape metrics from the Flask app.

---

### How It Works:

1. **Data Collection:**
   - Prometheus scrapes metrics from the Flask app (`dummy_app.py`) and system metrics.
   - Metrics are fetched using Prometheus APIs.

2. **Anomaly Detection:**
   - Metrics are stored in a sliding window of size `WINDOW_SIZE` (e.g., 100).
   - The **Isolation Forest** model is trained on the sliding window data.
   - Anomalies are detected based on:
     - Isolation Forest predictions.
     - Standard deviation thresholds.

3. **Health Monitoring:**
   - The Flask API (`health_api.py`) provides an endpoint (`/check_health`) to check the health of metrics.
   - Anomalies trigger alerts, logging, and agent notifications.

4. **Agent Model:**
   - The AI agent (`executeScript.py`) continuously monitors metrics, detects anomalies, and sends results to an external agent (`autogen`).

---

### Deployment Steps:

1. **Install Python and Dependencies:**
   - Install Python 3.11 using the provided installation steps.
   - Create a virtual environment and install dependencies:
     ```sh
     python -m venv venv
     venv\Scripts\activate
     pip install -r requirements.txt
     ```

2. **Run Locally:**
   - Start the Flask app:
     ```sh
     python dummy_app.py
     ```
   - Start Prometheus:
     ```sh
     prometheus --config.file=prometheus.yml
     ```

3. **Run with Docker Compose:**
   - Build and start all services:
     ```sh
     docker-compose up --build
     ```

4. **Access Services:**
   - Flask app: `http://localhost:5000`
   - Prometheus: `http://localhost:9090`

---

### Functionality of Scripts:

1. **API Model (`health_api.py`):**
   - Provides a `/check_health` endpoint to:
     - Fetch metrics from Prometheus.
     - Detect anomalies using the Isolation Forest model.
     - Return health status for each metric.

2. **Agent Model (`executeScript.py`):**
   - Continuously fetches metrics from Prometheus.
   - Detects anomalies using the Isolation Forest model.
   - Sends anomaly results to an external agent (`autogen`).

3. **Prometheus Polling Agent (`prometheus_polling_agent.py`):**
   - Fetches all metrics from Prometheus.
   - Detects anomalies for each metric.
   - Sends anomaly data to a master agent.

4. **System Health Check (`healthcheck.py`):**
   - Monitors system metrics like CPU, memory, and disk usage.
   - Prints health statistics to the console.

---

### Summary of ML Model:

- **Isolation Forest**:
  - Trained on a sliding window of metric values.
  - Flags anomalies based on:
    - Isolation Forest predictions (`-1` indicates an anomaly).
    - Metric values deviating beyond `STD_DEV_THRESHOLD` standard deviations from the mean.

---

This solution provides a robust framework for real-time health monitoring and anomaly detection, leveraging Prometheus for metric collection, Flask for APIs, and machine learning for anomaly detection.
