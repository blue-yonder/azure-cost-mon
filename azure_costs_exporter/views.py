from flask import Blueprint, Response, abort
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

bp = Blueprint('views', __name__)

@bp.route("/health")
def health():
    return 'ok'


@bp.route("/metrics")
def metrics():
    try:
        content = generate_latest()
        return content, 200, {'Content-Type': CONTENT_TYPE_LATEST}
    except Exception as e:
        abort(Response("Scrape failed: {}".format(e), status=502))
