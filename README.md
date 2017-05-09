[![Build Status](https://travis-ci.org/blue-yonder/azure-cost-mon.svg?branch=master)](https://travis-ci.org/blue-yonder/azure-cost-mon)
[![Coverage Status](https://coveralls.io/repos/github/blue-yonder/azure-cost-mon/badge.svg?branch=master)](https://coveralls.io/github/blue-yonder/azure-cost-mon?branch=master)

azure-billing
=============

Prometheus scraper for the Microsoft Azure billing API.

Description
-----------

**azure-billing** is a web app, that is intended to be called by [Prometheus](https://prometheus.io) to export billing information from Azure. 
It will then return the available metrics in Prometheus compatible format.

The billing API in use is part of the "Enterprise Agreement (EA)" Portal. Hence it has not been tested for pay-as-you-go 
subscriptions. The configuration requires an active EA with Microsoft.

Configuration
-------------

You need to create an application.cfg file with the following content:

    ENROLLMENT_NUMBER="123456"
    BILLING_API_ACCESS_KEY="XXX"
    PROMETHEUS_METRIC_NAME="my_metric_name"

- `ENROLLMENT_NUMBER` is the unique ID that identifies a particular EA.
- The `BILLING_API_ACCESS_KEY` can be created in the [EA portal](https://ea.azure.com/) to gain
access to the billing API. Navigate to "Reports > Download Usage" and generate an API Access Key.
- `PROMETHEUS_METRIC_NAME` is the name of the time series that will be generated in
  Prometheus. This configuration is optional and defaults to `azure_costs`

Deployment
----------

E.g. via `gunicorn` in a `virtualenv` that contains this package as well as `gunicorn`:

    gunicorn azure-billing:app



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
