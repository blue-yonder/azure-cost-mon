import pytest, responses
import datetime
from prometheus_client import generate_latest, CollectorRegistry

from azure_costs_exporter.prometheus_collector import convert_json_df, AzureEABillingCollector
from azure_costs_exporter.prometheus_collector import base_columns, cost_column

from .data import sample_data, api_output_for_empty_months


def current_month():
     now = datetime.datetime.now()
     return now.strftime("%Y-%m")


@pytest.fixture()
def enrollment():
    return '1234567'


@pytest.fixture()
def api_url():
    base_url = "https://ea.azure.com/rest/{}/usage-report".format(enrollment())
    params = "?month={}&type=detail&fmt=Json".format(current_month())
    return base_url + params


def test_df_conversion():
    df = convert_json_df(sample_data)

    assert df.columns.size == len(base_columns) + len(cost_column)
    assert len(df) == len(sample_data)


def test_df_missing_column():
    with pytest.raises(KeyError):
        df = convert_json_df([dict(AccountName='foo',
                                   ConsumedService='bar',
                                   SubscriptionName='baz',
                                   ExtendedCost=1.2)])


@responses.activate
def test_extract_metrics(api_url, enrollment):

    responses.add(
        method='GET',
        url=api_url,
        match_querystring=True,
        json=sample_data
    )

    registry = CollectorRegistry()
    c = AzureEABillingCollector('costs', enrollment, 'ab123xy', 10)
    registry.register(c)

    result = generate_latest(registry).decode('utf8').split('\n')
    assert len(result) == 5

    expected_0 = 'costs{AccountName="platform",DepartmentName="engineering",MeterCategory="virtual network",MeterName="hours",MeterSubCategory="gateway hour",ResourceGroup="",SubscriptionName="production"} 0.0'
    expected_1 = 'costs{AccountName="platform",DepartmentName="engineering",MeterCategory="windows azure storage",MeterName="standard io - page blob/disk (gb)",MeterSubCategory="locally redundant",ResourceGroup="my-group",SubscriptionName="production"} 1.0'

    assert result[2] == expected_0
    assert result[3] == expected_1


@responses.activate
def test_get_azure_data(api_url, enrollment):

    c = AzureEABillingCollector('cloud_costs', enrollment, 'abc123xyz', 42.3)

    responses.add(
        method='GET',
        url=api_url,
        match_querystring=True,
        json=sample_data
    )

    data = c._get_azure_data(current_month())
    assert data == sample_data


@responses.activate
def test_empty_month(api_url, enrollment):
    """
    If no usage details have are available for a given month the API does not return a JSON document.    
    """
    c = AzureEABillingCollector('cloud_costs', enrollment, 'abc123xyz', 11)

    responses.add(
        method='GET',
        url=api_url,
        match_querystring=True,
        body=api_output_for_empty_months
    )

    data = c._get_azure_data(current_month())
    assert data == dict()
