import plotnine as p9
from ..utilities.agg_data import agg_data, bootstrapping_aggregation
from ..utilities.utils import unname
from ..utilities.labellers import ez_labels
from ..utilities.colors import ez_colors
from ..utilities.themes import theme_ez
from .ezplot import EZPlot
import pandas as pd
import numpy as np
import bootstrapped.stats_functions as bs_stats
from pandas.io.json import json_normalize


def ci_plot(df,
            x,
            y,
            group = None,
            facet_x = None,
            facet_y = None,
            base_size = 10,
            figure_size = (6,3),
            aggfun = bs_stats.mean,
            num_iterations = 10_000,
            **kwargs):
    '''
    Aggregates data in df and plots as a line chart.

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
    base_size : int
      base size for theme_ez
    figure_size :tuple of int
      figure size
    **kwargs : kwargs
      additional kwargs for geom_boxplot

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
    gdata = agg_data(dataframe,
                     variables,
                     groups,
                     lambda x: bootstrapping_aggregation(x, aggfun, num_iterations, **kwargs),
                     fill_groups=True)

    empty_dict = {'sample_size': 0,
                  'num_iterations': num_iterations,
                  'center': np.nan,
                  'low': np.nan,
                  'high': np.nan,
                  'successful': np.nan}
    gdata['y'] = gdata['y']\
                .apply(lambda x: empty_dict if isinstance(x, float) and np.isnan(x) else x)

    gdata = gdata[[c for c in ['x', 'y', 'group', 'facet_x', 'facet_y'] if c in gdata.columns]]
    for k,v in kwargs.items():
        gdata[k] = v

    # add group_x column
    if group is not None:
        gdata['group_x'] = gdata['group'].astype('str') + '_' + gdata['x'].astype(str)

    gdata = pd.concat([gdata.drop('y', axis=1),
                       json_normalize(gdata['y'])],
                      axis=1)

    g = EZPlot(gdata)

    # set groups
    if group is None:
        g += p9.geom_crossbar(p9.aes(x="factor(x)", y='center', ymin='low', ymax='high',
                                     group="factor(x)"),
                              colour = ez_colors(1)[0],
                              na_rm = False)
    else:
        g += p9.geom_crossbar(p9.aes(x="factor(x)", y='center', ymin='low', ymax='high',
                                     group="factor(group_x)", fill="factor(group)"),
                              position=p9.position_dodge(0.9, preserve='single'),
                              na_rm = True)

        g += p9.scale_fill_manual(values=ez_colors(g.n_groups('group')))

    # set facets
    if facet_x is not None and facet_y is None:
        g += p9.facet_wrap('~facet_x')
    if facet_x is not None and facet_y is not None:
        g += p9.facet_grid('facet_y~facet_x')

    # set x scale
    g += p9.scale_x_discrete()

    # set y scale
    g += p9.scale_y_continuous(labels=ez_labels)

    # set axis labels
    g += \
        p9.xlab(names['x']) + \
        p9.ylab(names['y'])

    # set theme
    g += theme_ez(figure_size = figure_size,
                  base_size = base_size,
                  legend_title=p9.element_text(text=names['group'], size=base_size))

    return g



