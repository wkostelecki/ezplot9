import plotnine as p9
from ..utilities.agg_data import agg_data
from ..utilities.utils import unname
from ..utilities.labellers import percent_labels
from ..utilities.colors import ez_colors
from ..utilities.themes import theme_ez
from .ezplot import EZPlot
from .line_plot import line_plot

from sklearn.metrics import auc, roc_curve

import pandas as pd
import numpy as np

import logging
log = logging.getLogger(__name__)


def compute_roc_params(target, prob, pos_label):
    fpr, tpr, th = roc_curve(target, prob, pos_label)
    auc_value = auc(fpr, tpr)
    fpr = np.round(fpr, 4)
    tpr = np.round(tpr, 4)

    roc_df = pd.DataFrame({'x': fpr, 'y': tpr}) \
        .groupby('x') \
        .first() \
        .reset_index()

    auc_df = pd.DataFrame({'auc':auc_value}, index = [0])
    return roc_df, auc_df

def roc_plot(df,
             target,
             prob,
             group=None,
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

    x=target
    y=prob
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

    for label, var in zip(['x', 'group'], [x, group]):
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
        tmp_data = agg_data(dataframe, variables, groups, None, fill_groups=True)
        groups_present = [c for c in ['x'] if c in tmp_data.columns]
        data = pd.melt(tmp_data, groups_present, var_name='group', value_name='y')
        data['group'] = data['group'].replace({var: names[var] for var in ys})

        # update values for plotting
        names['y'] = 'Value'
        names['group'] = 'Variable'
        group = 'Variable'

    else:

        names['y'], variables['y'] = unname(y)

        # aggregate data
        data = agg_data(dataframe, variables, groups, None, fill_groups=True)

    # add fake group column if group is not present
    if not ('group' in data.columns):
        data['group'] = ''

    # reorder columns
    data = data[[c for c in ['x', 'y', 'group'] if c in data.columns]]

    # compute roc curve parameters
    roc_dfs = {}
    auc_dfs = {}
    for g_name, g_df in data.groupby('group'):
        roc_dfs[g_name], auc_dfs[g_name] = compute_roc_params(g_df['x'], g_df['y'], pos_label)

    roc_df = pd.concat(roc_dfs, names = ['group']) \
        .reset_index()[['x', 'y', 'group']]

    auc_df = pd.concat(auc_dfs, names = ['group']) \
        .reset_index()[['auc', 'group']]

    auc_df['label'] = auc_df['auc'].apply(lambda x: '{:.3f}'.format(x))
    auc_df['tmp'] = -1

    # init plot obj
    g = EZPlot(roc_df)

    # set groups
    if group is None:
        g += p9.geom_line(p9.aes(x="x", y="y"), group=1, colour=ez_colors(1)[0])
    else:
        g += p9.geom_line(p9.aes(x="x", y="y", group="factor(group)", colour="factor(group)"))
        g += p9.scale_color_manual(values=ez_colors(g.n_groups('group')), name = names['group'])
        
    g += p9.geom_line(p9.aes(x='guide_x', y='guide_y'),
                      data=pd.DataFrame(data={'guide_x':[0,1], 'guide_y':[0,1]}),
                      color = '#696969',
                      linetype = 'dashed')
    
    g += p9.xlab('False Positive Rate') + \
         p9.ylab('True Positive Rate')
    
    g += p9.scale_x_continuous(labels=percent_labels, limits=[0,1])
    g += p9.scale_y_continuous(labels=percent_labels, limits=[0,1])
    
    g+=p9.geom_point(p9.aes(x='tmp', y='tmp', fill = 'label', group='group'), data = auc_df, stroke=0, size=4)
    g+=p9.scale_fill_manual(values=ez_colors(g.n_groups('group')), name = 'AUC')

    # set theme
    g += theme_ez(figure_size = figure_size,
                    base_size = base_size)
        
    return g, auc_df




