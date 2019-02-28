import plotnine as p9
from ..utilities.agg_data import agg_data
from ..utilities.utils import unname
from ..utilities.labellers import ez_labels
from ..utilities.colors import ez_colors
from ..utilities.themes import theme_ez
from .ezplot import EZPlot


def scatter_plot(df,
                 x,
                 y,
                 group = None,
                 facet_x = None,
                 facet_y = None,
                 base_size = 10,
                 figure_size = (6,3),
                 **kwargs):
    '''
    Aggregates data in df and plots as a scatter plot chart.

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
    **kwargs:
      additional kwargs passed to geom_point

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
    gdata = agg_data(dataframe, variables, groups, None, fill_groups=True)
    gdata = gdata[[c for c in ['x', 'y', 'group', 'facet_x', 'facet_y'] if c in gdata.columns]]

    # add group_x column
    if group is not None:
        gdata['group_x'] = gdata['group'].astype('str') + '_' + gdata['x'].astype(str)

    g = EZPlot(gdata)

    # set groups
    if group is None:
        g += p9.geom_point(p9.aes(x="x", y="y", group="factor(group)"),
                           colour = ez_colors(1)[0], **kwargs)
    else:
        g += p9.geom_point(p9.aes(x="x", y="y", group="factor(group)", color="factor(group)"), **kwargs)
        g += p9.scale_color_manual(values=ez_colors(g.n_groups('group')))

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
    if g.column_is_timestamp('y'):
        g += p9.scale_y_datetime()
    elif g.column_is_categorical('y'):
        g += p9.scale_y_discrete()
    else:
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



