from pathlib import Path
import hyperspy.api as hs
import pyxem as pxm
import numpy as np
from .hdrtools import MedipixHDRcontent


class Error(Exception):
    pass


class MIBError(Error):
    pass


class HDRError(Error):
    pass


class ReadError(Error):
    pass


class Converter(object):
    """
    A converter object that converts a given .mib file into a .hspy file.
    """

    def __init__(self, data_path=None):
        """
        Initialize a Converter object
        """

        self.data_path = Path(data_path)
        self.data = None
        self.hdr = None
        self.calibrationfile = None
        self.read_mib(self.data_path)

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

    def calibrate(self):
