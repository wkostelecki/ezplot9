def ez_labels(x,
              signif=2):
    '''
    Convert a float to a more readable string using the `k` for 1,000, `m` for 1,000,000 and `b` for 1,000,000,000.

    Parameters
    ----------
    x : array
        number to be converted to label
    signif : integer, default is 2
        number of figures to be kept

    Returns
    -------
    labels : list of strings
        the input x converted to label

    '''

    labels = []
    for val in x:
        if abs(val)>=1e9:
            lab = '{:.{}f}b'.format(val/1e9,signif)
            lab = lab.replace('.' + '0' * signif, '')
        elif abs(val)>=1e6:
            lab = '{:.{}f}m'.format(val / 1e6,signif)
            lab = lab.replace('.' + '0' * signif, '')
        elif abs(val)>=1e3:
            lab = '{:.{}f}k'.format(val / 1e3,signif)
            lab = lab.replace('.' + '0' * signif, '')
        elif abs(val)>=1:
            lab = '{:.{}f}'.format( val, signif)
            lab = lab.replace('.' + '0' * signif, '')
        else:
            lab='{:.{}g}'.format(val,signif)

        labels.append(lab)

    return labels


def money_labels(x,
                 currency='$',
                 signif=2):
    '''
    Convert a float to a currency string.

    Parameters
    ----------
    x : array
        number to be converted to label
    currency : string
        currency unit
    signif : integer, default is 2
        number of figures to be kept

    Returns
    -------
    labels : list of strings
        the input x converted to label

    '''

    # get ez labels
    labels = ez_labels(x, signif)

    # add currency
    labels = [currency + l for l in labels]

    # fix minus signs
    labels = [l.replace(currency +'-', '-' + currency) for l in labels]

    return labels

def percent_labels(x,
                   signif=2):
    '''
    Convert a float to percentage string.

    Parameters
    ----------
    x : array
        number to be converted to label
    signif : integer, default is 2
        number of figures to be kept

    Returns
    -------
    labels : list of strings
        the input x converted to label
    '''

    labels = []

    for val in x:
        lab = '{:.{}f}%'.format(val*100,signif)
        if val>=10**(-signif):
            lab = lab.replace('.'+'0'*(signif), '')
        labels.append(lab)

    return labels

def bp_labels(x,
              signif=2):
    '''
    Convert a float to a string expressed in basis point (ie *10000).

    Parameters
    ----------
    x : array
        number to be converted to label
    signif : integer, default is 2
        number of figures to be kept

    Returns
    -------
    labels : list of strings
        the input x converted to label
    '''

    labels = []
    for val in x:
        lab = '{:.{}f}bp'.format(val*10000,signif)
        lab = lab.replace('.'+'0'*(signif), '')
        labels.append(lab)

    return labels