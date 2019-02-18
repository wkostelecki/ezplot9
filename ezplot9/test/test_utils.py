import pytest

from ezplot9.utilities import utils

unname_testdata = [
    ('x', 'x', 'x'),
    ('a=b', 'a', 'b'),
    ('a=b + c', 'a', 'b + c'),
    (' a =b + c', 'a', 'b + c'),
    ('a==b', 'a==b', 'a==b'),
    ('a=b==c', 'a', 'b==c'),
    ('a=(b==c)&(d>=0)', 'a', '(b==c)&(d>=0)'),
]

@pytest.mark.parametrize("x, expected_name, expected_var", unname_testdata)
def test_unname(x, expected_name, expected_var):
    name, var = utils.unname(x)
    assert name == expected_name
    assert var == expected_var
