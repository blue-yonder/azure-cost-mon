Change Log
==========

All notable changes to this project are noted in this file. This project adheres to [Semantic
Versioning](http://semver.org/).

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

