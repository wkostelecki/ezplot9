import plotnine as p9

import numpy as np
import pandas as pd

from ..utilities.agg_data import agg_data
from ..utilities.utils import unname, sort_data_groups
from ..utilities.labellers import ez_labels, percent_labels
from ..utilities.colors import ez_colors, text_contrast
from ..utilities.themes import theme_ez
from .ezplot import EZPlot

import logging
log = logging.getLogger(__name__)

POSITION_KWARGS = {'overlay':{'position':'identity', 'alpha':0.7},
                   'stack':{},
                   'dodge':{'position':'dodge'}}
EPSILON = 1e-12

def bar_plot(df,
             x,
             y,
             group = None,
             facet_x = None,
             facet_y = None,
             aggfun = 'sum',
             fill = False,
             label_pos = 'auto',
             label_function = ez_labels,
             inside_labels_cutoff=0.04,
             position='stack',
             orientation = 'vertical',
             sort_groups = True,
             base_size = 10,
             figure_size = (6,3)):

    '''
    Aggregates data in df and plots as a bar chart.

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
    position : str
      if groups are present, choose between `stack`, `overlay` or `dodge`
    orientation : str
      use vertical or horizontal bars
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

    if orientation not in ['horizontal', 'vertical']:
        log.error("orientation not recognized")
        raise NotImplementedError("orientation not recognized")

    if position not in ['overlay', 'stack', 'dodge']:
        log.error("position not recognized")
        raise NotImplementedError("position not recognized")

    if label_pos not in [None, 'auto','top', 'inside', 'both']:
        log.error("label_pos not recognized")
        raise NotImplementedError("label_pos not recognized")
    elif label_pos=='auto':
        if position=='stack':
            if fill:
                label_pos='inside'
            else:
                label_pos = 'both'
        elif position == 'dodge':
            label_pos = 'top'
        elif position == 'overlay':
            position = None

    if fill:
        label_function = percent_labels

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

    # aggregate data
    gdata = agg_data(dataframe, variables, groups, aggfun, fill_groups=True)

    if fill:
        groups_to_normalize = [c for c in ['x', 'facet_x', 'facet_y'] if c in gdata.columns]
        total_values = gdata \
            .groupby(groups_to_normalize)['y'] \
            .sum() \
            .reset_index() \
            .rename(columns = {'y':'tot_y'})
        gdata = pd.merge(gdata, total_values, on = groups_to_normalize)
        gdata['y'] = gdata['y'] / (gdata['tot_y'] + EPSILON)
        gdata.drop('tot_y', axis=1, inplace=True)
        ylabeller = percent_labels
    else:
        ylabeller = ez_labels

    g = EZPlot(gdata)

    # determine order and create a categorical type
    if sort_groups:
        sort_data_groups(g)

    # get colors
    colors = np.flip(ez_colors(g.n_groups('group')))

    # set groups
    if group is None:
        g += p9.geom_col(p9.aes(x="x", y="y"), fill = ez_colors(1)[0])
    else:
        g += p9.geom_col(p9.aes(x="x", y="y",
                                group="factor(group)",
                                fill="factor(group)"),
                         **POSITION_KWARGS[position])
        g += p9.scale_fill_manual(values=colors, reverse=False)

    # set top labels
    if label_pos in ['top', 'both']:

        if position=='stack':
            groups_to_sum = [c for c in ['x', 'facet_x', 'facet_y'] if c in gdata.columns]
            top_labels = g.data \
                .groupby(groups_to_sum)['y'] \
                .sum() \
                .reset_index() \
                .rename(columns={'y': 'top_label_ypos'})
            top_labels['top_label'] = label_function(top_labels['top_label_ypos'])

            g += p9.geom_text(p9.aes(x='x', y='top_label_ypos',label='top_label'),
                              data = top_labels,
                              color = "#000000",
                              size=base_size*0.7,
                              va='bottom')
        else:
            top_labels = g.data.copy()
            top_labels['top_label_ypos'] = top_labels['y']
            top_labels['top_label'] = label_function(top_labels['top_label_ypos'])
            g += p9.geom_text(p9.aes(x='x', y='top_label_ypos',
                                     label='top_label',
                                     group="factor(group)"),
                              data = top_labels,
                              color = "#000000",
                              size=base_size*0.7,
                              va='bottom',
                              position=p9.position_dodge(1))

    if (label_pos in ['inside', 'both']) & (position == 'stack'):
        groups_to_sum = [c for c in ['x', 'facet_x', 'facet_y'] if c in gdata.columns]
        inside_labels = g.data.copy()
        if group is None:
            inside_labels['group']='.'
        inside_labels['inside_label_ypos'] = \
            inside_labels\
            .sort_values('group', ascending=False) \
            .groupby(groups_to_sum, sort=False)['y'] \
            .cumsum()
        cut_off_val = inside_labels.groupby(groups_to_sum).sum().max().values[0]
        inside_labels['inside_label_ypos'] = inside_labels['inside_label_ypos'] - inside_labels['y']/2
        inside_labels['inside_label'] = \
            np.where(inside_labels['y']>inside_labels_cutoff*cut_off_val,
                     label_function(inside_labels['y']),
                     '')

        g += p9.geom_text(p9.aes(x='x', y='inside_label_ypos',
                                 label='inside_label',
                                 color = 'factor(group)'),
                          data=inside_labels,
                          size=base_size * 0.6,
                          va='center')
        g += p9.scale_color_manual(values=text_contrast(colors),
                                   reverse=True,
                                   guide=None)


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
    g += p9.scale_y_continuous(labels=ylabeller,
                               expand=[0,0,0.1*(not fill)+0.03,0])

    # set axis labels
    g += \
        p9.xlab(names['x']) + \
        p9.ylab(names['y'])

    # set orientation
    if orientation=='horizontal':
        g += p9.coord_flip()

    # set theme
    g += theme_ez(figure_size = figure_size,
                  base_size = base_size,
                  legend_title=p9.element_text(text=names['group'], size=base_size))

    if sort_groups:
        g+= p9.guides(fill=p9.guide_legend(reverse=True))

    return g

