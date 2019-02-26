from plotnine.themes.elements import element_line, element_rect, element_text
from plotnine.themes.theme import theme
from plotnine.themes.theme_gray import theme_gray
from .colors import ez_colors

STRIP_COLOR = ez_colors(1)[0]
class theme_ez(theme_gray):
    """
    White background with gray gridlines and colored strips

    Parameters
    ----------
    base_size : int, optional
        Base font size. All text sizes are a scaled versions of
        the base font size. Default is 11.
    base_family : str, optional
        Base font family.
    figure_size : tuple, optional
        Figure size
    """

    def __init__(self,
                 base_size=10,
                 base_family='DejaVu Sans',
                 figure_size = (6, 4),
                 **kwargs):

        super().__init__(base_size, base_family)

        self.add_theme(
            theme(figure_size = figure_size,
                  dpi=150,
                  panel_grid_major=element_line(size=0.9, alpha=1, color='0.9'),
                  panel_grid_minor=element_line(size=0.2, alpha=1, color='0.9'),
                  text = element_text(color='k', size=base_size*0.8),
                  strip_background = element_rect(color='k', fill=STRIP_COLOR, size=0.5, alpha=.95),
                  strip_text = element_text(weight='bold', color='w', size=base_size),
                  axis_title=element_text(color='k', size=base_size),
                  legend_key = element_rect(fill='w', color='w', size=0.5),
                  panel_border = element_rect(color='k', size=0.5),
                  plot_background = element_rect(fill='w'),
                  panel_background = element_rect(fill='w', alpha=.2),
                  axis_line = element_line(color='k', size=0.5),
                  **kwargs),
            inplace=True)
