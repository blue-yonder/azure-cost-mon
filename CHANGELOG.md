Change Log
==========

All notable changes to this project are noted in this file. This project adheres to [Semantic
Versioning](http://semver.org/).

1.1.0
-----

- Added BILLING_SCRAPE_TIMEOUT to be able to set a different value then the default of 10 seconds
- Bugfix: convert subscription_id to string, since azure management compute module raises an 
  Exception if a unicode string is passed as an argument

1.0.0
-----

- Added support for additional metrics: allocated virtual machines and reserved virtual machine
  instances
- Renamed configuration option `PROMETHEUS_METRIC_NAME` to `BILLING_METRIC_NAME`


0.4.1
-----

- Fixed issue (https://github.com/blue-yonder/azure-cost-mon/issues/12)
  where the sum of multiple time series was numerically instable by
  emitting only integer values. The instability resulted in more counter
  resets within Prometheus than necessary, so that `increase` gave wrong
  results!


0.4.0
-----

- Use the `X-Prometheus-Scrape-Timeout-Seconds` header sent by
  prometheus to overwrite the internal request timeout default.


0.3.1
-----

- Fixed the exporter to cope with the non-standard response for months
  without usage details.


0.3.0
-----

- Removed own metric implementation in favor of the
  official prometheus_client
- Made metrics name non-optional in the configuration to prevent
  non standard metric name (w/o unit).
- Adapted README to match the package renaming

0.2
---

- Initial version

