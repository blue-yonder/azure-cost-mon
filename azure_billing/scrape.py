import requests
import datetime
from pandas import DataFrame

from .metrics import Counter

base_columns = ['DepartmentName', 'AccountName', 'SubscriptionName', 'MeterCategory', 
                'MeterSubCategory', 'MeterName', 'ResourceGroup']
cost_column = ['ExtendedCost']

def get_azure_data(enrollment, token, month):
    """
    Request the billing data from the Azure API and return a dict with the data
    """

    headers = {"Authorization":"Bearer {}".format(token)}
    url = "https://ea.azure.com/rest/{0}/usage-report?month={1}&type=detail&fmt=Json".format(enrollment, month)

    rsp = requests.get(url, headers=headers, timeout=10)
    rsp.raise_for_status()
    
    return rsp.json()


def current_month():
    """
    Return the current month in the format YYYY-MM
    """
    now = datetime.datetime.now()
    return now.strftime("%Y-%m")


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

def extract_metrics_from_df(df, counter):
    """
    Fill a counter object with the data from the data frame
    """
    groups = df.groupby(base_columns).sum()
    for name, value in groups.iterrows():
        meta = dict(zip(base_columns, name))
        counter.record(value.ExtendedCost, **meta)


def query_metrics(enrollment, token, metric_name, month=None):
    """
    Create and return the prometheus compatible output for the billing information
    """
    if month is None:
        month = current_month()

    raw = get_azure_data(enrollment, token, month)

    df = convert_json_df(raw)

    c = Counter(metric_name, "Costs billed to Azure Enterprise Agreement {}".format(enrollment))

    extract_metrics_from_df(df, c)

    return c.serialize()
