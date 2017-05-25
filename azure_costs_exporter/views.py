from flask import Blueprint, current_app, Response, abort
from prometheus_client import generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST
from .scrape import query_metrics

bp = Blueprint('views', __name__)

@bp.route("/health")
def health():
    return 'ok'


@bp.route("/metrics", methods=['GET'])
def metrics():

    registry = CollectorRegistry()

    try:
        query_metrics(registry,
                      current_app.config['ENROLLMENT_NUMBER'],
                      current_app.config['BILLING_API_ACCESS_KEY'],
                      current_app.config.get('PROMETHEUS_METRIC_NAME', 'azure_costs')
                                )
    except Exception as e:
        abort(Response("Scrape failed: {}".format(e),
                       status=502)
              )

    content = generate_latest(registry)

    return content, 200, {'Content-Type': CONTENT_TYPE_LATEST}