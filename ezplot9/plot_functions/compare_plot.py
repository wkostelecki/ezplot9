import plotnine as p9
import pandas as pd

from ..utilities.agg_data import agg_data
from ..utilities.utils import unname
from ..utilities.labellers import ez_labels
from ..utilities.colors import ez_colors
from ..utilities.themes import theme_ez
from .line_plot import line_plot
from .ezplot import EZPlot

import logging
log = logging.getLogger(__name__)


def compare_plot(df,
                 x,
                 y,
                 group = None,
                 facet_x = None,
                 facet_y = None,
                 aggfun = 'sum',
                 show_points = False,
                 base_size = 10,
                 figure_size = (6,3)):
    '''
    Aggregates data in df and plots multiple columns as a line chart.

    Parameters
    ----------
    df : pd.DataFrame
      input dataframe
    x : str
      quoted expression to be plotted on the x axis
    y : str or list of str
      quoted expression(s) to be plotted on the y axis
    group : str
      quoted expression to be used as group (ie color)
    facet_x : str
      quoted expression to be used as facet
    facet_y : str
      quoted expression to be used as facet
    aggfun : str or fun
      function to be used for aggregating (eg sum, mean, median ...)
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

    if isinstance(y, list):
        if group is not None and len(y)>1:
            log.error("groups can be specified only when a single y column is present")
            raise ValueError("groups can be specified only when a single y column is present")
        elif len(y)>1:
            # create a copy of the data
            dataframe = df.copy()

            # define groups and variables; remove and store (eventual) names
            names = {}
            groups = {}
            variables = {}

            for label, var in zip(['x', 'group', 'facet_x', 'facet_y'], [x, group, facet_x, facet_y]):
                names[label], groups[label] = unname(var)

            ys = []
            for i, var in enumerate(y):
                ys.append('y_{}'.format(i))
                names['y_{}'.format(i)], variables['y_{}'.format(i)] = unname(var)

            # fix special cases
            if x == '.index':
                groups['x'] = '.index'
                names['x'] = dataframe.index.name if dataframe.index.name is not None else ''

            # aggregate data and reorder columns
            gdata = agg_data(dataframe, variables, groups, aggfun, fill_groups=True)
            gdata = gdata[[c for c in ['x'] + ys + ['group', 'facet_x', 'facet_y'] if c in gdata.columns]]

            groups_present = [c for c in ['x', 'group', 'facet_x', 'facet_y'] if c in gdata.columns]
            melted_data = pd.melt(gdata, groups_present, var_name='variable', value_name='value')
            melted_data['variable'] = melted_data['variable'].replace({var:names[var] for var in ys})

            g = EZPlot(melted_data)

            g += p9.geom_line(p9.aes(x="x", y="value", group="factor(variable)", colour="factor(variable)"))
            if show_points:
                g += p9.geom_point(p9.aes(x="x", y="value", colour="factor(variable)"))
            g += p9.scale_color_manual(values=ez_colors(g.n_groups('variable')))

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
                p9.ylab('value')

            # set theme
            g += theme_ez(figure_size=figure_size,
                          base_size=base_size,
                          legend_title=p9.element_text(text='variable', size=base_size))

            return g

        else:
            g = line_plot(df, x, y[0], group, facet_x, facet_y, aggfun, show_points, base_size, figure_size)

            return g

    else:
        g = line_plot(df, x, y, group, facet_x, facet_y, aggfun, show_points, base_size, figure_size)

        return g
