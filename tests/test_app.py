import datetime

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


@pytest.fixture
def app():
    import os
    return create_app(os.path.join(os.getcwd(), "application.cfg"))


@pytest.fixture
def client():
    application = app()
    return application.test_client()


@pytest.fixture
def now():
    return datetime.datetime.now().strftime('%Y-%m')


@responses.activate
def test_configured_token_passed_to_billing_collector(client, now, enrollment, access_key):

    responses.add(
        method='GET',
        url="https://ea.azure.com/rest/{0}/usage-report?month={1}&type=detail&fmt=Json".format(enrollment, now),
        match_querystring=True,
        json=sample_data
    )

    assert client.get('/metrics').status_code == 200
    assert responses.calls[-1].request.headers['Authorization'] == "Bearer {}".format(access_key)


@pytest.mark.parametrize('timeout,expected', [('42.3', 42.3), (None, DEFAULT_SCRAPE_TIMEOUT)])
def test_ea_billing_metrics(app, access_key, now, enrollment, timeout, expected):
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

        rsp = app.test_client().get('/metrics', headers=headers)
        url = 'https://ea.azure.com/rest/{enrollment}/usage-report?month={month}&type=detail&fmt=Json'
        url = url.format(enrollment=enrollment, month=now)
        assert rsp.status_code == 200
        assert rsp.data.count(b'azure_costs_eur') == 4


def test_failing_target(client):
    with mock.patch("azure_costs_exporter.enterprise_billing_collector.AzureEABillingCollector.collect",
                    side_effect=requests.HTTPError()):
        rsp = client.get('/metrics')

        assert rsp.status_code == 502
        assert rsp.data.startswith(b'Scrape failed')


def test_health(client):
    rsp = client.get('/health')
    assert rsp.data == b'ok'
