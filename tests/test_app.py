import datetime
import os

import pytest
import responses
import requests
import mock

from azure_costs_exporter.main import create_app
from azure_costs_exporter.views import DEFAULT_SCRAPE_TIMEOUT
from .data import sample_data, api_output_for_empty_months


@pytest.fixture
def enrollment():
    return '31415'


@pytest.fixture
def access_key():
    return '3408795poitwiqeotu934t5pqweiut'


def get_client(configuration_name):
    path = os.path.join(os.getcwd(), 'tests', 'configuration_files', '{}.cfg'.format(configuration_name))
    application = create_app(path)
    return application.test_client()


@pytest.fixture
def now():
    return datetime.datetime.now().strftime('%Y-%m')


@responses.activate
def test_configured_token_passed_to_billing_collector(now, enrollment, access_key):
    client = get_client('only_ea_billing')
    responses.add(
        method='GET',
        url="https://ea.azure.com/rest/{0}/usage-report?month={1}&type=detail&fmt=Json".format(enrollment, now),
        match_querystring=True,
        json=sample_data
    )

    assert client.get('/metrics').status_code == 200
    assert responses.calls[-1].request.headers['Authorization'] == "Bearer {}".format(access_key)


@pytest.mark.parametrize('timeout,expected', [('42.3', 42.3), (None, DEFAULT_SCRAPE_TIMEOUT)])
def test_ea_billing_metrics(access_key, now, enrollment, timeout, expected):
    class RequestsMock(responses.RequestsMock):
        def get(self, *args, **kwargs):
            assert kwargs['timeout'] == expected
            return super(RequestsMock, self).get(*args, **kwargs)

    with RequestsMock() as resp:
        resp.add(
            method='GET',
            url="https://ea.azure.com/rest/{0}/usage-report?month={1}&type=detail&fmt=Json".format(enrollment, now),
            match_querystring=True,
            json=sample_data
        )

        headers = {}
        if timeout is not None:
            headers = {'X-Prometheus-Scrape-Timeout-Seconds': timeout}

        rsp = get_client('only_ea_billing').get('/metrics', headers=headers)
        assert rsp.status_code == 200
        assert rsp.data.count(b'azure_costs_eur') == 4


def test_failing_target():
    with mock.patch(
            "azure_costs_exporter.enterprise_billing_collector.AzureEABillingCollector.collect",
            side_effect=requests.HTTPError()):
        rsp = get_client('only_ea_billing').get('/metrics')

        assert rsp.status_code == 502
        assert rsp.data.startswith(b'Scrape failed')


@responses.activate
def test_allocated_vm_metrics():
    responses.add(
        method='POST',
        url='https://login.microsoftonline.com/tenant_id/oauth2/token',
        json={"token_type": "Bearer",
              "expires_in": "3600",
              "ext_expires_in": "0",
              "expires_on": "1861920000",
              "not_before": "1861920000",
              "resource": "https://management.core.windows.net/",
              "access_token": "XXXXXX"})
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

    rsp = get_client('only_allocated_vm').get('/metrics')
    assert rsp.status_code == 200
    assert rsp.data.count(b'AZURE_ALLOCATED_VMS') >= 3


@responses.activate
def test_reserved_vm_metrics():
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
    responses.add(
        method='GET',
        url='https://management.azure.com/providers/Microsoft.Capacity/reservationOrders?api-version=2017-11-01',
        match_querystring=True,
        json={'value': []})  # no reservations sufficient for this test

    rsp = get_client('only_reserved_vm').get('/metrics')
    assert rsp.status_code == 200
    assert rsp.data.count(b'AZURE_RESERVED_VMS') >= 4


def test_health():
    rsp = get_client('only_ea_billing').get('/health')
    assert rsp.data == b'ok'
