import pytest
import textwrap
from azure_costs_exporter.metrics import Counter


def test_no_name():

    with pytest.raises(TypeError):
        c = Counter()

def test_empty_counter():
    c = Counter('foo')
    assert c.serialize() == '' 

def test_single_record():
    name = 'foo'
    desc = 'some description'
    value = 1.2

    c = Counter(name, desc)
    c.record(value)

    result = c.serialize()

    expected = textwrap.dedent(
"""# HELP {0} {1}
# TYPE {0} counter
{0} {2:.2f}
""".format(name, desc, value))

    assert result == expected

def test_meta_data_record():
    name = 'foo'
    desc = 'bla'
    value = 1.2
    meta = dict(tag='something')

    c = Counter(name, desc)
    c.record(value, **meta)
    result = c.serialize()

    expected = name + '{tag="something"} ' + "%.2f" % (value,)

    assert result.split('\n')[2] == expected

