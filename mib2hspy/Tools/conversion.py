from pathlib import Path
import hyperspy.api as hs
import pyxem as pxm
import numpy as np
import pandas as pd
from .hdrtools import MedipixHDRcontent
from .parameters import MicroscopeParameters
from math import nan, isnan


class Error(Exception):
    pass


class MIBError(Error):
    pass


class HDRError(Error):
    pass


class ReadError(Error):
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

        self.data_path = Path(data_path)
        self.data = None
        self.hdr = None
        self.calibrationtable = None

        if not isinstance(microscope_parameters, MicroscopeParameters):
            raise TypeError('Microscope parameters must be given as a MicroscopeParameters object, not {!r}'.format(
                microscope_parameters))
        self.microscope_parameters = microscope_parameters

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

    def calibrate(self, calibrationtable=None, print_results=False):
        """
        Calibrates the dataset based on a calibration file.

        :param calibrationtable: Calibration table to use for calibrating the data.
        :param print_results: Whether to print the results or not. Default is False
        :type calibrationfile: Union[None, str, Path]
        :type print_results: bool
        :return:
        """
        if calibrationtable is None and self.calibrationtable is None:
            raise CalibrationError('No calibrationtable set.')
        elif self.calibrationtable is None:
            if isinstance(calibrationtable, pd.DataFrame):
                self.calibrationtable = calibrationtable
            else:
                raise TypeError('Expected calibration table to be of type pandas.DataFrame, not {table!r}'.format(
                    table=calibrationtable))
        self.microscope_parameters.set_values_from_calibrationtable(self.calibrationtable, print_results=print_results)

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

        self.data.data = self.data.data.rechunk(chunks) #Rechunk the data.

    def downsample(self, bitdepth):
        """
        Downsample the data.

        :param bitdepth: The new bitdepth of the data.
        :type bitdepth: str
        :return:
        """

        if self.data is None:
            raise FileNotSetError('Cannot downsample data. File is not set.')

        #Add a check for curent bit depth. Consider blocking users for upsampling data?
        self.data = self.data.astype(bitdepth)

    def set_metadata(self):
        """
        Set the metadata of the signal

        :return:
        """
        return NotImplemented

        if self.data is None:
            raise FileNotSetError('Cannot set metadata. File is not set.')

        if self.microscope_parameters.acceleration_voltage.is_defined():
            self.data.beam_energy = self.microscope_parameters.acceleration_voltage.value
        if self.microscope_parameters.cameralength.is_defined():
            self.data.camera_length = self.microscope_parameters.cameralength.value()
        #if self.microscope_parameters.
        #WIP
