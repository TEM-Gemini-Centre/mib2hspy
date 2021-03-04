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
