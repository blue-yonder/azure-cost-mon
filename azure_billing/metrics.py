

class Counter(object):
    """
    Counter for Prometheus.
    """
    def __init__(self, name, doc=None):
        self._name = name
        self._doc = doc
        self._records = []

    def _definition(self):
        """Output HELP and TYPE info for Prometheus."""
        msg = "# HELP %s %s" % (self._name, self._doc)
        msg += "\n"
        msg += "# TYPE %s counter" % self._name
        msg += "\n"
        return msg

    def record(self, value, **params):
        """
        Issue a prometheus compliant record.

        :value: the value to be set (float)
        :param_dict: parameters that should be attached to the entry

        :return: string to be used in webservice that is scraped by prometheus.
        """
        msg = "%s" % self._name

        if params:
            param_list = [k + '="' + v + '"' for k, v in sorted(params.items())]
            msg += '{' + ",".join(param_list) + '}'

        msg += " %.2f" % value
        msg += "\n"

        self._records.append(msg)

    def serialize(self):
        if self._records:
            return self._definition() + ''.join(self._records)
        else:
            return ''
