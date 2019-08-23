import plotnine as p9
import numpy as np

from ..utilities.agg_data import agg_data
from ..utilities.utils import unname
from ..utilities.labellers import ez_labels
from ..utilities.colors import ez_colors
from ..utilities.themes import theme_ez
from ..utilities.binning import bin_data
from .ezplot import EZPlot

import logging
log = logging.getLogger(__name__)

POSITION_KWARGS = {'overlay':{'position':'identity', 'alpha':0.2},
                   'stack':{'position':'stack'}}

def density_plot(df,
                 x,
                 group = None,
                 facet_x = None,
                 facet_y = None,
                 position = 'overlay',
                 sort_groups=True,
                 base_size=10,
                 figure_size=(6, 3),
                 **stat_kwargs):

    '''
    Plot a 1-d density plot

    Parameters
    ----------
    df : pd.DataFrame
      input dataframe
    x : str
      quoted expression to be plotted on the x axis
    group : str
      quoted expression to be used as group (ie color)
    facet_x : str
      quoted expression to be used as facet
    facet_y : str
      quoted expression to be used as facet
    position : str
      if groups are present, choose between `stack` or `overlay`
    base_size : int
      base size for theme_ez
    figure_size :tuple of int
      figure size
    stat_kwargs : kwargs
      kwargs for the density stat

    Returns
    -------
    g : EZPlot
      EZplot object

    '''

    if position not in ['overlay', 'stack']:
        log.error("position not recognized")
        raise NotImplementedError("position not recognized")

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

    # aggregate data and reorder columns
    gdata = agg_data(dataframe, variables, groups, None, fill_groups=False)
    gdata = gdata[[c for c in ['x', 'group', 'facet_x', 'facet_y'] if c in gdata.columns]]

    # start plotting
    g = EZPlot(gdata)
    
    # determine order and create a categorical type
    colors = ez_colors(g.n_groups('group'))

    # set groups
    if group is None:
        g += p9.geom_density(p9.aes(x="x"),
                             stat = p9.stats.stat_density(**stat_kwargs),
                             colour = ez_colors(1)[0],
                             fill = ez_colors(1)[0],
                             **POSITION_KWARGS[position])
    else:
        g += p9.geom_density(p9.aes(x="x",
                                    group="factor(group)",
                                    colour="factor(group)",
                                    fill="factor(group)"),
                             stat = p9.stats.stat_density(**stat_kwargs),
                             **POSITION_KWARGS[position])
        g += p9.scale_fill_manual(values=colors, reverse=False)
        g += p9.scale_color_manual(values=colors, reverse=False)

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
        p9.ylab('Density')

    # set theme
    g += theme_ez(figure_size=figure_size,
                  base_size=base_size,
                  legend_title=p9.element_text(text=names['group'], size=base_size))

    if sort_groups:
        g += p9.guides(fill=p9.guide_legend(reverse=True))

    return g
