import pytest, responses
import datetime
from prometheus_client import generate_latest, CollectorRegistry

from azure_costs_exporter.scrape import current_month, convert_json_df, extract_metrics_from_df
from azure_costs_exporter.scrape import base_columns, cost_column, get_azure_data, query_metrics

from .data import sample_data


def test_month():
    now = datetime.datetime.now()
    assert current_month() == now.strftime("%Y-%m")


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


def test_extract_metrics():
    df = convert_json_df(sample_data)
    registry = CollectorRegistry()
    extract_metrics_from_df(df, 'costs', '123', registry)

    result = generate_latest(registry).decode('utf8').split('\n')
    assert len(result) == 5

    expected_0 = 'costs{AccountName="platform",DepartmentName="engineering",MeterCategory="virtual network",MeterName="hours",MeterSubCategory="gateway hour",ResourceGroup="",SubscriptionName="production"} 0.71'
    expected_1 = 'costs{AccountName="platform",DepartmentName="engineering",MeterCategory="windows azure storage",MeterName="standard io - page blob/disk (gb)",MeterSubCategory="locally redundant",ResourceGroup="my-group",SubscriptionName="production"} 0.24'

    assert result[2] == expected_0
    assert result[3] == expected_1


@responses.activate
def test_get_azure_data():

    enrollment='12345'

    responses.add(
        method='GET',
        url="https://ea.azure.com/rest/{}/usage-report?month=2017-03&type=detail&fmt=Json".format(enrollment),
        match_querystring=True,
        json=sample_data
    )

    data = get_azure_data(enrollment, 'abc123xyz', '2017-03')
    assert data == sample_data


@responses.activate
def test_data():

    enrollment='12345'
    access_key='abc123xyz'
    metric_name = 'cloud_costs'

    responses.add(
        method='GET',
        url="https://ea.azure.com/rest/{}/usage-report?month=2017-03&type=detail&fmt=Json".format(enrollment),
        match_querystring=True,
        json=sample_data
    )
    registry = CollectorRegistry()
    query_metrics(registry, enrollment, access_key, metric_name, month='2017-03')

    prom_data = generate_latest(registry)

    assert prom_data.decode('utf8').count(metric_name) == 4
