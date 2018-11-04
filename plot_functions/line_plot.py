import plotnine as p9
from plotnine import ylab, xlab, theme
from plotnine.data import mtcars
import pandas as pd

# line_plot(mtcars, x = "cyl", y = "carb") + ylab("Total Carburetors")
# line_plot(mtcars, x = "cyl", y = "1", points = True) + ylab("Count of Cars")
def line_plot(df, x, y, size = 12, points = False):

  gdata = agg_data(df, x, y)

  g = (
    ggplot(gdata) +
    geom_line(aes(x = "x", y = "y"))
  )

  g = (
    g +
    theme_bw(base_size = size) +
    xlab(x) +
    ylab(y)
  )

  if points:
    g = g + geom_point(aes(x = "x", y = "y"))

  return(g)

def agg_data(df, x, y):

  df.eval('__x = ' + x, inplace=True)
  df.eval('__y = ' + y, inplace=True)
 
  df2 = pd.DataFrame(
    data = {
      "x": df.eval("x = " + x)["x"],
      "y": df.eval("y = " + y)["y"]
      }
  )

  gdata = df2.groupby("x", as_index = False)["y"].sum()

  return(gdata)

