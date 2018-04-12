from prometheus_client.core import GaugeMetricFamily

from pandas import DataFrame

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient


_BASE_COLUMNS = ['subscription', 'location', 'resource_group', 'vm_size']
_COUNT_COLUMN = ['total']
_ALL_COLUMNS = _BASE_COLUMNS + _COUNT_COLUMN


def _extract_resource_group(vm_id):
    return vm_id.split('/')[4]

class AzureAllocatedVMCollector(object):
    """
    Class to export information about allocated Azure virtual machines 
    in Prometheus compatible format.
    """

    def __init__(self, application_id, application_secret, tenant_id, subscription_ids, metric_name):
        """
        Constructor.
        
        :param metric_name: Name of the timeseries
        :param timeout: Timeout to use for the request against the EA portal
        """
        self._metric_name = metric_name
        self._subscription_ids = subscription_ids
        self._credentials = ServicePrincipalCredentials(client_id=application_id,
                                                        secret=application_secret,
                                                        tenant=tenant_id)

    def _create_gauge(self):
        """
        Create a gauge instance.

        :return: prometheus_client gauge instance
        """
        description = "Number of virtual machines per Azure subscription, location, resource group, and vm size"
        allocated_vms = GaugeMetricFamily(self._metric_name, description, labels=_BASE_COLUMNS)
        return allocated_vms

    def _collect_allocated_vms(self, allocated_vms):
        rows = []

        for subscription_id in self._subscription_ids:
            compute_client = ComputeManagementClient(self._credentials, subscription_id)
            for vm in compute_client.virtual_machines.list_all():
                rows.append([subscription_id,
                             vm.location,
                             _extract_resource_group(vm.id),
                             vm.hardware_profile.vm_size,
                             1])

        df = DataFrame(data=rows, columns=_ALL_COLUMNS)

        groups = df.groupby(_BASE_COLUMNS).sum()

        for name, value in groups.iterrows():
            allocated_vms.add_metric(name, int(value.total))

    def describe(self):
        """
        Default registry calls "collect" if "describe" is not existent to determine timeseries names.
        We do not want that to avoid pointless Azure API calls.

        :return: The metrics we are collecting.
        """
        return [self._create_gauge()]

    def collect(self):
        """
        Yield the metrics.
        """
        allocated_vms = self._create_gauge()
        self._collect_allocated_vms(allocated_vms)

        yield allocated_vms
