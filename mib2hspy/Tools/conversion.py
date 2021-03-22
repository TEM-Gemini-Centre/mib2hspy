from pathlib import Path
import hyperspy.api as hs
import pyxem as pxm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from .hdrtools import MedipixHDRcontent
from .parameters import MicroscopeParameters
from .plotting import add_scalebar
from math import nan, isnan
from warnings import warn


class Error(Exception):
    pass


class MIBError(Error):
    pass


class HDRError(Error):
    pass


class ReadError(Error):
    pass


class WriteError(Error):
    pass


class BlockfileError(Error):
    pass


class CalibrationError(Error):
    pass


class FileNotSetError(Error):
    pass


class ReshapeError(Error):
    pass


class DimensionError(Error):
    pass


class Converter(object):
    """
    A converter object that converts a given .mib file into a .hspy file.
    """

    def __init__(self, microscope_parameters=MicroscopeParameters()):
        """
        Initialize a Converter object

        :param microscope_parameters: microscope parameters to use as a basis for metadata and calibrations.
        :type microscope_parameters: MicroscopeParameters
        """
        self._data_path = None
        self._data = None
        self._hdr = None
        self._chunks = None  # Used for keeping track of the chunking being used.

        if not isinstance(microscope_parameters, MicroscopeParameters):
            raise TypeError('Microscope parameters must be given as a MicroscopeParameters object, not {!r}'.format(
                microscope_parameters))
        self.microscope_parameters = microscope_parameters

    def __repr__(self):
        return '{self.__class__.__name__}(data_path={self._data_path!r}, microscope_parameters={self._microscope_parameters!r})'.format(
            self=self)

    def __str__(self):
        return 'Converter for file "{self._data_path!s}" with data {self._data!s}:\n\n***Header content***\n{self._hdr!s}***\n\n***Microscope parameters***\n{self.microscope_parameters!s}'.format(
            self=self)

    @property
    def data(self):
        return self._data

    @property
    def hdr(self):
        return self._hdr

    @property
    def data_path(self):
        return self._data_path

    @data_path.setter
    def data_path(self, data_path):
        if data_path is None:
            self._data_path = None
            self._data = None
            self._hdr = None
        else:
            data_path = Path(data_path)
            if data_path.exists() and data_path.suffix == '.mib':
                if data_path == self._data_path:
                    pass
                else:
                    self._data_path = Path(data_path)
                    self._data = None
                    self._hdr = None

    @property
    def dimension(self):
        if self.data is not None:
            return int(len(np.shape(self.data)))
        else:
            return 0

    @property
    def frames(self):
        if self.data is not None:
            return int(len(self.data))
        else:
            return 0

    @property
    def ndx(self):
        if self.data is not None:
            return self.data.axes_manager[-2].size
        else:
            return 0

    @property
    def ndy(self):
        if self.data is not None:
            return self.data.axes_manager[-1].size
        else:
            return 0

    @property
    def nx(self):
        if self.dimension >= 3:
            return self.data.axes_manager[0].size
        else:
            return 0

    @property
    def ny(self):
        if self.dimension >= 4:
            return self.data.axes_manager[1].size
        else:
            return 0

    @property
    def image_extent(self):
        if self.data is not None:
            return [min(self.data.axes_manager[-2].axis), max(self.data.axes_manager[-2].axis),
                    min(self.data.axes_manager[-1].axis), max(self.data.axes_manager[-1].axis)]
        else:
            raise FileNotSetError('Cannot get image extent when data is not set.')

    @property
    def scan_extent(self):
        if self.dimension >= 4:
            return [min(self.data.axes_manager[0].axis), max(self.data.axes_manager[0].axis),
                    min(self.data.axes_manager[1].axis), max(self.data.axes_manager[1].axis)]
        else:
            raise DimensionError('Cannot get scan extent for data with dimension {self.dimension}'.format(self=self))

    def read_mib(self, data_path=None):
        """
        Read a MIB data file

        :param data_path: Path to the .mib file
        :type data_path: Union[str, Path]
        :return:
        """
        if data_path is not None:
            self.data_path = Path(data_path)
        try:
            if self.data_path.exists() and self.data_path.is_file():
                if self.data_path.suffix == '.mib':
                    try:
                        self._data = pxm.load_mib(str(self.data_path))
                    except Exception as e:
                        raise MIBError(e)
                    else:
                        try:
                            self._hdr = MedipixHDRcontent(self.data_path.with_suffix('.hdr'))
                            self._hdr.load_hdr()
                        except Exception as e:
                            raise HDRError(e)
            else:
                raise FileExistsError('File "{self.data_path}" does not exist.'.format(self=self))
        except MIBError as e:
            self._data = None
        except HDRError as e:
            self._hdr = None
        except FileExistsError:
            self._data = None
            self._hdr = None
        finally:
            if self.data is not None:
                print('Loaded file "{self.data_path}" successfully:\nData: {self.data}\nHDR: {self.hdr}'.format(
                    self=self))
            else:
                raise ReadError(
                    'File "{self.data_path}" was not loaded successfully:\nData: {self.data}\n HDR: {self.hdr}'.format(
                        self=self))

    def get_max_value(self):
        """
        Get the maximum value of the dataset.
        :return:
        """
        if self.data is not None:
            max_value = self.data.max(axis=np.arange(0, self.dimension))
            return int(max_value.data[0])
        else:
            return nan

    def reshape(self, nx=None, ny=None, dx=256, dy=256):
        """
        Reshape the datastack.

        If either nx or ny are zero, data is reshaped into a single frame. This is used for converting single frames rather than stacks.

        :param nx: The fast scan dimension (px). Default is None (attempts to work out the size based on the header content or data shape).
        :param ny: The slow scan dimension (px). Default is None (attempts to work out the size based on the header content or data shape).
        :param dx: The detector size along horizontal (px). Default is 256
        :param dy: The detector size along vertical (px). Default is 256
        :type nx: Union[int, NoneType]
        :type ny: Union[int, NoneType]
        :type dx: int
        :type dy: int
        :return:
        """

        if self.data is None:
            raise FileNotSetError('Cannot reshape data. File is not set.')

        if nx is None and ny is None:
            frames_per_trigger = int(self.hdr.frames_per_trigger)
            if frames_per_trigger > 1:
                # Assume line triggering
                nx = frames_per_trigger
                ny = self.frames / nx
            else:
                # Assume frame triggering. assume square data
                nx = int(np.sqrt(self.frames))
                ny = nx
        elif nx is None and ny is not None:
            ny = int(ny)
            nx = int(self.frames / ny)
        elif nx is not None and ny is None:
            nx = int(nx)
            ny = int(self.frames / nx)
        else:
            nx = int(nx)
            ny = int(ny)

        # Make sure dimensions are integers
        dx = int(dx)
        dy = int(dy)

        if self.frames == 1:
            self._data = self.data.inav[0]
        else:
            if nx < 0 or ny < 0:
                raise ReshapeError('Scan dimensions {x}x{y} are not valid.'.format(x=nx, y=ny))

            if not nx * ny == self.frames:
                raise ReshapeError(
                    'Cannot reshape {self.data} with {self.frames} into a {nx}x{ny} stack. Dimensions does not match'.format(
                        self=self, nx=nx, ny=ny))

            # Reshape the data and convert new signal.
            self._data = pxm.LazyElectronDiffraction2D(
                self.data.data.reshape((nx, ny, dx, dy)))  # How to retain metadata?

    def rechunk(self, chunks):
        """
        Rechunk the data.

        :param chunks: The chunks to use. If given as an integer, the same chunk size will be applied to all axes. If given as a typle, the length must match the signal dimensions.
        :return:
        """

        if self.data is None:
            raise FileNotSetError('Cannot rechunk data. File is not set.')

        if isinstance(chunks, int):
            if chunks > 0:
                chunks = tuple([chunks] * self.dimension)
            else:
                raise ValueError('Chunk size {chunks} is not a valid chunk size.'.format(chunks=chunks))

        chunks = tuple([int(chunk) for chunk in chunks])  # Make sure chunks is a tuple and contains integers.
        if not len(chunks) == self.dimension:
            raise ValueError(
                'The number of chunks in {chunks!r} does not match the data shape {self.data!r}'.format(chunks=chunks,
                                                                                                        self=self))
        if not all([chunk > 0 for chunk in chunks]):
            raise ValueError('Chunks {chunks!r} contain non-positive chunk sizes.'.format(chunks=chunks))

        self.data.data = self.data.data.rechunk(chunks)  # Rechunk the data.
        self._chunks = chunks  # Store the chunking that was used.

    def downsample(self, bitdepth):
        """
        Downsample the data.

        :param bitdepth: The new bitdepth of the data.
        :type bitdepth: str
        :return:
        """

        if self.data is None:
            raise FileNotSetError('Cannot downsample data. File is not set.')

        # Add a check for curent bit depth. Consider blocking users for upsampling data?
        self.data.data = self.data.data.astype(bitdepth)

    def set_metadata(self):
        """
        Set the metadata of the signal

        :return:
        """

        if self.data is None:
            raise FileNotSetError('Cannot set metadata. File is not set.')

        experimental_parameters = {
            'beam_energy': self.microscope_parameters.acceleration_voltage.value,
            'camera_length': self.microscope_parameters.cameralength.value,
            'convergence_angle': self.microscope_parameters.convergence_angle.value,
            'rocking_angle': self.microscope_parameters.rocking_angle.value,
            'rocking_frequency': self.microscope_parameters.rocking_frequency.value,
        }
        self.data.set_experimental_parameters(**experimental_parameters)

        # Store the microscope parameters in the original metadata as well.
        self.data.original_metadata.add_dictionary(
            {'Acquisition_instrument': {'Parameters': self.microscope_parameters.get_parameters_as_dict()}})

        if self.hdr is not None:
            self.data.original_metadata.add_dictionary({'Header': self.hdr.as_dict()})
        else:
            self.data.original_metadata.add_dictionary({'Header': None})

    def apply_calibrations(self):
        """
        Applies the microscope parameters to the signal axes to create a calibrated signal.
        :return:
        """
        if self.data is None:
            raise FileNotSetError('Cannot apply calibrations. File is not set.')
        # Set diffraction calibration
        if self.microscope_parameters.diffraction_scale.is_defined():
            self.data.set_diffraction_calibration(self.microscope_parameters.diffraction_scale.value)

        # Set scan calibration
        if self.microscope_parameters.scan_step_x.is_defined() and self.microscope_parameters.scan_step_y.is_defined():
            if self.microscope_parameters.scan_step_x.nominal_value == self.microscope_parameters.scan_step_y.nominal_value:
                self.data.set_scan_calibration(self.microscope_parameters.scan_step_x.value)
            else:
                self.data.axes_manager[0].scale = self.microscope_parameters.scan_step_x.value
                self.data.axes_manager[1].scale = self.microscope_parameters.scan_step_y.value
                self.data.axes_manager[0].units = self.microscope_parameters.scan_step_x.units
                self.data.axes_manager[1].units = self.microscope_parameters.scan_step_y.units

    def prepare_blockfile(self, normalize_intensities=True, logarithmic=True, pixel_size=55):
        """
        Prepare a signal suited for blockfile exportation.

        :param normalize_intensities: Whether to normalize the intensities (i.e. scale the intensities to 255). Default is True
        :param logarithmic: Whether to take the logarithm of the data before scaling or not. Default is True
        :param pixel_size: The pixel size of the camera in microns. Default is 55 um
        :type normalize_intensities: bool
        :type logarithmic: bool
        :type pixel_size: Union[int, float]
        :return: blo
        :rtype:
        """
        if self.data is None:
            raise FileNotSetError('Cannot prepare blockfile. File is not set.')

        if not isinstance(self.data, (pxm.ElectronDiffraction2D, pxm.LazyElectronDiffraction2D)):
            raise BlockfileError(
                'Can only prepare blockfiles for ElectronDiffraction2D and LazyElectronDiffraction2D signal types, not {self.data!r}'.format(
                    self=self))

        if not isinstance(self.data, pxm.LazyElectronDiffraction2D):
            warn(
                'It is advised to prepare blockfiles based on lazy electron diffraction data, not {self.data}, as the process require copying the signal.'.format(
                    self=self))

        if not self.dimension > 2:
            raise BlockfileError(
                'Data must be a scan in order to convert into a blockfile. Dimension of data {self.data!r} is {self.dimension}'.format(
                    self=self))

        # Deepcopy the data
        blo = self.data.deepcopy()

        if logarithmic:
            blo = np.log10(blo)
        if normalize_intensities:
            blo = blo / blo.max(axis=np.arange(0, self.dimension)) * 255

        blo.axes_manager[2].scale = pixel_size * 1E4  # Convert pixel size in um to cm
        blo.axes_manager[3].scale = pixel_size * 1E4
        blo.axes_manager[2].units = 'cm'
        blo.axes_manager[3].units = 'cm'

        return blo

    def prepare_figure(self, dpi=300, figure_width=3, scan=False):
        """
        Prepare a figure for plotting
        :param dpi: The resolution of the figure
        :param figure_width: The width of the figure in inches
        :type dpi: Union[int, float]
        :type figure_width: Union[int, float]
        :return: figure, axis
        """

        if self.data is not None:
            if scan:
                figsize = (figure_width, figure_width * self.ny / self.nx)
            else:
                figsize = (figure_width, figure_width * self.ndy / self.ndx)
        else:
            figsize = (figure_width, figure_width)

        fig = plt.figure(figsize=figsize, dpi=dpi, frameon=False)
        ax = fig.add_axes([0, 0, 1, 1], xticks=[], yticks=[], frameon=False)

        return fig, ax

    def plot_image(self, dpi=300, figure_width=3, logarithm=False, inav=None, scalebar=True, scalebar_kwargs=None,
                   **kwargs):
        """
        Prepare a plot/image of the data

        :param dpi: The DPI of the figure
        :param figure_width: The width of the figure in inches.
        :param logarithm: Whether to plot the logarithm of the data or not. Default is False
        :param inav: Which image to extract from a stack to plot. Only used if the data is a stack. Default is None, in which case the first image of the stack will be used.
        :param scalebar: Whether to add a scale bar or not.
        :param scalebar_kwargs: Keyword arguments to be used for creating scalebars in the plot.
        :param kwargs: Keyword arguments passed to mib2hspy.Tools.plotting.add_scalebar().
        :return: The figure containing the plot
        :rtype: matplotlib.pyplot.Figure
        :type dpi: float
        :type figure_width: float
        :type logarithm: bool
        :type inav: Union[NoneType, int, float, tuple, list]
        :type scalebar: bool
        :type scalebar_kwargs: Union[None, dict]
        :type kwargs: dict
        """

        if self.data is None:
            raise FileNotSetError('Cannot plot an image of the data for {self}. Data is not set.'.format(self=self))

        if scalebar_kwargs is None:
            scalebar_kwargs = {}

        if not self.frames == 1:
            warn('Preparing plots for a stack is not advised.')

        fig, ax = self.prepare_figure(dpi, figure_width)

        if self.dimension == 2:
            image = self.data.data
            units = self.data.axes_manager[0].units
        elif self.dimension == 3:
            if inav is None:
                warn(
                    'No navigation index provided when preparing plot for {self.data}. Using first image in stack'.format(
                        self=self))
                image = self.data.inav[0].data
            else:
                image = self.data.inav[inav].data
            units = self.data.axes_manager[1].units
        elif self.dimension == 4:
            if inav is None:
                warn(
                    'No navigation index provided when preparing plot for {self.data}. Using first image in stack'.format(
                        self=self))
                image = self.data.inav[0, 0].data
            else:
                image = self.data.inav[inav[0], inav[1]].data
            units = self.data.axes_manager[2].units
        else:
            raise DimensionError('Dimension {self.dimension} is not supported for plotting.'.format(self=self))

        if logarithm:
            image = np.log10(image)

        extent = self.image_extent
        image_kwargs = {'extent': extent}
        image_kwargs.update(kwargs)

        ax.imshow(image, **image_kwargs)
        if scalebar:
            add_scalebar(ax, abs(extent[1] - extent[0]), units=units, **scalebar_kwargs)

        return fig

    def plot_vbf(self, kind='box', vbf_kwargs=None, dpi=300, figure_width=3, scalebar=True, scalebar_kwargs=None,
                 **kwargs):
        """
        Plots a virtual bright field image of the data.

        :param kind: What kind of VBF to plot
        :param vbf_kwargs: Parameters passed to VBF getting function.
        :param dpi: The dpi of the figure
        :param figure_width: The width of the figure
        :param scalebar: Whether to add a scalebar or not
        :param scalebar_kwargs: Optional keyword arguments passed to scalebar function
        :param kwargs: Optional keyword arguments passed to matplotlib.pyplot.imshow
        :type kind: str
        :type vbf_kwargs: Union[None, dict]
        :type dpi: Union[int, float]
        :type figure_width: Union[int, float]
        :type scalebar: bool
        :type scalebar_kwargs: Union[None, dict]
        :type kwargs: dict
        :return: The created figure object
        :rtype: matplotlib.pyplot.Figure
        """
        if self.data is None:
            raise FileNotSetError('Cannot plot a VBF of the data for {self}. Data is not set.'.format(self=self))

        if scalebar_kwargs is None:
            scalebar_kwargs = {}

        if not self.dimension == 4:
            raise DimensionError('VBF images are not supported for {self.dimension}D data: {self.data}.'.format(self=self))

        fig, ax = self.prepare_figure(dpi, figure_width, scan=True)

        vbf = self.get_VBF(kind, **vbf_kwargs).data

        extent = self.scan_extent
        image_kwargs = {'extent': extent}
        image_kwargs.update(kwargs)

        ax.imshow(vbf, **image_kwargs)
        if scalebar:
            add_scalebar(ax, abs(extent[1] - extent[0]), units=self.data.axes_manager[0].units, **scalebar_kwargs)

        return fig

    def get_square_vbf(self, cx=None, cy=None, width=10):
        """
        Get an "inappropriate" VBF of the signal using a box around the central beam.

        :param cx: The centre position of the box along X.
        :param cy: The centre position of the box along Y.
        :param width: The width of the box.
        :return:
        """
        if cx is None:
            cx = self.data.axes_manager[-2].axis[int(self.data.axes_manager[-2].size / 2)]

        if cy is None:
            cy = self.data.axes_manager[-1].axis[int(self.data.axes_manager[-1].size / 2)]

        half_width = int(width / 2)
        if isinstance(cy, float) or isinstance(cx, float):
            half_width *= self.data.axes_manager[-2].scale

        return self.data.isig[cx - half_width:cx + half_width, cy - half_width:cy + half_width].sum(
            axis=np.arange(self.dimension - 2, self.dimension))

    def get_circular_VBF(self, cx=None, cy=None, r=10, r_inner=0):
        """
        Get a VBF signal using a circular mask.

        :param cx: Centre of mask.
        :param cy: Centre of mask.
        :param r: Radius of circle.
        :param r_inner: Inner radius of annular circle.
        :return:
        """
        if cx is None:
            cx = self.data.axes_manager[-2].axis[int(self.data.axes_manager[-2].size / 2)]

        if cy is None:
            cy = self.data.axes_manager[-1].axis[int(self.data.axes_manager[-1].size / 2)]

        if isinstance(cx, int):
            warn(
                'X coordinate of centre of circular aperture for VBF is given as an integer. Interpreting this as '
                'a pixel coordinate and transforming it into a scaled coordinate when determining the circle '
                'centre.')
            cx = self.data.axes_manager[-2].axis[cx]
        if isinstance(cx, int):
            warn(
                'Y coordinate of centre of circular aperture for VBF is given as an integer. Interpreting this as '
                'a pixel coordinate and transforming it into a scaled coordinate when determining the circle '
                'centre.')
            cy = self.data.axes_manager[-1].axis[cy]
        if isinstance(r, int):
            warn(
                'Outer radius of circular aperture for VBF is given as an integer. Interpreting this as '
                'a pixel coordinate and transforming it into a scaled coordinate when determining the circle '
                'radius.')
            r = r * self.data.axes_manager[-2].scale
        if isinstance(r_inner, int):
            warn(
                'Inner radius of circular aperture for VBF is given as an integer. Interpreting this as '
                'a pixel coordinate and transforming it into a scaled coordinate when determining the circle '
                'inner radius.')
            r_inner = r_inner * self.data.axes_manager[-2].scale
        return self.data.get_integrated_intensity(hs.roi.CircleROI(cx, cy, r, r_inner=r_inner))

    def get_VBF(self, kind, **kwargs):
        """
        get a virtual bright field of the data.

        :param kind: The kind of VBF. Should be either "box" or "circle".
        :param kwargs: Optional keyword arguments passed to VBF generation function (depends on the `kind` parameter)
        :return:
        """

        supported_types = ['box', 'circle']
        if self.data is None:
            raise FileNotSetError('Cannot plot VBF. File is not set.')

        if not self.frames > 1:
            warn('{self.data} has only {self.frames} frames. Preparing VBF will result in a single-pixel image')

        if kind == 'box':
            vbf = self.get_square_vbf(**kwargs)
        elif kind == 'circle':
            vbf = self.get_circular_VBF(**kwargs)
        else:
            raise ValueError(
                'VBF type {kind} is not among supported. Please use either of {supported_types}.'.format(kind=kind,
                                                                                                         supported_types=', '.join(
                                                                                                             supported_types)))

        if isinstance(vbf, (pxm.LazyElectronDiffraction2D, pxm.LazyElectronDiffraction1D)):
            vbf.compute(progressbar=False)

        if not (1 <= len(np.shape(vbf.data)) <= 2):
            raise DimensionError(
                'Dimension {self.dimension} of {self.data} is not suited for plotting VBF images'.format(self=self))
        return vbf

    def write(self, extension, overwrite=False, **kwargs):
        """
        Writes the file with the provided extension
        :param extension: The file type to create
        :type extension: str
        :param overwrite: Whether to overwrite existing data with the given extension
        :type overwrite: bool
        :param kwargs: Keyword arguments passed to auxiliary functions for preparation of various extensions such as Converter.prepare_blockfile()
        :return:
        """
        if self.data is not None:
            output_path = str(self.data_path.with_suffix(extension))
            try:
                if extension == '.blo':
                    self.prepare_blockfile(**kwargs).save(output_path, overwrite=overwrite)
                if extension in ['.hdf', '.hdf5', '.hspy']:
                    self.data.save(output_path, overwrite=overwrite, chunks=self._chunks)
                if extension in ['.png', '.jpg', '.tiff', '.tif']:
                    self.save_plot(extension, **kwargs)
                else:
                    self.data.save(output_path, overwrite=overwrite)
            except Exception as e:
                raise WriteError(e)
        else:
            raise WriteError('Can not write data before it is set!')

    def save_plot(self, extension='.png', toggle_prompt=False, **kwargs):
        try:
            inav = kwargs.pop('inav')
        except KeyError:
            inav = None

        try:
            num_frames = kwargs.pop('num_frames')
        except KeyError:
            num_frames = np.inf

        # Determine wich frames to extract.
        if self.frames > 1:  # is a stack
            if inav is None:  # If no frame index is provided
                warn(
                    '{self.data} contains a stack of images. Converting this data to {extension} is not advised as it will create {self.frames} files'.format(
                        self=self, extension=extension))
                if toggle_prompt:
                    if not input('Continue? [y]/n').lower() == 'y':
                        raise WriteError('Writing cancelled by user.')
                if self.dimension >= 3:
                    xs = np.arange(0, self.data.axes_manager[0].size)
                    if self.dimension == 4:
                        ys = np.arange(0, self.data.axes_manager[1].size)
                    else:
                        ys = None
                else:
                    xs = None
                    ys = None
            else:
                if isinstance(inav, (int, float)):
                    xs = [inav]
                    ys = None
                else:
                    xs = [int(inav[0])]
                    ys = [int(inav[1])]
        else:
            xs = None
            ys = None

        counter = 0
        if xs is None and ys is None:
            self.plot_image(**kwargs).savefig(self.data_path.with_suffix(extension))
        elif xs is not None and ys is None:
            for x in xs:
                self.plot_image(inav=x, **kwargs).savefig(self.data_path.with_name(
                    '{self.data_path.stem}_{x:07.0f}{extension}'.format(self=self, x=x, extension=extension)))
                plt.close('all')
                counter += 1
                if counter >= num_frames:
                    return 0
        elif xs is not None and ys is not None:
            for y in ys:
                for x in xs:
                    self.plot_image(inav=(x, y), **kwargs).savefig(self.data_path.with_name(
                        '{self.data_path.stem}_{x:06.0f}_{y:06.0f}{extension}'.format(self=self, x=x, y=y,
                                                                                      extension=extension)))
                    plt.close('all')
                    counter += 1
                    if counter >= num_frames:
                        return 0

        else:
            raise ValueError(
                'Could not determine which frame to plot for {self.data}. Attempted to pixk navigation inidces from {xs!r} and {ys!r}'.format(
                    self=self, xs=xs, ys=ys))
