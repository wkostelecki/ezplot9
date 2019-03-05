import plotnine as p9
import numpy as np
import pandas as pd

from ..utilities.agg_data import agg_data
from ..utilities.utils import unname
from ..utilities.labellers import ez_labels
from ..utilities.colors import ez_colors
from ..utilities.themes import theme_ez
from ..utilities.binning import bin_data
from .ezplot import EZPlot

import logging
log = logging.getLogger(__name__)

POSITION_KWARGS = {'overlay':{'position':'identity', 'alpha':0.7},
                   'stack':{},
                   'dodge':{'position':'dodge'}}

def variable_histogram(df,
                       x,
                       group = None,
                       facet_y = None,
                       w='1',
                       bins=21,
                       bin_width = None,
                       position = 'stack',
                       normalize = False,
                       sort_groups=True,
                       base_size=10,
                       figure_size=(6, 3)):

    '''
    Plot a 1-d histogram

    Parameters
    ----------
    df : pd.DataFrame
      input dataframe
    x : str or list
      quoted expressions to be plotted on the x axis
    group : str
      quoted expression to be used as group (ie color)
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

    # TODO: performance improvement
    # TODO: add support for categorical variables in x

    if position not in ['overlay', 'stack', 'dodge']:
        log.error("position not recognized")
        raise NotImplementedError("position not recognized")

    if (bins is None) and (bin_width is None):
        log.error("Either bins or bin_with should be defined")
        raise ValueError("Either bins or bin_with should be defined")

    if (bins is not None) and (bin_width is not None):
        log.error("Only one between bins or bin_with should be defined")
        raise ValueError("Only one between  bins or bin_with should be defined")

    if isinstance(x, str):
        x=[x]

    # create a copy of the data
    dataframe = df.copy()

    # define groups and variables; remove and store (eventual) names
    names = {}
    groups = {}
    variables = {}

    for label, var in zip(['group', 'facet_y'], [group, facet_y]):
        names[label], groups[label] = unname(var)
    xs = []
    for i, var in enumerate(x):
        xs.append('x_{}'.format(i))
        names['x_{}'.format(i)], groups['x_{}'.format(i)] = unname(var)
    names['w'], variables['w'] = unname(w)

    # set column names and evaluate expressions
    tmp_df = agg_data(dataframe, variables, groups, None, fill_groups=False)

    # redefine groups and variables; remove and store (eventual) names
    new_groups = {c:c for c in tmp_df.columns if c in ['group', 'facet_y'] + xs}
    non_x_groups = [g for g  in new_groups.keys() if g not in xs]

    # bin data (if necessary)
    bins_x={}
    bin_width_x={}
    for x in xs:
        if tmp_df[x].dtypes != np.dtype('O'):
            tmp_df[x], bins_x[x], bin_width_x[x]= bin_data(tmp_df[x], bins, bin_width)
        else:
            bin_width_x[x]=1

    # aggregate data and reorder columns
    df_ls=[]
    for x in xs:
        # aggregate data
        groups = {g:g for g in non_x_groups}
        groups[x] = x
        df = agg_data(tmp_df, variables, groups, 'sum', fill_groups=True)
        df.fillna(0, inplace=True)
        df['facet_x']=names[x]
        df.rename(columns={x:'x'}, inplace=True)

        # normalize
        if normalize:
            if len(non_x_groups)==0:
                df['w'] = df['w']/(df['w'].sum()*bin_width_x[x])
            else:
                df['w'] = df.groupby(non_x_groups)['w'].apply(lambda z: z/(z.sum()*bin_width_x[x]))

        df_ls.append(df)
    gdata = pd.concat(df_ls)
    gdata = gdata[[c for c in ['x', 'w', 'group', 'facet_x', 'facet_y'] if c in gdata.columns]]

    # start plotting
    g = EZPlot(gdata)

    # set groups
    for x in xs:
        var = names[x]
        if group is None:
            g += p9.geom_bar(p9.aes(x="x", y="w"),
                             data=gdata.query('facet_x==@var'),
                             stat = 'identity',
                             colour = None,
                             fill = ez_colors(1)[0])
        else:
            g += p9.geom_bar(p9.aes(x="x", y="w",
                                    group="factor(group)",
                                    fill="factor(group)"),
                             data=gdata.query('facet_x==@var'),
                             colour=None,
                             stat = 'identity',
                             **POSITION_KWARGS[position])
            g += p9.scale_fill_manual(values=ez_colors(g.n_groups('group')))

    # set facets
    if facet_y is None:
        g += p9.facet_wrap('~facet_x', scales='free')
    else:
        g += p9.facet_grid('facet_y~facet_x', scales='free')

    # set x scale
    g += p9.scale_x_continuous(labels=ez_labels)

    # set y scale
    g += p9.scale_y_continuous(labels=ez_labels)

    # set axis labels
    g += \
        p9.xlab('Value') + \
        p9.ylab('Counts')

    # set theme
    g += theme_ez(figure_size=figure_size,
                  base_size=base_size,
                  legend_title=p9.element_text(text=names['group'], size=base_size))

    if sort_groups:
        g += p9.guides(fill=p9.guide_legend(reverse=True))

    return g
