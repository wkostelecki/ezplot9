import plotnine as p9
from ezplot9.utilities.agg_data import agg_data
import pandas as pd

# line_plot(mtcars, x = "cyl", y = "carb") + ylab("Total Carburetors")
# line_plot(mtcars, x = "cyl", y = "1", points = True) + ylab("Count of Cars")
# line_plot(mtcars, "cyl", "1", "am")
def line_plot(df, x, y, group = None, size = 12, points = False):
  """
  Aggregates data in df and plots as a line chart.
  Parameters:
  df - dataframe
  x - quoted expression
  y - quoted expression
  group - quoted expression
  size - base size for theme_*
  points - Whether to overlay points on line (default is False)
  """
  gdata = agg_data(df, x, y, group)

  if group is None:
    g = (
      p9.ggplot(gdata) +
      p9.geom_line(p9.aes(x = "x", y = "y"))
    )
  else:
    g = (
      p9.ggplot(gdata) +
      p9.geom_line(p9.aes(x = "x", y = "y", group = "group", colour = "group"))
    )

  g = (
    g +
    p9.theme_bw(base_size = size) +
    p9.theme(legend_position = "top") +
    p9.xlab(x) +
    p9.ylab(y)
  )

  if points and group is None:
    g = g + p9.geom_point(p9.aes(x = "x", y = "y"), colour = "black")
  elif points:
    g = g + p9.geom_point(p9.aes(x = "x", y = "y", colour = "group"))

  return(g)



