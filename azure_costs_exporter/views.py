from flask import Blueprint, Response, abort, current_app, request
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, generate_latest

from .prometheus_collector import AzureEABillingCollector


bp = Blueprint('views', __name__)
DEFAULT_SCRAPE_TIMEOUT = 10


def _get_timeout():
    try:
        return float(request.headers.get('X-Prometheus-Scrape-Timeout-Seconds'))
    except Exception:
        return DEFAULT_SCRAPE_TIMEOUT


@bp.route("/health")
def health():
    return 'ok'


@bp.route("/metrics")
def metrics():
    timeout = _get_timeout()
    collector = AzureEABillingCollector(
        current_app.config['PROMETHEUS_METRIC_NAME'],
        current_app.config['ENROLLMENT_NUMBER'],
        current_app.config['BILLING_API_ACCESS_KEY'],
        timeout
    )
    registry = CollectorRegistry()
    registry.register(collector)
    try:
        content = generate_latest(registry)
        return content, 200, {'Content-Type': CONTENT_TYPE_LATEST}
    except Exception as e:
        abort(Response("Scrape failed: {}".format(e), status=502))
