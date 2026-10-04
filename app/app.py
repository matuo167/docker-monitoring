import time

from flask import Flask, Response, jsonify, request
from prometheus_client import Counter, Histogram, generate_latest


app = Flask(__name__)

# Keep labels low-cardinality: endpoint is a Flask route, not the raw URL.
HTTP_REQUESTS = Counter(
    "http_requests_total",
    "Total number of HTTP requests handled by the application",
    ["method", "endpoint", "status"],
)
HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)


@app.before_request
def start_timer():
    request.request_start_time = time.perf_counter()


@app.after_request
def record_metrics(response):
    # /metrics is intentionally included so the Prometheus scrape is visible.
    endpoint = request.url_rule.rule if request.url_rule else request.path
    duration = time.perf_counter() - getattr(
        request, "request_start_time", time.perf_counter()
    )

    HTTP_REQUESTS.labels(
        method=request.method,
        endpoint=endpoint,
        status=str(response.status_code),
    ).inc()
    HTTP_REQUEST_DURATION.labels(
        method=request.method,
        endpoint=endpoint,
    ).observe(duration)
    return response


@app.get("/")
def index():
    return jsonify(
        message="Monitoring demo API is running",
        endpoints=["/", "/health", "/slow", "/error", "/metrics"],
    )


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/slow")
def slow():
    time.sleep(2)
    return jsonify(message="This response was intentionally delayed", delay_seconds=2)


@app.get("/error")
def error():
    return jsonify(error="Intentional error for monitoring practice"), 500


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), mimetype="text/plain; version=0.0.4")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
