import datetime

import pytest
import responses
from mock import MagicMock

import azure_costs_exporter
from azure_costs_exporter.main import create_app
from .data import sample_data


@pytest.fixture
def enrollment():
    return '31415'


@pytest.fixture
def access_key():
    return '3408795poitwiqeotu934t5pqweiut'


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def client():
    application = app()
    return application.test_client()


@pytest.fixture
def now():
    return datetime.datetime.now().strftime('%Y-%m')


@responses.activate
def test_token(client, now, enrollment, access_key):

    responses.add(
        method='GET',
        url="https://ea.azure.com/rest/{0}/usage-report?month={1}&type=detail&fmt=Json".format(enrollment, now),
        match_querystring=True,
        json=sample_data
    )

    assert client.get('/metrics').status_code == 200
    assert responses.calls[-1].request.headers['Authorization'] == "Bearer {}".format(access_key)


@responses.activate
def test_metrics(app, now, enrollment):
    
    responses.add(
        method='GET',
        url="https://ea.azure.com/rest/{0}/usage-report?month={1}&type=detail&fmt=Json".format(enrollment, now),
        match_querystring=True,
        json=sample_data
    )

    rsp = app.test_client().get('/metrics')
    assert rsp.status_code == 200
    assert rsp.data.count(b'azure_costs_eur') == 4


@responses.activate
def test_metrics_timeout(monkeypatch, app, access_key, now, enrollment):
    get_mock = MagicMock()
    monkeypatch.setattr(azure_costs_exporter.prometheus_collector.requests,
                        'get',
                        get_mock)

    rsp = app.test_client().get('/metrics', headers={'Scrape-Timeout-Seconds': 42.0})
    url = 'https://ea.azure.com/rest/{enrollment}/usage-report?month={month}&type=detail&fmt=Json'
    url = url.format(enrollment=enrollment, month=now)

    get_mock.assert_called_once_with(
        url,
        headers={'Authorization': 'Bearer {}'.format(access_key)},
        timeout=42
    )
    assert rsp.status_code == 200


@responses.activate
@pytest.mark.parametrize('status', [500, 400])
def test_failing_target(client, now, status):
    responses.add(
        method='GET',
        url="https://ea.azure.com/rest/{0}/usage-report?month={1}&type=detail&fmt=Json".format(enrollment, now),
        match_querystring=True,
        status=status
    )

    rsp = client.get('/metrics')

    assert rsp.status_code == 502
    assert rsp.data.startswith(b'Scrape failed')


def test_health(client):
    rsp = client.get('/health')
    assert rsp.data == b'ok'
