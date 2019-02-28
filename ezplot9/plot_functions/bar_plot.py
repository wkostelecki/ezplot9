import plotnine as p9

import numpy as np

from ..utilities.agg_data import agg_data
from ..utilities.utils import unname
from ..utilities.labellers import ez_labels
from ..utilities.colors import ez_colors
from ..utilities.themes import theme_ez
from .ezplot import EZPlot

import logging
log = logging.getLogger(__name__)

POSITION_KWARGS = {'overlay':{'position':'identity', 'alpha':0.7},
                   'stack':{},
                   'dodge':{'position':'dodge'}}

def bar_plot(df,
             x,
             y,
             group = None,
             facet_x = None,
             facet_y = None,
             aggfun = 'sum',
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

  g = EZPlot(gdata)

  # determine order and create a categorical type
  if sort_groups:
    if g.column_is_categorical('x'):
      g.sort_group('x', 'y', ascending=False)
    g.sort_group('group', 'y')
    g.sort_group('facet_x', 'y', ascending=False)
    g.sort_group('facet_y', 'y', ascending=False)
    if groups:
      colors = np.flip(ez_colors(g.n_groups('group')))
  else:
    colors = ez_colors(g.n_groups('group'))


  # set groups
  if group is None:
    g += p9.geom_col(p9.aes(x="x", y="y"), fill = ez_colors(1)[0])
  else:
    g += p9.geom_col(p9.aes(x="x", y="y",
                            group="factor(group)",
                            fill="factor(group)"),
                     **POSITION_KWARGS[position])
    g += p9.scale_fill_manual(values=colors, reverse=False)

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
  g += p9.scale_y_continuous(labels=ez_labels,
                             expand=[0,0,0.1,0])

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

