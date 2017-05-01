azure-billing
=============

Prometheus scraper for Azure billing API.

Description
-----------

**azure-billing** is a web app, that is intended to be called by Prometheus to export billing information from azure. 
It will then return the available metrics in Prometheus compatible format.

Configuration
-------------

You need to create an application.cfg file with the following content:

    ENROLLMENT="123456"
    TOKEN="XXX"


Tests
-----

The used python testing tool is [pytest](http://pytest.org/latest/).
To run the tests:

```bash
mkvirtualenv billing
pip install -e .
pip install -r requirements_dev.txt
py.test
```
