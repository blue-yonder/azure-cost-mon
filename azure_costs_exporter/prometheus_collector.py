import requests
import datetime
from pandas import DataFrame
from prometheus_client.core import CounterMetricFamily

base_columns = ['DepartmentName', 'AccountName', 'SubscriptionName', 'MeterCategory',
                'MeterSubCategory', 'MeterName', 'ResourceGroup']
cost_column = ['ExtendedCost']


def convert_json_df(data):
    """
    Convert the API response (JSON document) to a data frame
    """
    columns = base_columns + cost_column
    content = list()
    for item in data:
        line = list()
        for c in columns:
            value = item[c]
            try:
                value = value.lower()
            except:
                pass

            line.append(value)

        content.append(line)

    df = DataFrame(data=content, columns=columns)

    return df


class AzureEABillingCollector(object):
    """
    Class to export Azure billing and usage information extracted via ea.azure.com 
    in Prometheus compatible format.
    """

    def __init__(self, metric_name, enrollment, token, timeout):
        """
        Constructor.
        
        :param metric_name: Name of the timeseries
        :param enrollment: ID of the enterprise agreement (EA)
        :param token: Access Key generated via the EA portal
        :param timeout: Timeout to use for the request against the EA portal
        """
        self._metric_name = metric_name
        self._enrollment = enrollment
        self._token = token
        self._timeout = timeout

    def _get_azure_data(self, month=None):
        """
        Request the billing data from the Azure API and return a dict with the data

        :param month: string for the given month or None for the current month
        :return: JSON document of usage and billing information for the given month
        """
        if month is None:
            now = datetime.datetime.now()
            month = now.strftime("%Y-%m")

        headers = {"Authorization": "Bearer {}".format(self._token)}
        url = "https://ea.azure.com/rest/{0}/usage-report?month={1}&type=detail&fmt=Json".format(self._enrollment,
                                                                                                 month)

        rsp = requests.get(url, headers=headers, timeout=self._timeout)
        rsp.raise_for_status()

        if rsp.text.startswith('"Usage Data Extract"'):
            # special treatement for no usage details. Azure API doesn't return a JSON document in that case...
            return dict()

        return rsp.json()

    def _create_counter(self):
        """
        Create a counter instance.
        
        :return: prometheus_client counter instance
        """
        description = "Costs billed to Azure Enterprise Agreement {}".format(self._enrollment)
        c = CounterMetricFamily(self._metric_name, description, labels=base_columns)
        return c

    def describe(self):
        """
        Default registry calls "collect" if "describe" is not existent to determine timeseries names. 
        Don't want that because it issues a request to the billing API.
            
        :return: The metrics we are collecting.
        """
        return [self._create_counter()]

    def collect(self):
        """
        Yield the metrics.
        """
        c = self._create_counter()

        usage_data = self._get_azure_data()
        df = convert_json_df(usage_data)
        groups = df.groupby(base_columns).sum()

        for name, value in groups.iterrows():
            c.add_metric(name, value.ExtendedCost)

        yield c
