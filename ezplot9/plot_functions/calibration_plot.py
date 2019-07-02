import plotnine as p9
import numpy as np
import pandas as pd

from ..utilities.agg_data import agg_data
from ..utilities.utils import unname, sort_data_groups
from ..utilities.labellers import ez_labels, percent_labels
from ..utilities.colors import ez_colors
from ..utilities.themes import theme_ez
from ..utilities.binning import bin_data, qbin_data
from .marginal_plot import marginal_plot

import logging
log = logging.getLogger(__name__)

def calibration_plot(df,
                     prob,
                     binary_target,
                     group = None,
                     facet_x = None,
                     facet_y = None,
                     bins=21,
                     use_quantiles = False,
                     label_pos='auto',
                     label_function=ez_labels,
                     sort_groups=True,
                     base_size=10,
                     figure_size=(6, 3)):

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

    g += p9.scale_x_continuous(labels=percent_labels)
    g += p9.scale_y_continuous(labels=percent_labels)
    g += p9.geom_line(p9.aes(x='guide_x', y='guide_y'),
                      data=pd.DataFrame(data={'guide_x':[0,1], 'guide_y':[0,1]}),
                      color = '#696969',
                      linetype = 'dashed')

    return g