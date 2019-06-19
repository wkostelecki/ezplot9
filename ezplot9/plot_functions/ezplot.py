import plotnine as p9
import numpy as np
import datetime
import pandas as pd

from pandas.api.types import CategoricalDtype, is_categorical, is_bool_dtype

import logging
log = logging.getLogger(__name__)

class EZPlot(p9.ggplot):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

    def column_is_categorical(self, col):
        '''
        Check if a column in self.data is categorical or not

        Parameters
        ----------
        col : str
            column to check

        Returns
        -------
        flag : bool

        '''
        if col not in self.data.columns:
            log.error('{} is not present in the data'.format(col))
            raise ValueError('{} is not present in the data'.format(col))
        else:
            return (self.data[col].dtypes == np.dtype('O')) \
                   or is_bool_dtype(self.data[col].dtypes)\
                   or is_categorical(self.data[col].dtypes)

    def column_is_timestamp(self, col):
        '''
        Check if a column in self.data is timestamp or not

        Parameters
        ----------
        col : str
            column to check

        Returns
        -------
        flag : bool

        '''
        if col not in self.data.columns:
            log.error('{} is not present in the data'.format(col))
            raise ValueError('{} is not present in the data'.format(col))
        else:
            return type(self.data[col][0]) in [datetime.date, pd._libs.tslib.Timestamp]

    def n_groups(self, col):
        '''
        Check how many unique values there are in a column

        Parameters
        ----------
        col : str
            column to check

        Returns
        -------
        n : int
            number of unique values

        '''
        return len(self.data[col].unique())

    def sort_group(self, group_col, var_col, ascending=True):
        if group_col in self.data.columns:
            group_order_list = \
                self.data \
                .groupby(group_col)[var_col] \
                .sum() \
                .reset_index() \
                .sort_values(var_col, ascending=ascending)[group_col] \
                .to_list()

            group_cat = CategoricalDtype(categories=[str(v) for v in group_order_list], ordered=True)
            self.data[group_col] = self.data[group_col].astype(str).astype(group_cat)
