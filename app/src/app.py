# Point d'entree de l'API Flask
# API REST de gestion de citations (quotes) avec health check et metriques Prometheus.

import os
import time
from flask import Flask, request, jsonify

from quotes import _seed_defaults, list_quotes, get_quote, add_quote, delete_quote, count_quotes

app = Flask(__name__)

# Compteurs maison pour exposer des metriques au format Prometheus
# Pas de lib externe, on code le format exposition nous-memes pour bien comprendre
_request_counts = {}
_request_durations = {}
_start_time = time.time()


@app.before_request
def _before():
    """Enregistre le timestamp de debut de requete."""
    request._start_time = time.time()


@app.after_request
def _after(response):
    """Collecte les metriques apres chaque requete."""
    duration = time.time() - getattr(request, "_start_time", time.time())
    key = f'{request.method} {request.path} {response.status_code}'

    _request_counts[key] = _request_counts.get(key, 0) + 1

    if key not in _request_durations:
        _request_durations[key] = {"sum": 0.0, "count": 0}
    _request_durations[key]["sum"] += duration
    _request_durations[key]["count"] += 1

    return response


@app.route("/")
def index():
    """Endpoint racine, renvoie les infos de l'API."""
    return jsonify({
        "service": "quotes-api",
        "version": "1.0.0",
        "description": "API de gestion de citations",
        "endpoints": ["/quotes", "/health", "/metrics"],
    })


@app.route("/health")
def health():
    """Health check standard -- utilise par Docker HEALTHCHECK et les probes K8s."""
    return jsonify({"status": "healthy", "quotes_count": count_quotes()})


@app.route("/metrics")
def metrics():
    """Expose les metriques au format Prometheus text exposition.
    Ref: https://prometheus.io/docs/instrumenting/exposition_formats/
    """
    lines = [
        "# HELP http_requests_total Total number of HTTP requests.",
        "# TYPE http_requests_total counter",
    ]
    for key, count in _request_counts.items():
        method, path, status = key.rsplit(" ", 2)
        lines.append(
            f'http_requests_total{{method="{method}",path="{path}",status="{status}"}} {count}'
        )

    lines.append("# HELP http_request_duration_seconds HTTP request duration in seconds.")
    lines.append("# TYPE http_request_duration_seconds summary")
    for key, stats in _request_durations.items():
        method, path, status = key.rsplit(" ", 2)
        label = f'method="{method}",path="{path}",status="{status}"'
        lines.append(f"http_request_duration_seconds_sum{{{label}}} {stats['sum']:.6f}")
        lines.append(f"http_request_duration_seconds_count{{{label}}} {stats['count']}")

    lines.append("# HELP app_quotes_total Current number of quotes in memory.")
    lines.append("# TYPE app_quotes_total gauge")
    lines.append(f"app_quotes_total {count_quotes()}")

    lines.append("# HELP app_uptime_seconds Time since the app started.")
    lines.append("# TYPE app_uptime_seconds gauge")
    lines.append(f"app_uptime_seconds {time.time() - _start_time:.2f}")

    return "\n".join(lines) + "\n", 200, {"Content-Type": "text/plain; version=0.0.4; charset=utf-8"}


# --- CRUD citations ---

@app.route("/quotes", methods=["GET"])
def get_quotes():
    return jsonify(list_quotes())


@app.route("/quotes/<quote_id>", methods=["GET"])
def get_single_quote(quote_id):
    quote = get_quote(quote_id)
    if quote is None:
        return jsonify({"error": "Quote not found"}), 404
    return jsonify(quote)


@app.route("/quotes", methods=["POST"])
def create_quote():
    data = request.get_json(silent=True)
    if not data or not data.get("author") or not data.get("text"):
        return jsonify({"error": "Fields 'author' and 'text' are required"}), 400
    quote = add_quote(data["author"], data["text"])
    return jsonify(quote), 201


@app.route("/quotes/<quote_id>", methods=["DELETE"])
def remove_quote(quote_id):
    if delete_quote(quote_id):
        return jsonify({"deleted": True}), 200
    return jsonify({"error": "Quote not found"}), 404


# Seed des citations par defaut au demarrage
_seed_defaults()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
