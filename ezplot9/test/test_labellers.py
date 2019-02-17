import pytest

from ezplot9.utilities.labellers import *

ez_labels_testdata = [
    ([1e-3, 0, 1, 1e3, 1e6, 1e9], ['0.001', '0', '1', '1k', '1m', '1b']),
    ([1000, 1001, 1010, 1100], ['1k', '1k', '1.01k', '1.10k'])
]

@pytest.mark.parametrize("x, expected_labels", ez_labels_testdata)
def test_ez_labels(x, expected_labels):
    labels = ez_labels(x)
    assert labels == expected_labels

money_labels_testdata = [
    ([1e-3, 0, 1, 1e3, 1e6, 1e9], ['$0.001', '$0', '$1', '$1k', '$1m', '$1b']),
    ([1000, 1001, 1010, 1100, -1000], ['$1k', '$1k', '$1.01k', '$1.10k', '-$1k'])
]

@pytest.mark.parametrize("x, expected_labels", money_labels_testdata)
def test_money_labels(x, expected_labels):
    labels = money_labels(x)
    assert labels == expected_labels

percent_labels_testdata = [
    ([-1, -0.98, -0.01, 0, 0.1, 0.01, 0.001, 0.00001],
     ['-100.00%', '-98.00%', '-1.00%', '0.00%', '10%', '1%', '0.10%', '0.00%'])
]

@pytest.mark.parametrize("x, expected_labels", percent_labels_testdata)
def test_percent_labels(x, expected_labels):
    labels = percent_labels(x)
    assert labels == expected_labels

bp_labels_testdata = [
    ([-1, -0.98, -0.01, 0, 0.1, 0.01, 0.001, 0.00001, 0.000001],
     ['-10000bp', '-9800bp', '-100bp', '0bp', '1000bp', '100bp', '10bp', '0.10bp', '0.01bp'])
]

@pytest.mark.parametrize("x, expected_labels", bp_labels_testdata)
def test_bp_labels(x, expected_labels):
    labels = bp_labels(x)
    assert labels == expected_labels