import pandas as pd

def bin_data(x,
             bins=21,
             bin_width=None):
    '''
    Bin the values of a vector

    Parameters
    ----------
    x : array
        vector to be binned
    bins : int or None
        number of bins
    bin_width : float or None
        width of each bin

    Returns
    -------
    binned_x : array
        binnded version of the input

    '''
    max_val = x.max()
    min_val = x.min()

    if (bins is not None) and (bin_width is None):
        bin_width = (max_val - min_val) / (bins - 1)
        delta = 0.5 * bin_width
    elif (bins is None) and (bin_width is not None):
        bins = int((max_val - min_val) / bin_width) + 1
        delta = 0.5 * (max_val - min_val - bin_width * bins)
    else:
        log.error("Only one between nbins and bin_width should be defined")
        raise ValueError("Only one between nbins and binwidth should be defined")

    start_bin = min_val - delta
    bins_intervals = [start_bin + bin_width * i for i in range(bins + 1)]
    bins_labels = [min_val + bin_width * i for i in range(bins)]
    binned_x = pd.cut(x, bins=bins_intervals, labels=bins_labels)
    binned_x = binned_x.astype(float)

    return binned_x, bins, bin_width

def qbin_data(x,
              n_quantiles=20):
    '''
    Bin the values of a vector according to its quantiles

    Parameters
    ----------
    x : array
        vector to be binned
    n_quantiles : int
        number of quantiles to be used

    Returns
    -------
    binned_x : array
        binnded version of the input

    '''

    binned_x = pd.qcut(x, q=n_quantiles, duplicates='drop')
    rename_dict = \
        pd.DataFrame({'x':x, 'q_x':binned_x})\
        .groupby('q_x')['x']\
        .mean()\
        .to_dict()
    binned_x = binned_x.cat.rename_categories(rename_dict).astype(float)

    return binned_x