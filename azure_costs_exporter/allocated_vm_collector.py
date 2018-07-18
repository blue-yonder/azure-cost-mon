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
        Constructor. Access is granted to what Microsoft calls a service principal / Azure Active Directory
        Application / app registration. Read more about this topic at
        https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-create-service-principal-portal.
        This page will guide you how to obtain an application_id, and application_secret, and the tenant_id of
        your Azure Active Directory. Please do not forget to grant "Reader" permissions to the app for all
        subscriptions that you want to monitor.
        
        :param application_id: The application ID that is created during the Azure app registration.
        :param application_secret: The application secret that is created during the Azure app registration.
        :param tenant_id: The ID of your Azure Active Directory instance
        :param subscription_ids: A _sequence_ of subscription IDs that shall be monitored. The application_id
                                 required "Reader" permissions on each subscription.
        :param metric_name: Name of the timeseries
        """
        self._metric_name = metric_name
        self._subscription_ids = subscription_ids
        self._credentials = ServicePrincipalCredentials(
            client_id=application_id,
            secret=application_secret,
            tenant=tenant_id)

    def _create_gauge(self):
        description = "Number of virtual machines per Azure subscription, location, resource group, and vm size"
        allocated_vms = GaugeMetricFamily(self._metric_name, description, labels=_BASE_COLUMNS)
        return allocated_vms

    def _collect_allocated_vms(self, allocated_vms):
        rows = []

        for subscription_id in self._subscription_ids:
            compute_client = ComputeManagementClient(self._credentials, str(subscription_id))
            for vm in compute_client.virtual_machines.list_all():
                rows.append([
                    subscription_id,
                    vm.location,
                    _extract_resource_group(vm.id),
                    vm.hardware_profile.vm_size,
                    1])

        df = DataFrame(data=rows, columns=_ALL_COLUMNS)

        groups = df.groupby(_BASE_COLUMNS).sum()

        for labels, value in groups.iterrows():
            allocated_vms.add_metric(labels, int(value.total))

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
