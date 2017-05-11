from flask import Blueprint, current_app, Response, abort
from .scrape import query_metrics

bp = Blueprint('views', __name__)

@bp.route("/health")
def health():
    return 'ok'


@bp.route("/metrics", methods=['GET'])
def metrics():

    try:
        metrics = query_metrics(current_app.config['ENROLLMENT_NUMBER'],
                                current_app.config['BILLING_API_ACCESS_KEY'],
                                current_app.config.get('PROMETHEUS_METRIC_NAME', 'azure_costs')
                                )
    except Exception as e:
        abort(Response("Scrape failed: {}".format(e),
                       status=502)
              )

    return metrics, 200, {'Content-Type': 'text/plain; charset=utf-8'}