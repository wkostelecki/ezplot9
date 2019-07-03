import plotnine as p9
from ..utilities.agg_data import agg_data
from ..utilities.utils import unname
from ..utilities.labellers import ez_labels
from ..utilities.colors import ez_colors
from ..utilities.themes import theme_ez
from .ezplot import EZPlot

from sklearn.metrics import auc, roc_curve

import pandas as pd

import logging
log = logging.getLogger(__name__)


def compute_roc_params(target, prob, pos_label):
    fpr, tpr, th = roc_curve(target, prob, pos_label)
    auc_value = auc(fpr, tpr)
    fpr = np.round(fpr, 4)
    tpr = np.round(tpr, 4)

    roc_df = pd.DataFrame({'x': fpr, 'y': tpr})\
            .groupby('x')\
            .first()\
            .reset_index()

    return roc_df, auc_value

def roc_plot(df,
             target,
             prob,
             group=None,
             facet_x=None,
             facet_y=None,
             pos_label=1,
             show_points=False,
             base_size=10,
             figure_size=(6, 3)):
    '''
    Aggregates data in df and plots multiple columns as a line chart.

    Parameters
    ----------
    df : pd.DataFrame
      input dataframe
    target : str
      columns with targets
    prob : str or list of str
      column(s) with probabilities
    group : str
      quoted expression to be used as group (ie color)
    facet_x : str
      quoted expression to be used as facet
    facet_y : str
      quoted expression to be used as facet
    show_points : bool
      show/hide markers
    base_size : int
      base size for theme_ez
    figure_size :tuple of int
      figure size

    Returns
    -------
    g : EZPlot
      EZplot object

    '''

    if group is not None and isinstance(y, list) and len(y) > 1:
        log.error("groups can be specified only when a single y column is present")
        raise ValueError("groups can be specified only when a single y column is present")

    if isinstance(y, list) and len(y) == 1:
        y = y[0]

    # create a copy of the data
    dataframe = df.copy()

    # define groups and variables; remove and store (eventual) names
    names = {}
    groups = {}
    variables = {}

    for label, var in zip(['x', 'group', 'facet_x', 'facet_y'], [x, group, facet_x, facet_y]):
        names[label], groups[label] = unname(var)

    # fix special cases
    if x == '.index':
        groups['x'] = '.index'
        names['x'] = dataframe.index.name if dataframe.index.name is not None else ''

    if isinstance(y, list):

        ys = []
        for i, var in enumerate(y):
            ys.append('y_{}'.format(i))
            names['y_{}'.format(i)], variables['y_{}'.format(i)] = unname(var)

        # aggregate data
        tmp_gdata = agg_data(dataframe, variables, groups, None, fill_groups=False)
        groups_present = [c for c in ['x', 'facet_x', 'facet_y'] if c in tmp_gdata.columns]
        gdata = pd.melt(tmp_gdata, groups_present, var_name='group', value_name='y')
        gdata['group'] = gdata['group'].replace({var: names[var] for var in ys})

        # update values for plotting
        names['y'] = 'Value'
        names['group'] = 'Variable'
        group = 'Variable'

    else:

        names['y'], variables['y'] = unname(y)

        # aggregate data
        gdata = agg_data(dataframe, variables, groups, None, fill_groups=False)

    # add fake group column if group is not present
    if not ('group' in gdata.columns):
        gdata['group'] = '.'

    # reorder columns
    data = data[[c for c in ['x', 'y', 'group', 'facet_x', 'facet_y'] if c in gdata.columns]]

    # compute roc curve parameters
    groups = [c for c in ['x', 'y', 'group', 'facet_x', 'facet_y'] if c in gdata.columns]
    roc_dfs = {}
    auc_d = {}
    for g_name, g_df in data.groupby(groups):
        roc_df, auc_value = compute_roc_params(g_df['x'], g_df['y'], pos_label)
        roc_dfs[g_name] = roc_df
        auc_d[g_name] - auc_value

    return roc_dfs, auc_d




