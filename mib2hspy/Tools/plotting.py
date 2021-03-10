import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle


def find_decimals(number, max_places=10):
    """
    Return the number of decimals in a float
    :param number: The number to find decimal places in
    :param max_places: The maximum number of places to consider
    :return: The number of decimal points in the number
    :type number: float
    :type max_places: int
    :rtype: int
    """
    return np.argmin([number - round(number, decimals) for decimals in np.arange(0, max_places + 1, 1)])


def best_scalebar_length(length):
    """
    Return the best scalebar length for a desired scalebar length.

    Finds the closest "pretty" value for a desired scalebar length

    :param length: The desired length of the scalebar
    :type length: Union[int, float]
    :return: Pretty scalebar length
    :rtype: float
    """

    preset_lengths = np.hstack(
        (np.arange(0.01, 0.1, 0.01),
         np.arange(0.1, 1, 0.1),
         np.arange(1, 3, 0.5),
         np.arange(3, 11, 1),
         np.arange(15, 30, 5),
         np.arange(30, 100, 10),
         np.arange(100, 1100, 100))
    )

    return preset_lengths[np.argmin(np.abs(preset_lengths - length))]


def add_scalebar(ax, image_width, units, xy=(0.01, 0.01), height=0.02, relative_length=0.3, **kwargs):
    """
    Adds a scalebar to the axes

    :param ax: Axis to add scalebar to
    :param image_width: The width of the image, in scaled coordinates
    :param units: The units of the scale
    :param xy: The anchor point of the scalebar (lower left corner), in relative axis coordinates. Default is (0.01, 0.01)
    :param height: The height of the scalebar, in relative axis coordinates. Default is 0.01.
    :param relative_length: The preferred relative length of the scalebar. Default is 0.3.
    :param kwargs: Additional keyword arguments. Only fields `"rect_kwargs"` and `"text_kwargs"` will be used, and will be passed to matplotlib.patches.Rectangle and matplotlib.pyplot.text, respectively.
    :type ax: matplotlib.pyplot.Axes
    :type image_width: float
    :type units: str
    :type xy: tuple
    :type height: float
    :type relative_length: float
    :type kwargs: dict
    :return:
    """

    length = best_scalebar_length(image_width * relative_length)
    width = length / image_width
    rect_kwargs = {'color': 'w',
                   'transform': ax.transAxes}
    rect_kwargs.update(kwargs.get('rect_kwargs', {}))
    rect_kwargs.update({
        'width': width,
        'height': height}
    )
    scalebar = Rectangle(xy, **rect_kwargs)
    ax.add_patch(scalebar)

    text_kwargs = {
        'transform': ax.transAxes,
        'ha': 'center',
        'va': 'bottom',
        'color': 'w',
    }

    text_kwargs.update(kwargs.get('text_kwargs', {}))
    ax.text(xy[0] + width / 2, xy[1] + height,
            r'{l:.{decimals}f} {u}'.format(l=length, u=units, decimals=find_decimals(length)), **text_kwargs)