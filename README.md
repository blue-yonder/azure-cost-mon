[![Build Status](https://travis-ci.org/blue-yonder/azure-cost-mon.svg?branch=master)](https://travis-ci.org/blue-yonder/azure-cost-mon)
[![Coverage Status](https://coveralls.io/repos/github/blue-yonder/azure-cost-mon/badge.svg?branch=master)](https://coveralls.io/github/blue-yonder/azure-cost-mon?branch=master)
[![PyPI version](https://badge.fury.io/py/azure-costs-exporter.svg)](https://badge.fury.io/py/azure-costs-exporter)

ACE azure-costs-exporter
========================

Prometheus exporter for the Microsoft Azure billing API. Check out
[this blog post](https://tech.blue-yonder.com/public-cloud-cost-control/) for
more background about the idea and some nice screenshots.

Description
-----------

**azure-costs-exporter** is a web app, that is intended to be called by [Prometheus](https://prometheus.io) to export billing information from Azure. It will then return the available metrics in Prometheus compatible format.

The billing API in use is part of the "Enterprise Agreement (EA)" Portal. Hence, it is not available for pay-as-you-go 
subscriptions. The configuration requires an active EA with Microsoft.

Configuration
-------------

You need to create an `application.cfg` file with the following content:

    ENROLLMENT_NUMBER="123456"
    BILLING_API_ACCESS_KEY="XXX"
    PROMETHEUS_METRIC_NAME="my_metric_name"

- `ENROLLMENT_NUMBER` is the unique ID that identifies a particular EA.
- The `BILLING_API_ACCESS_KEY` can be created in the [EA portal](https://ea.azure.com/) to gain
access to the billing API. Navigate to "Reports > Download Usage" and generate an API Access Key.
- `PROMETHEUS_METRIC_NAME` is the name of the time series that will be generated in Prometheus.

Deployment
----------

E.g. via `gunicorn`. In an activated `virtualenv`, you can do:

    pip install azure-costs-exporter gunicorn
    cp /path/to/application.cfg .
    gunicorn azure_costs_exporter:app

Tests
-----

The used python testing tool is [pytest](https://docs.pytest.org/en/latest/).
To run the tests:

```bash
mkvirtualenv billing
pip install -r requirements_dev.txt
pip install -e .
py.test
```
