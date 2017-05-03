import pytest
import responses
import datetime

from azure_billing import app
from .data import sample_data


@pytest.fixture
def enrollment():
    return '12345'


@pytest.fixture
def token():
    return 'abc123xyz'


@pytest.fixture
def client():
    app.config['ENROLLMENT'] = enrollment()
    app.config['TOKEN'] = '123'#token()
    return app.test_client()


@pytest.fixture
def now():
    return datetime.datetime.now().strftime('%Y-%m')


@responses.activate
def test_token(client, now, enrollment, token):
    responses.add(
        method='GET',
        adding_headers={"Authorization":"Bearer {}".format(token)},
        url="https://ea.azure.com/rest/{0}/usage-report?month={1}&type=detail&fmt=Json".format(enrollment, now),
        match_querystring=True,
        json=sample_data
    )
    #TODO this test should fail
    rsp = client.get('/metrics')
    assert rsp.status_code == 200


@responses.activate
def test_metrics(client, now, enrollment):
    
    responses.add(
        method='GET',
        url="https://ea.azure.com/rest/{0}/usage-report?month={1}&type=detail&fmt=Json".format(enrollment, now),
        match_querystring=True,
        json=sample_data
    )
    metric_name = b'my_costs'
    app.config['METRIC_NAME'] = metric_name

    rsp = client.get('/metrics')
    assert rsp.status_code == 200
    assert rsp.data.count(metric_name) == 4


@responses.activate
def test_metrics_name_default_value(client, now, enrollment):
    responses.add(
        method='GET',
        url="https://ea.azure.com/rest/{0}/usage-report?month={1}&type=detail&fmt=Json".format(enrollment, now),
        match_querystring=True,
        json=sample_data
    )
    #make sure that app.config is empty
    try:
        del app.config['METRIC_NAME']
    except KeyError:
        pass

    rsp = client.get('/metrics')
    assert rsp.status_code == 200
    assert rsp.data.count(b"azure_costs") == 4


@responses.activate
def test_failing_target(client, now):
    responses.add(
        method='GET',
        url="https://ea.azure.com/rest/{0}/usage-report?month={1}&type=detail&fmt=Json".format(enrollment, now),
        match_querystring=True,
        status=500
    )

    rsp = client.get('/metrics')

    assert rsp.status_code == 502
    assert rsp.data.startswith(b'Scrape failed')

    responses.add(
        method='GET',
        url="https://ea.azure.com/rest/{0}/usage-report?month={1}&type=detail&fmt=Json".format(enrollment, now),
        match_querystring=True,
        status=400
    )

    rsp = client.get('/metrics')

    assert rsp.status_code == 502
    assert rsp.data.startswith(b'Scrape failed')




def test_health(client):
    rsp = client.get('/health')
    assert rsp.data == b'ok'
