import os
import time
import logging

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = Flask(__name__)

database_url = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/flaskdb"
)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

REQUEST_COUNT = Counter(
    "flask_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "flask_http_request_duration_seconds",
    "HTTP request latency",
    ["endpoint"]
)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)


@app.before_request
def start_timer():
    app.start_time = time.time()


@app.after_request
def track_request(response):
    endpoint = "unknown"
    if hasattr(response, "request"):
        endpoint = response.request.path

    REQUEST_COUNT.labels(
        method="GET",
        endpoint=endpoint,
        status=response.status_code
    ).inc()

    REQUEST_LATENCY.labels(endpoint=endpoint).observe(
        time.time() - app.start_time
    )

    logger.info("request_completed status=%s", response.status_code)
    return response


@app.route("/")
def home():
    return jsonify(
        message="Flask DevOps assessment application is running",
        environment=os.getenv("ENVIRONMENT", "local")
    )


@app.route("/health")
def health():
    try:
        db.session.execute(db.text("SELECT 1"))
        return jsonify(status="healthy", database="connected"), 200
    except Exception as error:
        logger.exception("Health check failed")
        return jsonify(status="unhealthy", error=str(error)), 500


@app.route("/todos", methods=["GET"])
def list_todos():
    todos = Todo.query.all()
    return jsonify(
        [{"id": todo.id, "title": todo.title} for todo in todos]
    )


@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {
        "Content-Type": CONTENT_TYPE_LATEST
    }


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=5000)