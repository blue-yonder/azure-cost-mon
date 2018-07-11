import pytest
import responses

from prometheus_client import generate_latest, CollectorRegistry

from azure_costs_exporter.reserved_vm_collector import AzureReservedVMCollector


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


@pytest.fixture()
def single_order():
    responses.add(
        method='GET',
        url='https://management.azure.com/providers/Microsoft.Capacity/reservationOrders?api-version=2017-11-01',
        match_querystring=True,
        json={'value': [
            {
                'name': 'SINGLE_ORDER'
            }
        ]})


@pytest.fixture()
def reservation():
    """
    Standard reservation with default parameters that all following tests use to some extent 
    """
    return {
        "sku": {"name": "SIZE"},
        "location": "WESTEUROPE",
        "properties": {
            "quantity": 42,
            "appliedScopes": [
                "/subscriptions/SOME_SUBSCRIPTION"
            ],
            "appliedScopeType": "Single",
            "provisioningState": "Succeeded",
            "effectiveDateTime": "2018-01-01T00:00:00.000000Z",
            "expiryDate": "2019-01-01"}
    }


@responses.activate
def test_base_reservation(enable_login, single_order, reservation):
    responses.add(
        method='GET',
        url='https://management.azure.com/providers/Microsoft.Capacity/reservationOrders/SINGLE_ORDER/reservations?api-version=2017-11-01',
        match_querystring=True,
        json={'value': [reservation]})

    registry = CollectorRegistry()
    c = AzureReservedVMCollector('app_id', 'app_secret', 'tenant_id', 'SERIES_NAME')
    registry.register(c)

    result = generate_latest(registry).decode('utf8').split('\n')
    assert 'SERIES_NAME{duration="1-year",location="WESTEUROPE",subscription="SOME_SUBSCRIPTION",vm_size="SIZE"} 42.0' in result
    assert 'SERIES_NAME_next_expiration{duration="1-year",location="WESTEUROPE",subscription="SOME_SUBSCRIPTION",vm_size="SIZE"} 1546300800.0' in result


@responses.activate
def test_three_year_reservation(enable_login, single_order, reservation):
    reservation['properties']['effectiveDateTime'] = '2016-01-01T00:00:00.000000Z'
    responses.add(
        method='GET',
        url='https://management.azure.com/providers/Microsoft.Capacity/reservationOrders/SINGLE_ORDER/reservations?api-version=2017-11-01',
        match_querystring=True,
        json={'value': [reservation]})

    registry = CollectorRegistry()
    c = AzureReservedVMCollector('app_id', 'app_secret', 'tenant_id', 'SERIES_NAME')
    registry.register(c)

    result = generate_latest(registry).decode('utf8').split('\n')
    assert 'SERIES_NAME{duration="3-year",location="WESTEUROPE",subscription="SOME_SUBSCRIPTION",vm_size="SIZE"} 42.0' in result
    assert 'SERIES_NAME_next_expiration{duration="3-year",location="WESTEUROPE",subscription="SOME_SUBSCRIPTION",vm_size="SIZE"} 1546300800.0' in result


@responses.activate
def test_shared_reservation(enable_login, single_order, reservation):
    reservation['properties']['appliedScopeType'] = 'Shared'
    responses.add(
        method='GET',
        url='https://management.azure.com/providers/Microsoft.Capacity/reservationOrders/SINGLE_ORDER/reservations?api-version=2017-11-01',
        match_querystring=True,
        json={'value': [reservation]})

    registry = CollectorRegistry()
    c = AzureReservedVMCollector('app_id', 'app_secret', 'tenant_id', 'SERIES_NAME')
    registry.register(c)

    result = generate_latest(registry).decode('utf8').split('\n')
    assert 'SERIES_NAME{duration="1-year",location="WESTEUROPE",subscription="shared",vm_size="SIZE"} 42.0' in result
    assert 'SERIES_NAME_next_expiration{duration="1-year",location="WESTEUROPE",subscription="shared",vm_size="SIZE"} 1546300800.0' in result


@responses.activate
def test_expired_reservation(enable_login, single_order, reservation):
    reservation['properties']['provisioningState'] = 'Canceled'
    responses.add(
        method='GET',
        url='https://management.azure.com/providers/Microsoft.Capacity/reservationOrders/SINGLE_ORDER/reservations?api-version=2017-11-01',
        match_querystring=True,
        json={'value': [reservation]})

    registry = CollectorRegistry()
    c = AzureReservedVMCollector('app_id', 'app_secret', 'tenant_id', 'SERIES_NAME')
    registry.register(c)

    result = generate_latest(registry).decode('utf8').split('\n')
    assert 'SERIES_NAME{duration="1-year",location="WESTEUROPE",subscription="shared",vm_size="SIZE"} 42.0' not in result
    assert 'SERIES_NAME_next_expiration{duration="1-year",location="WESTEUROPE",subscription="shared",vm_size="SIZE"} 1546300800.0' not in result
