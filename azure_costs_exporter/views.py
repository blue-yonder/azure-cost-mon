from flask import Blueprint, Response, abort, current_app, request
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, generate_latest

from .enterprise_billing_collector import AzureEABillingCollector
from .allocated_vm_collector import AzureAllocatedVMCollector
from .reserved_vm_collector import AzureReservedVMCollector


bp = Blueprint('views', __name__)
DEFAULT_SCRAPE_TIMEOUT = 10


def _get_timeout():
    try:
        return float(request.headers.get('X-Prometheus-Scrape-Timeout-Seconds')) 
    except Exception:
        return current_app.config.get('BILLING_SCRAPE_TIMEOUT', DEFAULT_SCRAPE_TIMEOUT)


def _register_billing_collector(registry):
    timeout = _get_timeout()
    collector = AzureEABillingCollector(
        current_app.config['BILLING_METRIC_NAME'],
        current_app.config['ENROLLMENT_NUMBER'],
        current_app.config['BILLING_API_ACCESS_KEY'],
        timeout
    )
    registry.register(collector)


def _register_allocated_vm_collector(registry):
    collector = AzureAllocatedVMCollector(
        current_app.config['APPLICATION_ID'],
        current_app.config['APPLICATION_SECRET'],
        current_app.config['AD_TENANT_ID'],
        current_app.config['SUBSCRIPTION_IDS'],
        current_app.config['ALLOCATED_VM_METRIC_NAME'],
    )
    registry.register(collector)


def _register_reserved_vm_collector(registry):
    collector = AzureReservedVMCollector(
        current_app.config['APPLICATION_ID'],
        current_app.config['APPLICATION_SECRET'],
        current_app.config['AD_TENANT_ID'],
        current_app.config['RESERVED_VM_METRIC_NAME'],
    )
    registry.register(collector)


def _register_collectors(registry):
    if 'BILLING_METRIC_NAME' in current_app.config:
        _register_billing_collector(registry)
    if 'ALLOCATED_VM_METRIC_NAME' in current_app.config:
        _register_allocated_vm_collector(registry)
    if 'RESERVED_VM_METRIC_NAME' in current_app.config:
        _register_reserved_vm_collector(registry)


@bp.route("/health")
def health():
    return 'ok'


@bp.route("/metrics")
def metrics():
    registry = CollectorRegistry()
    _register_collectors(registry)

    try:
        content = generate_latest(registry)
        return content, 200, {'Content-Type': CONTENT_TYPE_LATEST}
    except Exception as e:
        abort(Response("Scrape failed: {}".format(e), status=502))
