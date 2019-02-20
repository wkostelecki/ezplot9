import pytest
from pydataset import data

from ..utilities import agg_data

mtcars = data('mtcars')

get_groups_testdata = [(None, {}, {},
                        {}, {}, {}),
                       (None, {'y':'a', 'w':'@a/b'}, {'group':'g'},
                        {'group': 'g'}, {'y': 'a'}, {'w': 'a/b'}),
                       (None, {'y':['a', 'b', 'c'], 'z':'@a/b'}, {'group':'g'},
                        {'group': 'g'}, {'y_0': 'a', 'y_1': 'b', 'y_2': 'c'}, {'z': 'a/b'}),
                       (mtcars, {'x':'.index'}, {'group':'g'},
                        {'group': 'g'}, {'x': '.index'}, {})]
@pytest.mark.parametrize("df, variables, groups,"
                         "expected_data_groups, expected_data_variables, expected_delayed_variables",
                         get_groups_testdata)
def test_get_groups(df, variables, groups,
                    expected_data_groups, expected_data_variables, expected_delayed_variables):
    data_groups, data_variables, delayed_variables = agg_data.get_groups(df, variables, groups)
    assert data_groups == expected_data_groups
    assert data_variables == expected_data_variables
    assert delayed_variables == expected_delayed_variables