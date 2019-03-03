import plotnine as p9

import numpy as np
import pandas as pd

from ..utilities.agg_data import agg_data
from ..utilities.utils import unname
from ..utilities.labellers import ez_labels, percent_labels
from ..utilities.colors import ez_colors
from ..utilities.themes import theme_ez
from .ezplot import EZPlot

EPSILON = 1e-12

def area_plot(df,
              x,
              y,
              group = None,
              facet_x = None,
              facet_y = None,
              aggfun = 'sum',
              fill = False,
              sort_groups = True,
              base_size = 10,
              figure_size = (6,3)):
    '''
    Aggregates data in df and plots as a stacked area chart.

    Parameters
    ----------
    df : pd.DataFrame
      input dataframe
    x : str
      quoted expression to be plotted on the x axis
    y : str
      quoted expression to be plotted on the y axis
    group : str
      quoted expression to be used as group (ie color)
    facet_x : str
      quoted expression to be used as facet
    facet_y : str
      quoted expression to be used as facet
    aggfun : str or fun
      function to be used for aggregating (eg sum, mean, median ...)
    fill : bool
      plot shares for each group instead of absolute values
    sort_groups : bool
      sort groups by the sum of their value (otherwise alphabetical order is used)
    base_size : int
      base size for theme_ez
    figure_size :tuple of int
      figure size

    Returns
    -------
    g : EZPlot
      EZplot object

    '''

    # create a copy of the data
    dataframe = df.copy()

    # define groups and variables; remove and store (eventual) names
    names = {}
    groups = {}
    variables = {}

    for label, var in zip(['x', 'group', 'facet_x', 'facet_y'], [x, group, facet_x, facet_y]):
        names[label], groups[label] = unname(var)
    names['y'], variables['y'] = unname(y)

    # fix special cases
    if x == '.index':
        groups['x'] = '.index'
        names['x'] = dataframe.index.name if dataframe.index.name is not None else ''

    # aggregate data and reorder columns
    gdata = agg_data(dataframe, variables, groups, aggfun, fill_groups=True)
    gdata['y'].fillna(0, inplace=True)
    gdata = gdata[[c for c in ['x', 'y', 'group', 'facet_x', 'facet_y'] if c in gdata.columns]]

    if fill:
        groups_to_normalize = [c for c in ['x', 'facet_x', 'facet_y'] if c in gdata.columns]
        total_values = gdata\
            .groupby(groups_to_normalize)['y']\
            .sum()\
            .reset_index()\
            .rename(columns = {'y':'tot_y'})
        gdata = pd.merge(gdata, total_values, on = groups_to_normalize)
        gdata['y'] = gdata['y'] / (gdata['tot_y'] + EPSILON)
        gdata.drop('tot_y', axis=1, inplace=True)
        ylabeller = percent_labels
    else:
        ylabeller = ez_labels

    # get plot object
    g = EZPlot(gdata)

    # determine order and create a categorical type
    if (group is not None) and sort_groups:
        g.sort_group('group', 'y')
        g.sort_group('facet_x', 'y', ascending=False)
        g.sort_group('facet_y', 'y', ascending=False)
        if groups:
            colors = np.flip(ez_colors(g.n_groups('group')))
    elif (group is not None):
        colors = ez_colors(g.n_groups('group'))

    # set groups
    if group is None:
        g += p9.geom_area(p9.aes(x="x", y="y"),
                          colour = None,
                          fill = ez_colors(1)[0],
                          na_rm=True)
    else:
        g += p9.geom_area(p9.aes(x="x", y="y",
                                 group="factor(group)",
                                 fill="factor(group)"),
                          colour=None,
                          na_rm=True)
        g += p9.scale_fill_manual(values=colors)

    # set facets
    if facet_x is not None and facet_y is None:
        g += p9.facet_wrap('~facet_x')
    if facet_x is not None and facet_y is not None:
        g += p9.facet_grid('facet_y~facet_x')

    # set x scale
    if g.column_is_timestamp('x'):
        g += p9.scale_x_datetime()
    elif g.column_is_categorical('x'):
        g += p9.scale_x_discrete()
    else:
        g += p9.scale_x_continuous(labels=ez_labels)

    # set y scale
    g += p9.scale_y_continuous(labels=ylabeller)

    # set axis labels
    g += \
        p9.xlab(names['x']) + \
        p9.ylab(names['y'])

    # set theme
    g += theme_ez(figure_size = figure_size,
                  base_size = base_size,
                  legend_title=p9.element_text(text=names['group'], size=base_size))

    if sort_groups:
      g+= p9.guides(fill=p9.guide_legend(reverse=True), color=p9.guide_legend(reverse=True))

    return g



