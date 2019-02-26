import plotnine as p9
import numpy as np

from ..utilities.agg_data import agg_data
from ..utilities.utils import unname
from ..utilities.labellers import ez_labels
from ..utilities.colors import ez_colors
from ..utilities.themes import theme_ez
from ..utilities.binnnig import bin_data
from .ezplot import EZPlot

import logging
log = logging.getLogger(__name__)

POSITION_KWARGS = {'overlay':{'position':'identity', 'alpha':0.7},
                   'stack':{},
                   'dodge':{'position':'dodge'}}

def hist_plot(df,
              x,
              y=None,
              group = None,
              facet_x = None,
              facet_y = None,
              w='1',
              bins=21,
              bin_width = None,
              position = 'stack',
              normalize = False,
              base_size=10,
              figure_size=(6, 3)):

    '''
    Plot a 1-d or 2-d histogram

    Parameters
    ----------
    df : pd.DataFrame
      input dataframe
    x : str
      quoted expression to be plotted on the x axis
    y : str
      quoted expression to be plotted on the y axis. If this is specified the histogram will be 2-d.
    group : str
      quoted expression to be used as group (ie color)
    facet_x : str
      quoted expression to be used as facet
    facet_y : str
      quoted expression to be used as facet
    w : str
      quoted expression representing histogram weights (default is 1)
    bins : int or tuple
        number of bins to be used
    bin_width : float or tuple
        bin width to be used
    position : str
        if groups are present, choose between `stack`, `overlay` or `dodge`
    normalize : bool
        normalize histogram counts
    base_size : int
      base size for theme_ez
    figure_size :tuple of int
      figure size

    Returns
    -------
    g : EZPlot
      EZplot object

    '''

    if position not in ['overlay', 'stack', 'dodge']:
        log.error("position not recognized")
        raise NotImplementedError("position not recognized")

    if (bins is None) and (bin_width is None):
        log.error("Either bins or bin_with should be defined")
        raise ValueError("Either bins or bin_with should be defined")

    if (bins is not None) and (bin_width is not None):
        log.error("Only one between bins or bin_with should be defined")
        raise ValueError("Only one between  bins or bin_with should be defined")

    if (y is not None) and (group is not None):
        log.error("y and group cannot be requested at the same time")
        raise ValueError("y and group cannot be requested at the same time")

    if y is None:
        bins = (bins, bins)
        bin_width = (bin_width, bin_width)
    else:
        if type(bins) not in [tuple, list]:
            bins = (bins, bins)
        if type(bin_width) not in [tuple, list]:
            bin_width = (bin_width, bin_width)

    # create a copy of the data
    dataframe = df.copy()

    # define groups and variables; remove and store (eventual) names
    names = {}
    groups = {}
    variables = {}

    for label, var in zip(['x', 'y', 'group', 'facet_x', 'facet_y'], [x, y, group, facet_x, facet_y]):
        names[label], groups[label] = unname(var)
    names['w'], variables['w'] = unname(w)

    # set column names and evaluate expressions
    tmp_df = agg_data(dataframe, variables, groups, None, fill_groups=False)

    # redefine groups and variables; remove and store (eventual) names
    new_groups = {c:c for c in tmp_df.columns if c in ['x', 'y', 'group', 'facet_x', 'facet_y']}
    non_xy_groups = [g for g  in new_groups.keys() if g not in ['x', 'y']]
    new_variables = {'w':'w'}

    # bin data (if necessary)
    if tmp_df['x'].dtypes != np.dtype('O'):
        tmp_df['x'], bins_x, bin_width_x= bin_data(tmp_df['x'], bins[0], bin_width[0])
    else:
        bin_width_x=1
    if y is not None:
        if tmp_df['y'].dtypes != np.dtype('O'):
            tmp_df['y'], bins_y, bin_width_y = bin_data(tmp_df['y'], bins[1], bin_width[1])
        else:
            bin_width_y=1
    else:
        bin_width_y=1

    # aggregate data and reorder columns
    gdata = agg_data(tmp_df, new_variables, new_groups, 'sum', fill_groups=True)
    gdata.fillna(0, inplace=True)
    gdata = gdata[[c for c in ['x', 'y', 'w', 'group', 'facet_x', 'facet_y'] if c in gdata.columns]]

    # normalize
    if normalize:
        if len(non_xy_groups)==0:
            gdata['w'] = gdata['w']/(gdata['w'].sum()*bin_width_x*bin_width_y)
        else:
            gdata['w'] = gdata.groupby(non_xy_groups)['w'].apply(lambda x: x/(x.sum()*bin_width_x*bin_width_y))

    # start plotting
    g = EZPlot(gdata)

    if y is None:
        # set groups
        if group is None:
            g += p9.geom_bar(p9.aes(x="x", y="w"),
                             stat = 'identity',
                             colour = None,
                             fill = ez_colors(1)[0])
        else:
            g += p9.geom_bar(p9.aes(x="x", y="w",
                                    group="factor(group)",
                                    fill="factor(group)"),
                             colour=None,
                             stat = 'identity',
                             **POSITION_KWARGS[position])
            g += p9.scale_fill_manual(values=ez_colors(g.n_groups('group')))

        # set facets
        if facet_x is not None and facet_y is None:
            g += p9.facet_wrap('~facet_x')
        if facet_x is not None and facet_y is not None:
            g += p9.facet_grid('facet_y~facet_x')

        # set x scale
        if g.column_is_categorical('x'):
            g += p9.scale_x_discrete()
        else:
            g += p9.scale_x_continuous(labels=ez_labels)

        # set y scale
        g += p9.scale_y_continuous(labels=ez_labels)

        # set axis labels
        g += \
            p9.xlab(names['x']) + \
            p9.ylab('Counts')

        # set theme
        g += theme_ez(figure_size=figure_size,
                      base_size=base_size,
                      legend_title=p9.element_text(text=names['group'], size=base_size))

    else:
        g += p9.geom_tile(p9.aes(x="x", y="y", fill='w'),
                          stat = 'identity',
                          colour = None)

        # set facets
        if facet_x is not None and facet_y is None:
            g += p9.facet_wrap('~facet_x')
        if facet_x is not None and facet_y is not None:
            g += p9.facet_grid('facet_y~facet_x')

        # set x scale
        if g.column_is_categorical('x'):
            g += p9.scale_x_discrete()
        else:
            g += p9.scale_x_continuous(labels=ez_labels)

        # set y scale
        if g.column_is_categorical('y'):
            g += p9.scale_y_discrete()
        else:
            g += p9.scale_y_continuous(labels=ez_labels)

        # set axis labels
        g += \
            p9.xlab(names['x']) + \
            p9.ylab(names['y'])

        # set theme
        g += theme_ez(figure_size=figure_size,
                      base_size=base_size,
                      legend_title=p9.element_text(text='Counts', size=base_size))

    return g
