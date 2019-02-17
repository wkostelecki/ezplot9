import plotnine as p9
import numpy as np
import datetime
import pandas as pd

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
            return self.data[col].dtypes == np.dtype('O')

    def column_is_timestamp(self, col):
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
        n
            number of unique values

        '''
        return len(self.data[col].unique())