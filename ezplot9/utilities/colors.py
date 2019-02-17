import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl

def ez_colors(n,
              hexadecimal=True):
    '''
    Generate the ez color palette with 'n' colors

    Parameters
    ----------
    n : integer
        number of colors to be generated
    hexadecimal : boolean
        use hexadecimal representation (otherwise RGB representation is used)

    Returns
    -------
    colors : array
        array with 'n' colors
    '''

    if n <= 10:
        # use the tab10 palette
        colors = plt.cm.tab10(np.linspace(0, 1, 10))[0:n,:]

    elif n <= 20:
        # use the tab10 palette with some extra colors from tab20
        to_fill = n - 10
        tmp = plt.cm.tab20(np.linspace(0, 1, 20))

        colors = plt.cm.tab10(np.linspace(0, 1, 10))

        for i in range(to_fill):
            colors = np.insert(colors, 2 * i + 1, tmp[2 * i + 1, :], axis=0)
    else:
        # interpolate tab20
        to_create = n - 20
        max_generation = to_create // 10 + 1
        n_max_generation = to_create % 10

        col20 = plt.cm.tab20(np.linspace(0, 1, 20))

        colors = []

        # colors spawn in the max generation
        for c in range(0, n_max_generation):
            delta = (col20[2 * c + 1, :] - col20[2 * c, :]) / (max_generation + 1)

            for j in range(0, max_generation + 2):
                colors.append(col20[2 * c, :] + j * delta)

        # colors spawn in the max generation-1
        for c in range(n_max_generation, 10):
            delta = (col20[2 * c + 1, :] - col20[2 * c, :]) / (max_generation)

            for j in range(0, max_generation + 1):
                colors.append(col20[2 * c, :] + j * delta)

        colors = np.array(colors)

    if hexadecimal:
        tmp=[]
        for col in colors:
            tmp.append(mpl.colors.rgb2hex(col))
        colors=tmp

    return colors

def display_colors(colors):

    '''
    Display an array of colors. This function is based on `seaborn.palplot`

    Parameters
    ----------
    colors: array of colors
        colors to be displayed

    Returns
    -------
    fig : figure
        figure displaying the colors
    '''

    fig = sns.palplot(colors)

    return fig

