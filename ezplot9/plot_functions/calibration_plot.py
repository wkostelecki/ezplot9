import plotnine as p9
import numpy as np
import pandas as pd

from ..utilities.agg_data import agg_data
from ..utilities.utils import unname, sort_data_groups
from ..utilities.labellers import ez_labels, percent_labels
from ..utilities.colors import ez_colors
from ..utilities.themes import theme_ez
from ..utilities.binning import bin_data, qbin_data
from ..utilities.binning import bin_data, qbin_data
from .marginal_plot import marginal_plot
from .ci_plot import ci_plot

import logging
log = logging.getLogger(__name__)

def calibration_plot(df,
                     prob,
                     binary_target,
                     group = None,
                     facet_x = None,
                     facet_y = None,
                     bins=10,
                     use_quantiles = False,
                     label_pos='auto',
                     label_function=ez_labels,
                     sort_groups=True,
                     xy_range = ((0,1), (0,1)),
                     use_bootstrapping=False,
                     base_size=10,
                     figure_size=(6, 3)):
    '''
    Plot calibration curves for classification models

    Parameters
    ----------
    df
    prob : str
      quoted expression to be plotted on the x axis (ie confidence/probability from a fitted model)
    binary_target : str
      quoted expression to be plotted on the y axis (ie the binarized target that will be considered)
    group : str
      quoted expression to be used as group (ie color)
    facet_x : str
      quoted expression to be used as facet
    facet_y : str
      quoted expression to be used as facet
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

    if use_bootstrapping:

        # create a copy of the data
        dataframe = df.copy()

        # define groups and variables; remove and store (eventual) names
        names = {}
        groups = {}
        variables = {}

        for label, var in zip(['x', 'group', 'facet_x', 'facet_y'], [prob, group, facet_x, facet_y]):
            names[label], groups[label] = unname(var)
        names['y'], variables['y'] = unname(binary_target)

        # set column names and evaluate expressions
        tmp_df = agg_data(dataframe, variables, groups, None, fill_groups=False)

        # bin data
        if use_quantiles:
            quantile_groups = [c for c in tmp_df.columns if c in ['group', 'facet_x', 'facet_y']]
            if len(quantile_groups) > 0:
                tmp_df['x'] = tmp_df.groupby(quantile_groups)['x'].apply(lambda x: qbin_data(x, bins))
            else:
                tmp_df['x'] = qbin_data(tmp_df['x'], bins)
        else:
            tmp_df['x'], _, _ = bin_data(tmp_df['x'], bins, None)

        tmp_df.rename(columns = {'x':prob,
                                 'y':binary_target,
                                 'group':group,
                                 'facet_x':facet_x,
                                 'facet_y':facet_y},
                      inplace=True)

        g = ci_plot(tmp_df,
                    prob,
                    binary_target,
                    group = group,
                    facet_x = facet_x,
                    facet_y = facet_y,
                    base_size = base_size,
                    figure_size = figure_size,
                    num_iterations = 10_000,
                    geom = 'ribbon')

    else:

        g = marginal_plot(df,
                          prob,
                          binary_target,
                          group = group ,
                          facet_x = facet_x ,
                          facet_y = facet_y ,
                          aggfun = 'mean',
                          bins=bins,
                          use_quantiles =use_quantiles ,
                          label_pos=label_pos,
                          label_function=label_function,
                          sort_groups=sort_groups,
                          base_size=base_size,
                          figure_size=figure_size)

    g += p9.scale_x_continuous(labels=percent_labels, limits = xy_range[0])
    g += p9.scale_y_continuous(labels=percent_labels, limits = xy_range[1])
    g += p9.geom_line(p9.aes(x='guide_x', y='guide_y'),
                      data=pd.DataFrame(data={'guide_x':xy_range[0], 'guide_y':xy_range[1]}),
                      color = '#696969',
                      linetype = 'dashed')

    g += p9.xlab('Confidence') + \
         p9.ylab('Fraction of positives')

    return g