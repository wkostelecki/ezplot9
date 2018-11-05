import pandas as pd

def agg_data(df, x, y, group):

  # df.eval('__x = ' + x, inplace=True)
  # df.eval('__y = ' + y, inplace=True)
 
  df2 = pd.DataFrame(
    data = {
      "x": df.eval("x = " + x)["x"],
      "y": df.eval("y = " + y)["y"]
      }
  )

  if group is None:
    gdata = df2.groupby("x", as_index = False)["y"].sum()
  elif group is not None:
    df2["group"] = df.eval("group = " + group)["group"]
    gdata = df2.groupby(["x", "group"], as_index = False)["y"].sum()


  return(gdata)

