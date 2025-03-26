from flask import Flask, jsonify
from prometheus_client import Counter, generate_latest

app = Flask(__name__)

# Prometheus Counter Metric
REQUEST_COUNT = Counter('app_requests_total', 'Total number of requests')


@app.route("/")
def home():
    REQUEST_COUNT.inc()
    return jsonify({"message": "Hello, this is a dummy application!"})

@app.route("/metrics")
def metrics():
    return generate_latest()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
