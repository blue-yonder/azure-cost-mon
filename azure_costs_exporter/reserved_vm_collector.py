import datetime

from prometheus_client.core import GaugeMetricFamily

from pandas import DataFrame

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.reservations import AzureReservationAPI


_BASE_COLUMNS = ['subscription', 'location', 'vm_size', 'duration']
_COUNT_COLUMN = ['total']
_EXPIRES_COLUMNS = ['next_expiration']
_ALL_COLUMNS = _BASE_COLUMNS + _COUNT_COLUMN
_EPOCH = datetime.date(1970, 1, 1)

def _extract_subscription_id(properties):
    if properties.applied_scope_type != "Shared":
        return properties.applied_scopes[0].split('/')[-1]
    else:
        return "shared"


class AzureReservedVMCollector(object):
    """
    Class to export information about reserved Azure virtual machines 
    in Prometheus compatible format.
    """

    def __init__(self, application_id, application_secret, tenant_id, metric_name):
        """
        Constructor. Access is granted to what Microsoft calls a service principal / Azure Active Directory
        Application / app registration. Read more about this topic at
        https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-create-service-principal-portal.
        This page will guide you how to obtain an application_id, and application_secret, and the tenant_id of
        your Azure Active Directory.
        
        In addition, the application requires "Reader" permissions on _each individual_ reservation _order_ to be
        able to retrieve the information of the actual reservations within the reservation orders.
        
        :param application_id: The application ID that is created during the Azure app registration.
        :param application_secret: The application secret that is created during the Azure app registration.
        :param tenant_id: The ID of your Azure Active Directory instance
        :param metric_name: Name of the timeseries
        """
        self._metric_name = metric_name
        self._credentials = ServicePrincipalCredentials(client_id=application_id,
                                                        secret=application_secret,
                                                        tenant=tenant_id)

    def _create_gauges(self):
        reserved_vms = GaugeMetricFamily(
            self._metric_name,
            "Number of reserved virtual machines per Azure subscription, location, duration, and vm size",
            labels=_BASE_COLUMNS)
        expirations = GaugeMetricFamily(
            self._metric_name + "_next_expiration",
            "Timestamp of the next expiration of a virtual machine reservation of certain location, size, duration, and subscription",
            labels=_BASE_COLUMNS)
        return reserved_vms, expirations

    def _collect_reserved_vms(self, reserved_vms, expirations):
        rows = []

        reservations = AzureReservationAPI(self._credentials)

        for order in reservations.reservation_order.list():
            for r in reservations.reservation.list(order.name):
                if r.properties.provisioning_state.upper() == "SUCCEEDED":
                    rows.append([
                        _extract_subscription_id(r.properties),
                        r.location,
                        r.sku.name,
                        "{}-year".format(int((r.properties.expiry_date - r.properties.effective_date_time.date()).days / 365)),
                        r.properties.quantity,
                        (r.properties.expiry_date - _EPOCH).total_seconds()])
        df = DataFrame(data=rows, columns=_BASE_COLUMNS + _COUNT_COLUMN + _EXPIRES_COLUMNS)

        groups = df.groupby(_BASE_COLUMNS).sum()
        for labels, value in groups.iterrows():
            reserved_vms.add_metric(labels, int(value.total))

        groups = df.groupby(_BASE_COLUMNS).min()
        for labels, value in groups.iterrows():
            expirations.add_metric(labels, int(value.next_expiration))


    def describe(self):
        """
        Default registry calls "collect" if "describe" is not existent to determine timeseries names.
        We do not want that to avoid pointless Azure API calls.

        :return: The metrics we are collecting.
        """
        return self._create_gauges()

    def collect(self):
        """
        Yield the metrics.
        """
        reserved_vms, expirations = self._create_gauges()
        self._collect_reserved_vms(reserved_vms, expirations)

        yield reserved_vms
        yield expirations
