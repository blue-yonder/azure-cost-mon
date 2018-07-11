import pytest
import responses

from prometheus_client import generate_latest, CollectorRegistry

from azure_costs_exporter.allocated_vm_collector import AzureAllocatedVMCollector


@pytest.fixture()
def enable_login():
    responses.add(
        method='POST',
        url='https://login.microsoftonline.com/tenant_id/oauth2/token',
        json={
            "token_type": "Bearer",
            "expires_in": "3600",
            "ext_expires_in": "0",
            "expires_on": "1861920000",
            "not_before": "1861920000",
            "resource": "https://management.core.windows.net/",
            "access_token": "XXXXXX"})
    # cannot check passed credentials with responses.

@responses.activate
def test_single_machine(enable_login):
    responses.add(
        method='GET',
        url='https://management.azure.com/subscriptions/SUBSCRIPTION_ID/providers/Microsoft.Compute/virtualMachines?api-version=2017-03-30',
        match_querystring=True,
        json={'value': [
            {
                'id': '/subscriptions/SUBSCRIPTION_ID/resourceGroups/RESOURCE_GROUP/providers/Microsoft.Compute/virtualMachines/NAME',
                'location': 'WESTEUROPE',
                'properties': {'hardwareProfile': {'vmSize': 'SIZE'}}
            }
        ]})

    registry = CollectorRegistry()
    c = AzureAllocatedVMCollector('app_id', 'app_secret', 'tenant_id', ['SUBSCRIPTION_ID'], 'SERIES_NAME')
    registry.register(c)

    result = generate_latest(registry).decode('utf8').split('\n')
    assert 'SERIES_NAME{location="WESTEUROPE",resource_group="RESOURCE_GROUP",subscription="SUBSCRIPTION_ID",vm_size="SIZE"} 1.0' in result


@responses.activate
def test_multiple_machines_in_multiple_subscriptions(enable_login):
    responses.add(
        method='GET',
        url='https://management.azure.com/subscriptions/SUBSCRIPTION_A/providers/Microsoft.Compute/virtualMachines?api-version=2017-03-30',
        match_querystring=True,
        json={'value': [
            {
                'id': '/subscriptions/SUBSCRIPTION_A/resourceGroups/RESOURCE_GROUP/providers/Microsoft.Compute/virtualMachines/NAME',
                'location': 'WESTEUROPE',
                'properties': {'hardwareProfile': {'vmSize': 'SIZE'}}
            }
        ]})
    responses.add(
        method='GET',
        url='https://management.azure.com/subscriptions/SUBSCRIPTION_B/providers/Microsoft.Compute/virtualMachines?api-version=2017-03-30',
        match_querystring=True,
        json={'value': [
            {
                'id': '/subscriptions/SUBSCRIPTION_B/resourceGroups/RESOURCE_GROUP/providers/Microsoft.Compute/virtualMachines/NAME',
                'location': 'WESTEUROPE',
                'properties': {'hardwareProfile': {'vmSize': 'SIZE'}}
            }
        ]})

    registry = CollectorRegistry()
    c = AzureAllocatedVMCollector('app_id', 'app_secret', 'tenant_id', ['SUBSCRIPTION_A', 'SUBSCRIPTION_B'], 'SERIES_NAME')
    registry.register(c)

    result = generate_latest(registry).decode('utf8').split('\n')
    assert 'SERIES_NAME{location="WESTEUROPE",resource_group="RESOURCE_GROUP",subscription="SUBSCRIPTION_A",vm_size="SIZE"} 1.0' in result
    assert 'SERIES_NAME{location="WESTEUROPE",resource_group="RESOURCE_GROUP",subscription="SUBSCRIPTION_B",vm_size="SIZE"} 1.0' in result


@responses.activate
def test_multiple_machines_in_single_subscription(enable_login):
    responses.add(
        method='GET',
        url='https://management.azure.com/subscriptions/SUBSCRIPTION_A/providers/Microsoft.Compute/virtualMachines?api-version=2017-03-30',
        match_querystring=True,
        json={'value': [
            {   # Reference machine
                'id': '/subscriptions/SUBSCRIPTION_A/resourceGroups/RESOURCE_GROUP/providers/Microsoft.Compute/virtualMachines/NAME_1',
                'location': 'WESTEUROPE',
                'properties': {'hardwareProfile': {'vmSize': 'SIZE'}}
            },
            {   # Different region
                'id': '/subscriptions/SUBSCRIPTION_A/resourceGroups/RESOURCE_GROUP/providers/Microsoft.Compute/virtualMachines/NAME_2',
                'location': 'OTHER REGION',
                'properties': {'hardwareProfile': {'vmSize': 'SIZE'}}
            },
            {   # Other size
                'id': '/subscriptions/SUBSCRIPTION_A/resourceGroups/RESOURCE_GROUP/providers/Microsoft.Compute/virtualMachines/NAME_3',
                'location': 'WESTEUROPE',
                'properties': {'hardwareProfile': {'vmSize': 'OTHER SIZE'}}
            },
            {   # Other resource group
                'id': '/subscriptions/SUBSCRIPTION_A/resourceGroups/OTHER_RESOURCE_GROUP/providers/Microsoft.Compute/virtualMachines/NAME_4',
                'location': 'WESTEUROPE',
                'properties': {'hardwareProfile': {'vmSize': 'SIZE'}}
            },
            {   # Second machine, just differs in name
                'id': '/subscriptions/SUBSCRIPTION_A/resourceGroups/RESOURCE_GROUP/providers/Microsoft.Compute/virtualMachines/NAME_5',
                'location': 'WESTEUROPE',
                'properties': {'hardwareProfile': {'vmSize': 'SIZE'}}
            }
        ]})

    registry = CollectorRegistry()
    c = AzureAllocatedVMCollector('app_id', 'app_secret', 'tenant_id', ['SUBSCRIPTION_A'], 'SERIES_NAME')
    registry.register(c)

    result = generate_latest(registry).decode('utf8').split('\n')

    # Machines with different parameters -> count = 1
    assert 'SERIES_NAME{location="OTHER REGION",resource_group="RESOURCE_GROUP",subscription="SUBSCRIPTION_A",vm_size="SIZE"} 1.0' in result
    assert 'SERIES_NAME{location="WESTEUROPE",resource_group="OTHER_RESOURCE_GROUP",subscription="SUBSCRIPTION_A",vm_size="SIZE"} 1.0' in result
    assert 'SERIES_NAME{location="WESTEUROPE",resource_group="RESOURCE_GROUP",subscription="SUBSCRIPTION_A",vm_size="OTHER SIZE"} 1.0' in result

    # All parameters match -> count = 2
    assert 'SERIES_NAME{location="WESTEUROPE",resource_group="RESOURCE_GROUP",subscription="SUBSCRIPTION_A",vm_size="SIZE"} 2.0' in result
