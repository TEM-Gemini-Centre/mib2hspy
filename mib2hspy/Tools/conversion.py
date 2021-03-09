from pathlib import Path
import hyperspy.api as hs
import pyxem as pxm
import numpy as np
import pandas as pd
from .hdrtools import MedipixHDRcontent
from .parameters import MicroscopeParameters
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


class Converter(object):
    """
    A converter object that converts a given .mib file into a .hspy file.
    """

    def __init__(self, data_path=None, microscope_parameters=MicroscopeParameters()):
        """
        Initialize a Converter object

        :param data_path: Path to the data to be converted
        :param microscope_parameters: microscope parameters to use as a basis for metadata and calibrations.
        :type data_path: Union[str, Path]
        :type microscope_parameters: MicroscopeParameters
        """

        self._data_path = Path(data_path)
        self._data = None
        self._hdr = None

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

    @data.setter
    def data(self, data):
        if data is None:
            self._data = None
        else:
            if not isinstance(data, hs.signals.BaseSignal):
                raise TypeError('Data {data} is not a hyperspy signal!'.format(data=data))
            self._data = data

    @property
    def hdr(self):
        return self._hdr

    @hdr.setter
    def hdr(self, hdr):
        if hdr is None:
            self._hdr = None
        else:
            if not isinstance(hdr, MedipixHDRcontent):
                raise TypeError('Header {hdr} is not a MedipixHDRcontent object!'.format(hdr=hdr))
            if self.data is None:
                warn('Setting header while the data is not set is not recommended')
            self._hdr = hdr

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
                        self.data = pxm.load_mib(str(self.data_path))
                    except Exception as e:
                        raise MIBError(e)
                    else:
                        try:
                            self.hdr = MedipixHDRcontent(self.data_path.with_suffix('.hdr'))
                        except Exception as e:
                            raise HDRError(e)
            else:
                raise FileExistsError('File "{self.data_path}" does not exist.'.format(self=self))
        except MIBError as e:
            self.data = None
        except HDRError as e:
            self.hdr = None
        except FileExistsError:
            self.data = None
            self.hdr = None
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
            max_value = self.data.max(axis=[0, 1, 2])
            return int(max_value.data[0])
        else:
            return nan

    def reshape(self, nx, ny, dx=256, dy=256):
        """
        Reshape the datastack.

        If either nx or ny are zero, data is reshaped into a single frame. This is used for converting single frames rather than stacks.

        :param nx: The fast scan dimension (px).
        :param ny: The slow scan dimension (px).
        :param dx: The detector size along horizontal (px). Default is 256
        :param dy: The detector size along vertical (px). Default is 256
        :type nx: int
        :type ny: int
        :type dx: int
        :type dy: int
        :return:
        """

        if self.data is None:
            raise FileNotSetError('Cannot reshape data. File is not set.')

        # Make sure dimensions are integers
        nx = int(nx)
        ny = int(ny)
        dx = int(dx)
        dy = int(dy)

        if nx == 0 or ny == 0:
            self.data = self.data.inav[0]
        elif nx > 0 and ny > 0:
            total_frames = nx * ny
            if not len(self.data) == total_frames:
                raise ValueError(
                    'The total number of frames in {self.data} does not match the number of scan pixels {n}'.format(
                        self=self, n=total_frames))

            # Reshape the data and convert new signal.
            self.data = pxm.LazyElectronDiffraction2D(
                self.data.data.reshape((nx, ny, dx, dy)))  # How to retain metadata?
        else:
            raise ValueError('Scan dimensions {x}x{y} are not valid.'.format(x=nx, y=ny))

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
                chunks = tuple([chunks] * len(self.data.shape))
            else:
                raise ValueError('Chunk size {chunks} is not a valid chunk size.'.format(chunks=chunks))

        chunks = tuple([int(chunk) for chunk in chunks])  # Make sure chunks is a tuple and contains integers.
        if not len(chunks) == len(self.data.shape):
            raise ValueError(
                'The number of chunks in {chunks!r} does not match the data shape {self.data!r}'.format(chunks=chunks,
                                                                                                        self=self))
        if not all([chunk > 0 for chunk in chunks]):
            raise ValueError('Chunks {chunks!r} contain non-positive chunk sizes.'.format(chunks=chunks))

        self.data.data = self.data.data.rechunk(chunks)  # Rechunk the data.

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
        self.data = self.data.astype(bitdepth)

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
            raise BlockfileError('Can only prepare blockfiles for ElectronDiffraction2D and LazyElectronDiffraction2D signal types, not {self.data!r}'.format(self=self))

        if not isinstance(self.data, pxm.LazyElectronDiffraction2D):
            warn('It is advised to prepare blockfiles based on lazy electron diffraction data, not {self.data}, as the process require copying the signal.'.format(self=self))

        if not len(self.data) == 2:
            raise BlockfileError(
                'Data must be a scan in order to convert into a blockfile. Length of data {self.data!r} is {l}'.format(
                    self=self, l=len(self.data)))

        #Deepcopy the data
        blo = self.data.deepcopy()

        if logarithmic:
            blo = np.log10(blo)
        if normalize_intensities:
            blo = blo / blo.max(axis=[0, 1, 2, 3]) * 255

        blo.axes_manager[2].scale = pixel_size * 1E4  # Convert pixel size in um to cm
        blo.axes_manager[3].scale = pixel_size * 1E4
        blo.axes_manager[2].units = 'cm'
        blo.axes_manager[3].units = 'cm'

        return blo

    def write(self, extension, overwrite=False, **kwargs):
        """
        Writes the file to the provided extension
        :param extension: The file type to create
        :type extension: str
        :param overwrite: Whether to overwrite existing data with the given extension
        :type overwrite: bool
        :param kwargs: Keyword arguments passed to auxiliary functions for preparation of various extensions such as Converter.prepare_blockfile()
        :return:
        """
        if self.data is not None:
            try:
                if extension == '.blo':
                    self.prepare_blockfile(**kwargs).write(self.data_path.with_suffix(extension), overwrite=overwrite)
                if extension in ['.hdf', '.hdf5', '.hspy']:
                    self.data.write(self.data_path.with_suffix(extension), overwrite=overwrite, chunks=self.data.data.chunks)
                else:
                    self.data.write(self.data_path.with_suffix(extension), overwrite=overwrite)
            except Exception as e:
                raise WriteError(e)
        else:
            raise WriteError('Can not write data before it is set!')
