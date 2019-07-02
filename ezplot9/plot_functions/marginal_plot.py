import plotnine as p9
import numpy as np
import pandas as pd

from ..utilities.agg_data import agg_data
from ..utilities.utils import unname, sort_data_groups
from ..utilities.labellers import ez_labels
from ..utilities.colors import ez_colors
from ..utilities.themes import theme_ez
from ..utilities.binning import bin_data, qbin_data
from .ezplot import EZPlot

import logging
log = logging.getLogger(__name__)

def marginal_plot(df,
                  x,
                  y,
                  group = None,
                  facet_x = None,
                  facet_y = None,
                  aggfun = 'sum',
                  bins=21,
                  use_quantiles = False,
                  label_pos='auto',
                  label_function=ez_labels,
                  sort_groups=True,
                  base_size=10,
                  figure_size=(6, 3)):

    '''
    Bin the data in a df and plot it using lines.

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
    bins : int or tuple
      number of bins to be used
    use_quantiles : bool
      bin data using quantiles
    label_pos : str
      Use count label on each point. Choose between None, 'auto' or 'force'
    label_function : callable
      labelling function
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

    if label_pos not in [None, 'auto', 'force']:
        log.error("label_pos not recognized")
        raise NotImplementedError("label_pos not recognized")
    elif label_pos == 'auto':
        if bins<=21 and group is None:
            show_labels=True
        else:
            show_labels=False
    else:
        show_labels = True if label_pos=='force' else False

    # create a copy of the data
    dataframe = df.copy()

    # define groups and variables; remove and store (eventual) names
    names = {}
    groups = {}
    variables = {}

    for label, var in zip(['x', 'group', 'facet_x', 'facet_y'], [x,  group, facet_x, facet_y]):
        names[label], groups[label] = unname(var)
    names['y'], variables['y'] = unname(y)

    # set column names and evaluate expressions
    tmp_df = agg_data(dataframe, variables, groups, None, fill_groups=False)

    # redefine groups and variables; remove and store (eventual) names
    new_groups = {c:c for c in tmp_df.columns if c in ['x', 'group', 'facet_x', 'facet_y']}
    new_variables = {'y': 'y'}

    # bin data
    if use_quantiles:
        quantile_groups = [c for c in tmp_df.columns if c in ['group', 'facet_x', 'facet_y']]
        if len(quantile_groups)>0:
            tmp_df['x'] = tmp_df.groupby(quantile_groups)['x'].apply(lambda x: qbin_data(x, bins))
        else:
            tmp_df['x'] = qbin_data(tmp_df['x'], bins)
    else:
        tmp_df['x'], _, _ = bin_data(tmp_df['x'], bins, None)

    # aggregate data and reorder columns
    gdata = agg_data(tmp_df, new_variables, new_groups, aggfun, fill_groups=False)

    # reorder columns
    gdata = gdata[[c for c in ['x', 'y', 'group', 'facet_x', 'facet_y'] if c in gdata.columns]]

    # init plot obj
    g = EZPlot(gdata)

    # determine order and create a categorical type
    if sort_groups:
        sort_data_groups(g)

    # get colors
    colors = np.flip(ez_colors(g.n_groups('group')))

    # set groups
    if group is None:
        g += p9.geom_line(p9.aes(x="x", y="y"), group=1, colour=colors[0])
        if show_labels:
            g += p9.geom_point(p9.aes(x="x", y="y"), group=1, colour=colors[0])
    else:
        g += p9.geom_line(p9.aes(x="x", y="y", group="factor(group)", colour="factor(group)"))
        if show_labels:
            g += p9.geom_point(p9.aes(x="x", y="y", colour="factor(group)"))
        g += p9.scale_color_manual(values=colors)

    # set labels
    if show_labels:
        groups_to_count = [c for c in tmp_df.columns if c in ['x', 'group', 'facet_x', 'facet_y']]
        tmp_df['label']=1
        top_labels = tmp_df \
            .groupby(groups_to_count)['label'] \
            .sum()\
            .reset_index()
        top_labels['label'] = label_function(top_labels['label'])
        
        # make sure labels and  data can be joined
        for c in ['group', 'facet_x', 'facet_y']:
            if c in tmp_df.columns and :
                try:
                    top_labels[c] = pd.Categorical(top_labels[c].astype(str),
                                                   categories = g.data[c].cat.categories,
                                                   ordered = g.data[c].cat.ordered)
                except:
                    pass
        #return g.data, top_labels
        g.data = pd.merge(g.data, top_labels, on=groups_to_count, how='left')
        g.data['label_pos'] = g.data['y'] + \
                    np.sign(g.data['y'])*g.data['y'].abs().max()*0.02

        g += p9.geom_text(p9.aes(x='x', y='label_pos', label='label'),
                          color="#000000",
                          size=base_size * 0.7,
                          ha='center',
                          va='bottom')
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
    g += p9.scale_y_continuous(labels=ez_labels)

    # set axis labels
    g += \
        p9.xlab(names['x']) + \
        p9.ylab(names['y'])

    # set theme
    g += theme_ez(figure_size=figure_size,
                  base_size=base_size,
                  legend_title=p9.element_text(text=names['group'], size=base_size))
    return g
