import logging
import sys
from datetime import date
from math import sqrt, isnan
from pathlib import Path
from warnings import warn

import hyperspy.api as hs
import numpy as np
import pyxem as pxm
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, QDate
from tabulate import tabulate

# create logger
logger = logging.getLogger(f'{__file__}')
logger.propagate = False

logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


class Error(Exception):
    pass


class SaveSignalError(Error):
    pass


class SignalChunkError(Error):
    pass


class PixelSizeError(Error):
    pass


class StepSizeError(Error):
    pass


class SignalModelError(Error):
    pass


class SignalModel(QObject):
    """
    Model for setting Signal conversion parameters through a GUI
    """
    signalChanged = pyqtSignal([], [str])
    pathChanged = pyqtSignal([], [str], [Path])
    chunksChanged = pyqtSignal([], [tuple])
    shapeChanged = pyqtSignal([], [tuple])

    pixelSizeChanged = pyqtSignal([], [tuple])
    axesUnitsChanged = pyqtSignal([], [str, str, str, str])
    stepSizeChanged = pyqtSignal([], [tuple], [float, float])
    beamEnergyChanged = pyqtSignal([], [int], [float])
    cameralengthChanged = pyqtSignal([], [int], [float])
    precessionAngleChanged = pyqtSignal([], [int], [float])
    precessionFrequencyChanged = pyqtSignal([], [int], [float])
    exposureTimeChanged = pyqtSignal([], [int], [float])
    scanRotationChanged = pyqtSignal([], [int], [float])
    convergenceAngleChanged = pyqtSignal([], [int], [float])
    operatorChanged = pyqtSignal([], [str])
    specimenChanged = pyqtSignal([], [str])
    notesChanged = pyqtSignal([], [str])
    dateChanged = pyqtSignal([], [date])
    stageXChanged = pyqtSignal([], [float])
    stageYChanged = pyqtSignal([], [float])
    stageZChanged = pyqtSignal([], [float])
    stageAlphaChanged = pyqtSignal([], [float])
    stageBetaChanged = pyqtSignal([], [float])
    stageChanged = pyqtSignal([], [str])
    modeChanged = pyqtSignal([], [str])
    alphaChanged = pyqtSignal([], [int])
    spotChanged = pyqtSignal([], [int])
    spotsizeChanged = pyqtSignal([], [float])

    default_detector_shape = (256, 256)
    default_detector_pixel_size = (55E-4, 55E-4)  # Pixel size in cm
    default_chunk_size = 32
    default_step_size = (1., 1.)
    default_scan_units = 'px'
    default_diffraction_units = '$Å^{-1}$'
    default_axes_names = ('x', 'y', 'kx', 'ky')
    default_beam_energy = 200.
    default_cameralength = 0.
    default_precession_angle = 0.
    default_precession_frequency = 0.
    default_exposure_time = 0.
    default_scan_rotation = 0.
    default_convergence_angle = 0.

    # Auxilliary metadata
    default_notes = ''
    default_mode = 'None'
    default_alpha = 0
    default_specimen = 'None'
    default_operator = 'None'
    default_stage_x = 0.
    default_stage_y = 0.
    default_stage_z = 0.
    default_stage_alpha = 0.
    default_stage_beta = 0.
    default_stage = 'None'
    default_date = date.today()
    default_spotsize = 0.
    default_spot = 0

    supported_file_formats = ('hspy', 'hdf5', 'blo')
    supported_signal_types = (type(None), hs.signals.BaseSignal)

    @property
    def silent(self):
        """
        Get whether the model is silent (emitting gui-signals) or not
        :return:
        """
        return self._silent

    @silent.setter
    def silent(self, value):
        """
        Set whether the model is silent (emitting gui-signals) or not
        :param value: Whether the signal should be silent or not
        :type value: bool
        :return:
        """
        logger.debug(f'Setting {self.__class__.__name__}.silent={value!r}')
        self._silent = bool(value)
        self.blockSignals(self._silent)

    @property
    def signal(self):
        """
        Get the hyperspy signal associated with the model
        :return: The current signal associated with the model
        :rtype: Union[hyperspy.api.Signal, None]
        """
        return self._signal

    @signal.setter
    def signal(self, value):
        """
        Set the current hyperspy signal associated with the model
        :param value: The signal associated with the model
        :type value: Union[None, hyperspy.api.Signal]
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.signal={value!r}')
        if isinstance(value, self.supported_signal_types):
            self._signal = value
            self.signalChanged.emit()
        else:
            raise TypeError(
                f"Cannot set signal associated to model {self!r} to {value} of invalid type {type(value)}. Accepted types are {self.supported_signal_types}.")

    @property
    def path(self):
        """
        Get the path to the current dataset
        :return: The path to the current dataset
        :rtype: Union[None, Path]
        """
        return self._path

    @path.setter
    def path(self, value):
        """
        Set the path to the current .mib dataset.

        This will emit the pathChanged signal unless the model has been set to silent.

        :param value: A valid path to a .mib dataset.
        :type value: Union[Path, str]
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.path={value!r}')
        if isinstance(value, (str, Path)):
            path = Path(value)
            if path.is_file():
                if path.suffix == '.mib':
                    self._path = path
                    self.pathChanged.emit()
                    self.pathChanged[str].emit(str(self._path.absolute()))
                    self.pathChanged[Path].emit(self._path.absolute())
                else:
                    raise ValueError(f'Cannot set path to "{value!r}". Path is not a .mib file')
            else:
                raise ValueError(f'Cannot set path to "{value!r}". File does not exist')
        else:
            raise TypeError(f'Cannot set path to "{value!r}". Accepted types are strings and pathlib.Path objects')

    @property
    def chunks(self):
        """
        Get the current chunking that will be applied to the signal when converted.
        :return: chunks
        :rtype: tuple
        """
        return self._chunks

    @chunks.setter
    def chunks(self, value):
        """
        Set the chunking that will be applied to the signal when converted.
        :param value: The chunks
        :type value: tuple of size 4.
        :return:
        """
        logger.debug(f'Setting {self.__class__.__name__}.chunks={value!r}')
        if isinstance(value, (list, tuple)):
            self._chunks = value
            self.chunksChanged.emit()
        else:
            raise TypeError(
                f'Cannot set chunking to {value} of invalid type {type(value)}. Accepted types are `list` and `tuple`.')

    @property
    def nx(self):
        """
        Get the scan pixels along the x-direction to be applied to the converted signal.
        :return: The number of pixels along the x-direction.
        :rtype: int
        """
        return self.shape[0]

    @nx.setter
    def nx(self, value):
        """
        Set the scan pixels along the x-direction to be appllied to the converted signal.
        :param value: The number of pixels along the x-direction
        :type value: int
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.nx={value!r}')
        if isinstance(value, int):
            self.shape = (value, self.shape[1], self.shape[2], self.shape[3])
        else:
            raise TypeError(f'Cannot set nx of {self.signal} to {value}: only integers are accepted.')

    @property
    def ny(self):
        """
        Get the scan pixels along the y-direction to be applied to the converted signal.
        :return: The number of pixels along the y-direction.
        :rtype: int
        """
        return self.shape[1]

    @ny.setter
    def ny(self, value):
        """
        Set the scan pixels along the y-direction to be applied to the converted signal.
        :return: The number of pixels along the y-direction.
        :rtype: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.ny={value!r}')
        if isinstance(value, int):
            self.shape = (self.shape[0], value, self.shape[2], self.shape[3])
        else:
            raise TypeError(f'Cannot set ny of {self.signal} to {value}: only integers are accepted.')

    @property
    def ndx(self):
        """
        Get the detector pixels along the kx-direction to be applied to the converted signal.
        :return: The number of pixels along the kx-direction of the detector.
        :rtype: int
        """
        return self._shape[2]

    @ndx.setter
    def ndx(self, value):
        """
        Set the number of detector pixels along the kx-direction to be applied to the converted signal.
        :param value: The number of pixels along the kx-direction in the diffraction pattern.
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.ndx={value!r}')
        if isinstance(value, int):
            self.shape = (self.shape[0], self.shape[1], value, self.shape[3])
        else:
            raise TypeError(f'Cannot set ndx of {self.signal} to {value}: only integers are accepted.')

    @property
    def ndy(self):
        """
        Get the detector pixels along the ky-direction to be applied to the converted signal.
        :return: The number of pixels along the ky-direction of the detector.
        :rtype: int
        """
        return self._shape[3]

    @ndy.setter
    def ndy(self, value):
        """
        Set the number of detector pixels along the ky-direction to be applied to the converted signal.
        :param value: The number of pixels along the ky-direction in the diffraction pattern.
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.ndy={value!r}')
        if isinstance(value, int):
            self.shape = (self.shape[0], self.shape[1], self.shape[2], value)
        else:
            raise TypeError(f'Cannot set ndy of {self.signal} to {value}: only integers are accepted.')

    @property
    def shape(self):
        """
        Get the current shape that will be applied to the converted signal.
        :return: The shape of the signal.
        :rtype: tuple
        """
        return self._shape

    @shape.setter
    def shape(self, value):
        """
        Set the current shape that will be applied to the converted signal.
        :param value: The shape of the signal
        :type value: Union[tuple, list, np.ndarray]
        :return: None
        """
        if isinstance(value, (tuple, list, np.ndarray)):
            if np.shape(value) == (4,):
                if all([isinstance(val, int) for val in value]):
                    logger.debug(f'Setting {self.__class__.__name__}.shape={value!r}')
                    self._shape = tuple(value)
                    self.shapeChanged.emit()
                    self.shapeChanged[tuple].emit(self.shape)
                else:
                    raise TypeError(f'Cannot set shape of {self.signal} to {value}: Only integers are accepted')
            else:
                raise ValueError(
                    f'Cannot set shape of {self.signal}. {value} has invalid shape {np.shape(value)}. Accepted shape is (4,)')
        else:
            raise TypeError(
                f'Cannot set shape of {self.signal}. {value} has invalid type {type(value)}. Accepted types are tuples, lists, and numpy.ndarrays')

    @property
    def metadata(self):
        """
        Return the metadata of the current data signal.
        :return: The metadata of the current signal
        """
        try:
            return self.signal.metadata
        except AttributeError as e:
            raise AttributeError(f'Cannot access metadata of {self.signal}. Please assign a signal first.') from e

    @property
    def original_metadata(self):
        """
        Return the original metadata of the current data signal.
        :return: The original metadata of the current signal
        """
        try:
            return self.signal.original_metadata
        except AttributeError as e:
            raise AttributeError(
                f'Cannot access original metadata of {self.signal}. Please assign a signal first.') from e

    @property
    def axes_manager(self):
        """
        Return the axes manager of the current data signal.
        :return: The axes manager of the current signal.
        """
        try:
            return self.signal.axes_manager
        except AttributeError as e:
            raise AttributeError(f'Cannot access axes manager of {self.signal}. Please assign a signal firs') from e

    @property
    def pixel_size(self):
        """
        Return the physical pixel size/pitch of the detector.
        :return: The physical pixel size in m.
        """
        return self._pixel_size

    @pixel_size.setter
    def pixel_size(self, value):
        """
        Set the physical pixel size/pitch of the detector in two dimensions.
        :param value: pixel size in m in two dimensions
        :type value: Union[tuple, list, np.ndarray]
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.pixel_size={value!r}')
        if isinstance(value, (tuple, list, np.ndarray)):
            if np.shape(value) == (2,):
                if all([isinstance(val, (int, float)) or isnan(val) for val in value]):
                    self._pixel_size = tuple(value)
                    self.pixelSizeChanged.emit()
                else:
                    raise PixelSizeError(
                        f'Cannot set pixel size of {self.signal} to {value!r}.') from TypeError(
                        f': Invalid types {", ".join([type(val) for val in value])}. Types should be either `int` or `float`')
            else:
                raise PixelSizeError(
                    f'Cannot set pixel size of {self.signal} to {value!r}: invalid dimension {np.shape(value)}. Correct dimension is `(2,)`')

    @property
    def step_size(self):
        """
        Return the step size of the 2D scan.
        :return: step_sizes
        :rtype: 2-tuple
        """
        return self._step_size

    @property
    def step_size_x(self):
        """
        Return the step size along the x-direction of the scan.
        :return: x-direction stepsize
        :rtype: float
        """
        return self._step_size[0]

    @step_size_x.setter
    def step_size_x(self, value):
        """
        Set the step size along the x-direction of the scan.
        :param value: x-direction stepsize
        :type value: Union[int, float]
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.step_size_x={value!r}')
        if isinstance(value, (int, float)) or isnan(value):
            self._step_size = (float(value), self.step_size[1])
            self.stepSizeChanged.emit()
            self.stepSizeChanged[tuple].emit(self.step_size)
            self.stepSizeChanged[float, float].emit(self.step_size_x, self.step_size_y)
        else:
            raise TypeError(
                f'Cannot set x-step size of {self.signal} to {value!r}. Invalid type {type(value)}. Accepted types are `int` and `float`')

    @property
    def step_size_y(self):
        """
        Return the step size along the y-direction of the scan.
        :return: y-direction stepsize
        :rtype: float
        """
        return self._step_size[1]

    @step_size_y.setter
    def step_size_y(self, value):
        """
        Set the step size along the y-direction of the scan.
        :param value: y-direction stepsize
        :type value: Union[int, float]
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.step_size_y={value!r}')
        if isinstance(value, (int, float)) or isnan(value):
            self._step_size = (self.step_size[0], value)
            self.stepSizeChanged[tuple].emit(self.step_size)
            self.stepSizeChanged[float, float].emit(self.step_size_x, self.step_size_y)
        else:
            raise TypeError(
                f'Cannot set y-step size of {self.signal} to {value!r}. Invalid type {type(value)}. Accepted types are `int` and `float`')

    @property
    def axes_names(self):
        """
        Return the names of the axes to be used when converting the signal.
        :return:
        """
        return self._axes_names

    @axes_names.setter
    def axes_names(self, value):
        """
        Set the names of the axes to be used when converting the signal.
        :param value: names of the axes (x, y, kx, ky)
        :type value: Union[tuple, list, np.ndarray]
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.axes_names={value!r}')
        if isinstance(value, (tuple, list, np.ndarray)):
            if np.shape(value) == (4,):
                if all([isinstance(val, str) for val in value]):
                    self._axes_names = tuple(value)
                else:
                    raise TypeError(
                        f'Cannot set axes names of {self.signal} to {value!r}. Invalid types found in names: {", ".join([type(val) for val in value])}. Only `str` names are accepted.')
            else:
                raise ValueError(
                    f'Cannot set axes names of {self.signal} to {value!r}. Invalid shape {np.shape(value)}')
        else:
            raise TypeError(
                f'Cannot set axes names of {self.signal} to {value!r}. Expected an array.like object (tuple, list, or np.ndarray), but got {type(value)} instead.')

    @property
    def axes_units(self):
        """
        Return the axes units to be used when converting the signal
        :return: axes units
        :rtype: tuple
        """
        return self._axes_units

    @axes_units.setter
    def axes_units(self, value):
        """
        Set the units of the axes to be used when converting the signal.
        :param value: units of the axes (x, y, kx, ky)
        :type value: Union[tuple, list, np.ndarray]
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.axes_units={value!r}')
        if isinstance(value, (tuple, list, np.ndarray)):
            if np.shape(value) == (4,):
                if all([isinstance(val, str) for val in value]):
                    self._axes_units = value
                    self.axesUnitsChanged.emit()
                    self.axesUnitsChanged[str, str, str, str].emit(*self.axes_units)
                else:
                    raise TypeError(
                        f'Cannot set axes units of {self.signal} to {value!r}. Invalid types found in units: {", ".join([type(val) for val in value])}. Only `str` names are accepted.')
            else:
                raise ValueError(
                    f'Cannot set axes units of {self.signal} to {value!r}. Invalid shape {np.shape(value)}')
        else:
            raise TypeError(
                f'Cannot set axes units of {self.signal} to {value!r}. Expected an array.like object (tuple, list, or np.ndarray), but got {type(value)} instead.')

    @property
    def beam_energy(self):
        """
        Return the beam energy metadata
        :return: beam energy in kV
        :rtype: float
        """
        return self._beam_energy

    @beam_energy.setter
    def beam_energy(self, value):
        """
        Set the beam energy metadata.

        Values larger than 10000 will be interpreted as being given in Volts and be converted to kV before being set. Thus, if you actually have used higher acceleration voltages than 10 000 001 V, you will need to specify 10 000 001 000 as the acceleration voltage to circumvent the automatic unit conversion.
        :param value: beam energy in kV
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.beam_energy={value!r}')
        if isinstance(value, (int, float)):
            value = float(value)
            if value >= 0 or isnan(value):
                if value > 10000:
                    value = value / 1000  # Interpret value as volts and convert to kV
                self._beam_energy = value
                self.beamEnergyChanged.emit()
                self.beamEnergyChanged[float].emit(self.beam_energy)
            else:
                raise ValueError(f'Cannot set beam energy to {value} for {self.signal}. Only values >=0 are accepted.')
        else:
            raise TypeError(
                f'Cannot set beam energy to {value} for {self.signal}. Only integers and floats are accepted.')

    @property
    def cameralength(self):
        """
        Return the cameralength metadata
        :return: the cameralength in cm
        :rtype: float
        """
        return self._cameralength

    @cameralength.setter
    def cameralength(self, value):
        """
        Set the cameralength metadata
        :param value: the cameralength in cm
        :type value: float
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.cameralength={value!r}')
        if isinstance(value, (int, float)):
            value = float(value)
            if value >= 0 or isnan(value):
                self._cameralength = value
                self.cameralengthChanged.emit()
                self.cameralengthChanged[float].emit(self.cameralength)
            else:
                raise ValueError(f'Cannot set cameralength to {value} for {self.signal}. Only values >=0 are accepted.')
        else:
            raise TypeError(
                f'Cannot set cameralength to {value} for {self.signal}. Only integers and floats are accepted.')

    @property
    def precession_angle(self):
        """
        Return the precession angle metadata
        :return: the precession angle in degrees
        :rtype: float
        """
        return self._precession_angle

    @precession_angle.setter
    def precession_angle(self, value):
        """
        Set the precession angle metadata

        :param value: the precession angle in degrees
        :type value: float
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.precession_angle={value!r}')
        if isinstance(value, (int, float)):
            value = float(value)
            if value >= 0 or isnan(value):
                self._precession_angle = value
                self.precessionAngleChanged.emit()
                self.precessionAngleChanged[float].emit(self.precession_angle)
            else:
                raise ValueError(
                    f'Cannot set precession angle to {value} for {self.signal}. Only values >=0 are accepted.')
        else:
            raise TypeError(
                f'Cannot set precession angle to {value} for {self.signal}. Only integers and floats are accepted.')

    @property
    def precession_frequency(self):
        """
        Return the precession frequency metadata
        :return: the precession frequency in Hz
        :rtype: float
        """
        return self._precession_frequency

    @precession_frequency.setter
    def precession_frequency(self, value):
        """
        Set the precession frequency metadata
        :param value: the precession frequency in Hz
        :type value: float
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.precession_frequency={value!r}')
        if isinstance(value, (int, float)):
            value = float(value)
            if value >= 0 or isnan(value):
                self._precession_frequency = value
                self.precessionFrequencyChanged.emit()
                self.precessionFrequencyChanged[float].emit(self.precession_frequency)
            else:
                raise ValueError(
                    f'Cannot set precession frequency to {value} for {self.signal}. Only values >=0 are accepted.')
        else:
            raise TypeError(
                f'Cannot set precession frequency to {value} for {self.signal}. Only integers and floats are accepted.')

    @property
    def exposure_time(self):
        """
        Return the exposure time of the dataset frames
        :return: exposure time in ms
        :rtype: float
        """
        return self._exposure_time

    @exposure_time.setter
    def exposure_time(self, value):
        """
        Set the exposure time of the dataset frames
        :param value: exposure time in ms
        :type value: float
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.exposure_time={value!r}')
        if isinstance(value, (int, float)):
            value = float(value)
            if value >= 0 or isnan(value):
                self._exposure_time = value
                self.exposureTimeChanged.emit()
                self.exposureTimeChanged[float].emit(self.exposure_time)
            else:
                raise ValueError(
                    f'Cannot set exposure time to {value} for {self.signal}. Only values >=0 are accepted.')
        else:
            raise TypeError(
                f'Cannot set exposure time to {value} for {self.signal}. Only integers and floats are accepted.')

    @property
    def scan_rotation(self):
        """
        Return the scan rotation metadata of the dataset
        :return: scan rotation in degrees
        :rtype: float
        """
        return self._scan_rotation

    @scan_rotation.setter
    def scan_rotation(self, value):
        """
        Set the scan rotation metadata of the dataset.

        This should be the rotation used in the scan software, NOT the misorientation between the scan coordinates and the detector coordinates.

        This does not rotate any part of the data, it is only used as metadata.

        :param value: scan rotation in degrees.
        :type value: float
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.scan_rotation={value!r}')
        if isinstance(value, (int, float)):
            value = float(value)
            if 0 <= value <= 360 or isnan(value):
                self._scan_rotation = value
                self.scanRotationChanged.emit()
                self.scanRotationChanged[float].emit(self.scan_rotation)
            else:
                raise ValueError(
                    f'Cannot set scan rotation to {value} for {self.signal}. Only values between 0 and 360 are accepted.')
        else:
            raise TypeError(
                f'Cannot set scan rotation to {value} for {self.signal}. Only integers and floats are accepted.')

    @property
    def convergence_angle(self):
        """
        Return the convergence semi-angle metadata of the dataset.

        :return: convergence semi-angle in mrad
        :rtype: float
        """
        return self._convergence_angle

    @convergence_angle.setter
    def convergence_angle(self, value):
        """
        Set the convergence semi-angle metadata of the dataset
        :param value: convergence semi-angle in mrad
        :type value: float
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.convergence_angle={value!r}')
        if isinstance(value, (int, float)):
            value = float(value)
            if 0 <= value or isnan(value):
                self._convergence_angle = value
                self.convergenceAngleChanged.emit()
                self.convergenceAngleChanged[float].emit(self.convergence_angle)
            else:
                raise ValueError(
                    f'Cannot set convergence angle to {value} for {self.signal}. Only values between 0 and 360 are accepted.')
        else:
            raise TypeError(
                f'Cannot set convergence angle to {value} for {self.signal}. Only integers and floats are accepted.')

    @property
    def operator(self):
        """
        Return the operator metadata.
        :return: operator metadata string
        :rtype: str
        """
        return self._operator

    @operator.setter
    def operator(self, value):
        """
        Set the operator metadata.
        :param value: operator name
        :type value: str
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.operator={value!r}')
        if isinstance(value, str):
            self._operator = value
            self.operatorChanged.emit()
            self.operatorChanged[str].emit(self.operator)
        else:
            raise TypeError(f'Cannot set operator to {value} for {self.signal}. Only strings are accepted')

    @property
    def specimen(self):
        """
        Return the specimen metadata string
        :return: specimen name/label
        :rtype: str
        """
        return self._specimen

    @specimen.setter
    def specimen(self, value):
        """
        Set the specimen metadata string
        :param value: specimen name/label
        :type value: str
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.specimen={value!r}')
        if isinstance(value, str):
            self._specimen = value
            self.specimenChanged.emit()
            self.specimenChanged[str].emit(self.specimen)
        else:
            raise TypeError(f'Cannot set specimen to {value} for {self.signal}. Only strings are accepted')

    @property
    def notes(self):
        """
        Return the notes metadata string
        :return: experimental notes
        :rtype: str
        """
        return self._notes

    @notes.setter
    def notes(self, value):
        """
        Set the notes metadata string
        :param value: experimental notes
        :type value: str
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.notes={value!r}')
        if isinstance(value, str):
            self._notes = value
            self.notesChanged.emit()
            self.notesChanged[str].emit(self.notes)
        else:
            raise TypeError(f'Cannot set notes to {value} for {self.signal}. Only strings are accepted')

    @property
    def date(self):
        """
        Return the date metadata of the experiment
        :return: the date of the experiment
        :rtype: datetime.date
        """
        return self._date

    @date.setter
    def date(self, value):
        """
        Set the date metadata of the experiment
        :param value: the date of the experiment
        :type value: Union[str, datetime.date, QDate]
        :return:
        """
        logger.debug(f'Setting {self.__class__.__name__}.date={value!r}')
        if isinstance(value, str):
            self._date = date.fromisoformat(value)
            self.dateChanged.emit()
            self.dateChanged[date].emit(self.date)
        elif isinstance(value, date):
            self._date = value
            self.dateChanged.emit()
            self.dateChanged[date].emit(self.date)
        elif isinstance(value, QDate):
            self._date = date(value.year(), value.month(), value.day())
        else:
            raise TypeError(
                f'Cannot set date to {value} for {self.signal}. Only strings and datetime.date objects are accepted')

    @property
    def stage_x(self):
        """
        Return the stage x-position metadata
        :return: stage x-position in microns
        :rtype: float
        """
        return self._stage_x

    @stage_x.setter
    def stage_x(self, value):
        """
        Set the stage x-position metadata
        :param value: stage x-position in microns
        :type value: Union[int, float]
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.stage_x={value!r}')
        if isinstance(value, (int, float)) or isnan(value):
            self._stage_x = float(value)
            self.stageXChanged.emit()
            self.stageXChanged[float].emit(self.stage_x)
        else:
            raise TypeError(
                f'Cannot set stage x position to {value} for {self.signal}. Only integers and floats are accepted')

    @property
    def stage_y(self):
        """
        Return the stage y-position metadata
        :return: stage y-position in microns
        :rtype: float
        """
        return self._stage_y

    @stage_y.setter
    def stage_y(self, value):
        """
        Set the stage y-position metadata
        :param value: stage y-position in microns
        :type value: Union[int, float]
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.stage_y={value!r}')
        if isinstance(value, (int, float)) or isnan(value):
            self._stage_y = float(value)
            self.stageYChanged.emit()
            self.stageYChanged[float].emit(self.stage_y)
        else:
            raise TypeError(
                f'Cannot set stage y position to {value} for {self.signal}. Only integers and floats are accepted')

    @property
    def stage_z(self):
        """
        Return the stage z-position metadata
        :return: stage z-position in microns
        :rtype: float
        """
        return self._stage_z

    @stage_z.setter
    def stage_z(self, value):
        """
        Set the stage z-position metadata
        :param value: stage z-position in microns
        :type value: Union[int, float]
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.stage_z={value!r}')
        if isinstance(value, (int, float)) or isnan(value):
            self._stage_z = float(value)
            self.stageZChanged.emit()
            self.stageZChanged[float].emit(self.stage_z)
        else:
            raise TypeError(
                f'Cannot set stage z position to {value} for {self.signal}. Only integers and floats are accepted')

    @property
    def stage_alpha(self):
        """
        Return the stage alpha tilt metadata
        :return: stage alpha tilt in degrees
        :rtype: float
        """
        return self._stage_alpha

    @stage_alpha.setter
    def stage_alpha(self, value):
        """
        Set the stage alpha tilt metadata
        :param value: stage alpha tilt in degrees
        :type value: Union[int, float]
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.stage_alpha={value!r}')
        if isinstance(value, (int, float)) or isnan(value):
            self._stage_alpha = float(value)
            self.stageAlphaChanged.emit()
            self.stageAlphaChanged[float].emit(self.stage_alpha)
        else:
            raise TypeError(
                f'Cannot set stage alpha position to {value} for {self.signal}. Only integers and floats are accepted')

    @property
    def stage_beta(self):
        """
        Return the stage beta tilt metadata.

        Corresponds to the rotation of a rotation holder.

        :return: stage beta tilt in degrees
        :rtype: float
        """
        return self._stage_beta

    @stage_beta.setter
    def stage_beta(self, value):
        """
        Set the stage beta tilt metadata
        :param value: stage beta tilt in degrees
        :type value: Union[int, float]
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.stage_beta={value!r}')
        if isinstance(value, (int, float)) or isnan(value):
            self._stage_beta = float(value)
            self.stageBetaChanged.emit()
            self.stageBetaChanged[float].emit(self.stage_beta)
        else:
            raise TypeError(
                f'Cannot set stage beta position to {value} for {self.signal}. Only integers and floats are accepted')

    @property
    def stage(self):
        """
        Return the stage name metadata
        :return: stage name
        :rtype: str
        """
        return self._stage

    @stage.setter
    def stage(self, value):
        """
        Set the stage name metadata
        :param value: stage name
        :type value: str
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.stage={value!r}')
        if isinstance(value, str):
            self._stage = value
            self.stageChanged.emit()
            self.stageChanged[str].emit(self.stage)
        else:
            raise TypeError(
                f'Cannot set stage to {value} for {self.signal}. Only strings are accepted')

    @property
    def mode(self):
        """
        Return the mode of the microscope
        :return: mode
        :rtype: str
        """
        return self._mode

    @mode.setter
    def mode(self, value):
        """
        Set the mode of the microscope
        :param value: mode
        :type value: str
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.mode={value!r}')
        if isinstance(value, str):
            self._mode = value
            self.modeChanged.emit()
            self.modeChanged[str].emit(self.mode)
        else:
            raise TypeError(f'Cannot set mode to {value} for {self.signal}. Only strings are accepted')

    @property
    def alpha(self):
        """
        Return the alpha-setting of the microscope
        :return: alpha-setting
        :rtype: int
        """
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        """
        Set the alpha-setting of the microscope

        The alpha-setting corresponds to the condenser mini-lens power setting on JEOL microscopes.

        :param value: alpha-setting
        :type value: int
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.alpha={value!r}')
        if isinstance(value, int):
            self._alpha = value
            self.alphaChanged.emit()
            self.alphaChanged[int].emit(self.alpha)
        else:
            raise TypeError(f'Cannot set alpha to {value} for {self.signal}. Only integers are accepted')

    @property
    def spot(self):
        """
        Return the spot-setting of the microscope
        :return: spot setting
        :rtype: int
        """
        return self._spot

    @spot.setter
    def spot(self, value):
        """
        Set the spot-setting of the microscope.
        :param value: spot setting
        :type value: int
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.spot={value!r}')
        if isinstance(value, int):
            self._spot = value
            self.spotChanged.emit()
            self.spotChanged[int].emit(self.spot)
        else:
            raise TypeError(f'Cannot set spot to {value} for {self.signal}. Only integers are accepted')

    @property
    def spotsize(self):
        """
        Return the spotsize setting of the microscope
        :return: nominal spotsize setting in nm
        :rtype: float
        """
        return self._spotsize

    @spotsize.setter
    def spotsize(self, value):
        """
        Set the spotsize setting of the microscope

        :param value: spotsize in nm
        :type value: float
        :return: None
        """
        logger.debug(f'Setting {self.__class__.__name__}.spotsize={value!r}')
        if isinstance(value, float) or isnan(value):
            self._spotsize = value
            self.spotsizeChanged.emit()
            self.spotsizeChanged[float].emit(self.spotsize)
        else:
            raise TypeError(f'Cannot set spotsize to {value} for {self.signal}. Only floats are accepted')

    def __init__(self, *args, **kwargs):
        """
        Create a model for handling signal conversion.

        :param args: optional positional arguments passed to QObject init
        :param kwargs: Optional keyword argument spassed to QObject init
        """
        super(SignalModel, self).__init__(*args, **kwargs)

        self._signal = None
        self._path = None
        self._silent = False

        # Required conversion parameters
        self._chunks = (1, 1, 1, 1)
        self._shape = (1, 1, 1, 1)
        self._pixel_size = (1, 1)
        self._step_size = (1, 1)
        self._axes_names = ('', '', '', '')
        self._axes_units = ('', '', '', '')

        # Metadata parameters
        self._beam_energy = 0.
        self._cameralength = 0.
        self._precession_angle = 0.
        self._precession_frequency = 0.
        self._exposure_time = 0.
        self._scan_rotation = 0.
        self._convergence_angle = 0.
        self._operator = ''
        self._specimen = ''
        self._notes = ''
        self._date = date.today()
        self._stage_x = 0.
        self._stage_y = 0.
        self._stage_z = 0.
        self._stage_alpha = 0.
        self._stage_beta = 0.
        self._stage = ''
        self._mode = ''
        self._alpha = 0
        self._spotsize = 0.
        self._spot = 0

        self.set_defaults()

    def set_defaults(self):
        """
        Reset parameters and metadata to default values.

        It is advised to set `silent` to False before running this function to ensure GUI updates.

        :return:
        """
        self.chunks = (
            self.default_chunk_size,
            self.default_chunk_size,
            self.default_chunk_size,
            self.default_chunk_size
        )
        self.shape = (1, 1) + self.default_detector_shape
        self.pixel_size = self.default_detector_pixel_size
        self.step_size_x = self.default_step_size[0]
        self.step_size_y = self.default_step_size[1]
        self.axes_names = self.default_axes_names
        self.axes_units = (self.default_scan_units, self.default_scan_units, self.default_diffraction_units,
                           self.default_diffraction_units)

        # Metadata parameters
        self.beam_energy = self.default_beam_energy
        self.cameralength = self.default_cameralength
        self.precession_angle = self.default_precession_angle
        self.precession_frequency = self.default_precession_frequency
        self.exposure_time = self.default_exposure_time
        self.scan_rotation = self.default_scan_rotation
        self.convergence_angle = self.default_convergence_angle
        self.operator = self.default_operator
        self.specimen = self.default_specimen
        self.notes = self.default_notes
        self.date = self.default_date
        self.stage_x = self.default_stage_x
        self.stage_y = self.default_stage_y
        self.stage_z = self.default_stage_z
        self.stage_alpha = self.default_stage_alpha
        self.stage_beta = self.default_stage_beta
        self.stage = self.default_stage
        self.mode = self.default_mode
        self.alpha = self.default_alpha
        self.spotsize = self.default_spotsize
        self.spot = self.default_spot

    def __str__(self):
        s = '\n\t'.join([
            f'Signal:\n\t\t{self.signal}',
            f'Path:\n\t\t{self.path}',
            f'Silent:\n\t\t{self.silent}',
            f'Chunks:\n\t\t{self.chunks}',
            f'Shape:\n\t\t{self.shape}',
            f'Pixel size:\n\t\t{self.pixel_size}',
            f'Step size:\n\t\t{self.step_size}',
            f'Axes names:\n\t\t{self.axes_names}',
            f'Axes units:\n\t\t{self.axes_units}',
            f'Beam energy:\n\t\t{self.beam_energy}',
            f'Cameralength:\n\t\t{self.cameralength}',
            f'Precession angle:\n\t\t{self.precession_angle}',
            f'Precession frequency:\n\t\t{self.precession_frequency}',
            f'Exposure time:\n\t\t{self.exposure_time}',
            f'Scan rotation:\n\t\t{self.scan_rotation}',
            f'Convergence angle:\n\t\t{self.convergence_angle}',
            f'Operator:\n\t\t{self.operator}',
            f'Specimen:\n\t\t{self.specimen}',
            f'Notes:\n\t\t{self.notes}',
            f'Date:\n\t\t{self.date}',
            f'Stage X:\n\t\t{self.stage_x}',
            f'Stage Y:\n\t\t{self.stage_y}',
            f'Stage Z:\n\t\t{self.stage_z}',
            f'Stage alpha:\n\t\t{self.stage_alpha}',
            f'Stage beta:\n\t\t{self.stage_beta}',
            f'Stage:\n\t\t{self.stage}',
            f'Mode:\n\t\t{self.mode}',
            f'Alpha:\n\t\t{self.alpha}',
            f'Spotsize:\n\t\t{self.spotsize}',
            f'Spot:\n\t\t{self.spot}',
        ])
        return f'{self.__class__.__name__}:\n\t{s}'


class SignalController(QObject):
    """
    Controller object for signal conversion
    """
    _cameralengths = {200:
        {
            8: 16.20,
            10: 19.64,
            12: 22.95,
            15: 28.16,
            20: 36.14,
            25: 44.75,
            30: 53.44,
            40: 70.33,
            50: 88.71,
            60: 107.28,
            80: 140.66
        }}

    def __init__(self, model, *args, **kwargs):
        """
        Create a controller object for controling signal conversion through a GUI

        :param model: The conversion model object to control
        :type model: SignalModel
        :param args: Optional positional arguments passed to QObject init
        :param kwargs: Optional keyword arguments passed to QObject init
        """
        super(SignalController, self).__init__(*args, **kwargs)
        if not isinstance(model, SignalModel):
            raise TypeError(
                f'Cannot create {self.__class__.__name__} for {model!r}. Invalid type {type(model)}. Accepted types are `SignalModel` and subclasses')
        self._model = model

    @pyqtSlot(tuple)
    def setShape(self, value):
        """
        Set the shape to use when converting the model data stack
        :param value: the shape
        :type value: tuple
        :return:
        """
        self._model.shape = value

    @pyqtSlot(int)
    def setNX(self, value):
        """
        Set the number of scan pixels along x-scan direction
        :param value: pixels in x-direction
        :type value: int
        :return:
        """
        self._model.nx = value

    @pyqtSlot(int)
    def setNY(self, value):
        """
        Set the number of scan pixels along y-scan direction
        :param value: pixels in y-direction
        :type value: int
        :return:
        """
        self._model.ny = value

    @pyqtSlot(int)
    def setNdX(self, value):
        """
        Set the number of pixels along kx-direction of detector
        :param value: pixels in kx-direction
        :type value: int
        :return:
        """
        self._model.ndx = value

    @pyqtSlot(int)
    def setNdY(self, value):
        """
        Set the number of pixels along ky-direction of detector
        :param value: pixels in ky-direction
        :type value: int
        :return:
        """
        self._model.ndy = value

    @pyqtSlot(tuple)
    def setChunks(self, value):
        """
        Set the chunks to use when rechunking the data during conversion.
        :param value: the chunks to use for each dimension of the dataset
        :type value: tuple
        :return:
        """
        self._model.chunks = value

    @pyqtSlot(int, int)
    def setChunk(self, ax, value):
        """
        Set the number of chunks to use for a specific axis when rechunking the data during conversion.
        :param ax: The axis that the chunking applies to
        :param value: The number of chunks to use
        :type ax: int
        :type value: int
        :return:
        """
        if 0 <= ax <= 3:
            chunks = list(self._model.chunks)
            chunks[ax] = value
            self._model.chunks = tuple(chunks)
        else:
            raise SignalChunkError(
                f'Cannot set chunksize of axis {ax} to {value} for signal {self._model.signal}: Axis must be in range (0, 3)')

    @pyqtSlot(pxm.signals.ElectronDiffraction2D)
    @pyqtSlot(pxm.signals.LazyElectronDiffraction2D)
    def setSignal(self, value):
        """
        Set the dataset to convert
        :param value: the dataset signal
        :type value: Union[pxm.signals.ElectronDiffraction2D, pxm.signals.LazyElectronDiffraction2D]
        :return:
        """
        self._model.signal = value

    @pyqtSlot(str)
    @pyqtSlot(Path)
    def setPath(self, value):
        """
        Set the path to the dataset to convert from/to.

        This path will also be used to write the converted signals to, with a different suffix.
        :param value: path to raw .mib dataset.
        :type value: Union[str, Path]
        :return:
        """
        self._model.path = value

    @pyqtSlot(list, bool)
    @pyqtSlot(list, bool)
    def saveSignal(self, extensions, overwrite):
        """
        Convert and save the dataset
        :param extensions: the file types to convert to given as a list of strings
        :param overwrite: whether to overwrite existing files or not
        :type extensions: list
        :type overwrite: bool
        :return:
        """
        logger.info(f'Converting signal {self._model.signal} to [{", ".join(extensions)}]')
        try:
            if self._model.signal is None:
                raise SaveSignalError(f'Cannot save signal {self._model.signal!r}. Please assign/load signal first.')
            else:
                self.apply_metadata_fields()
                data = self._model.signal.data
                frames = len(self._model.signal)
                scan_dim = float(self._model.shape[0] * self._model.shape[1])
                logger.debug(f'Signal has {frames} frames.')
                if scan_dim != frames:
                    raise SaveSignalError(
                        f'Cannot save signal {self._model.signal!r}. Number of frames {frames} does not match specified scan shape {scan_dim}')
                else:

                    # Reshape
                    logger.debug(f'Reshaping data to {self._model.shape}')
                    data = data.reshape(self._model.shape)

                    # Rechunk
                    logger.debug(f'Rechunking data to {self._model.chunks}')
                    data = data.rechunk(self._model.chunks)

                    # Create new signal
                    logger.debug(f'Creating new signal')
                    s = pxm.signals.LazyElectronDiffraction2D(data)
                    logger.debug(f'Created signal {s}')

                    # Add metadata
                    logger.debug(f'Adding {self._model.metadata.as_dictionary()} as metadata to new signal')
                    s.metadata.add_dictionary(self._model.metadata.as_dictionary())
                    logger.debug(
                        f'Adding {self._model.original_metadata.as_dictionary()} as original metadata to new signal')
                    s.original_metadata.add_dictionary(self._model.signal.original_metadata.as_dictionary())

                    # Loop through extensions and save the signal
                    for extension in extensions:
                        logger.info(f'Preparing {extension}-type signal')
                        if not isinstance(extension, str):
                            raise SaveSignalError(
                                f'Cannot save signal {s!r} as a {extension} file. File extension is not among supported file types ({", ".join(self._model.supported_file_formats)})')
                        p = self._model.path.with_suffix(extension).absolute()
                        if extension == '.blo':
                            s = self.make_blo(s, True)
                            logger.info(f'Writing signal to "{p}"')
                            s.save(str(p), overwrite=overwrite)
                        elif extension in ['.hspy', '.hdf5']:
                            s = self.make_hspy(s)
                            logger.info(f'Writing signal to "{p}" with chunks={self._model.chunks}')
                            s.save(str(p), overwrite=overwrite, chunks=self._model.chunks)
                        else:
                            raise NotImplementedError(f'File conversion to {extension} is not supported.')
                    logger.info(f'Finished converting signals')
        except Exception as e:
            logger.error(e, exc_info=True)

    @pyqtSlot()
    def reset(self):
        """
        Reset the model being controlled by the controller.
        :return:
        """
        logger.debug('Resetting data')
        self._model.signal = None
        self._model.set_defaults()

    @pyqtSlot()
    def readSignal(self):
        """
        Load the signal.

        Loads the .mib signal (and .hdr file) corresponding to the current path.
        :return:
        """
        try:
            logger.debug(f'Reading signal {self._model.path.absolute()}')
            self._model.signal = pxm.load_mib(str(self._model.path))
            try:
                logger.debug(f'Reading header {self._model.path.with_suffix(".hdr").absolute()}')
                header = load_hdr(self._model.path.with_suffix('.hdr'))
                try:
                    header_date = header['Time and Date Stamp (day, mnth, yr, hr, min, s)']
                    logger.debug(f'Extracted date information from header: {header_date}')
                    day, mnth, yr = header_date.split(' ')[0].split('/')
                    logger.debug(f'Header date decomposed to (day, mnth, yr): ({day}, {mnth}, {yr})')
                    logger.debug(f'Setting date based on header content')
                    self.setDate(date(int(yr), int(mnth), int(day)))
                except KeyError as e:
                    logger.debug(f'Could not extract date from header!', exc_info=True)
            except FileNotFoundError as e:
                logger.info(
                    f'Cannot read .hdr data for {self._model.path.absolute()}:\n{e}\nIgnoring error and continuing.')
            else:
                self._model.signal.metadata.add_dictionary({'HDR': header})
                self._model.signal.original_metadata.add_dictionary({'HDR': header})
        except Exception as e:
            logger.error(e, exc_info=True)

    @pyqtSlot(float)
    def setCameralength(self, value):
        """
        Set the cameralength of the model.

        :param value: cameralength
        :type value: float
        :return:
        """
        self._model.cameralength = value

    @pyqtSlot(float)
    def setBeamEnergy(self, value):
        """
        Set the beam energy of the model
        :param value: beam energy
        :type value: float
        :return:
        """
        self._model.beam_energy = value

    @pyqtSlot(float)
    def setPrecessionAngle(self, value):
        """
        Set the precession angle of the model
        :param value: precession angle
        :type value: float
        :return:
        """
        self._model.precession_angle = value

    @pyqtSlot(float)
    def setPrecessionFrequency(self, value):
        """
        Set the precession frequency of the model
        :param value: precession frequency
        :type value: float
        :return:
        """
        self._model.precession_frequency = value

    @pyqtSlot(float)
    def setConvergenceAngle(self, value):
        """
        Set the convergence semi-angle of the model
        :param value: convergence semi-angle
        :type value: float
        :return:
        """
        self._model.convergence_angle = value

    @pyqtSlot(float)
    def setExposureTime(self, value):
        """
        Set the exposure time of the scan frames
        :param value: exposure time
        :type value: float
        :return:
        """
        self._model.exposure_time = value

    @pyqtSlot(str)
    def setMode(self, value):
        """
        Set the mode setting of the microscope
        :param value: the mode setting
        :type value: str
        :return:
        """
        self._model.mode = value

    @pyqtSlot(int)
    def setAlpha(self, value):
        """
        Set the alpha setting of the microscope
        :param value: the alpha setting
        :type value: int
        :return:
        """
        self._model.alpha = value

    @pyqtSlot(str)
    def setOperator(self, value):
        """
        Set the operator metadata
        :param value: the operator name
        :type value: str
        :return:
        """
        self._model.operator = value

    @pyqtSlot(str)
    def setSpecimen(self, value):
        """
        Set the specimen name/label
        :param value: the specimen name/label
        :type value: str
        :return:
        """
        self._model.specimen = value

    @pyqtSlot(str)
    def setNotes(self, value):
        """
        Set the notes metadata of the model.

        This will only change the notes if the new notes are different from the old notes.

        :param value: the notes
        :type value: str
        :return:
        """
        if value != self._model.notes:
            self._model.notes = value
        else:
            logger.debug(f'New notes matches old notes "{self._model.notes}", skipping setting notes to "{value}"')

    @pyqtSlot(float)
    def setStageX(self, value):
        """
        Set the stage metadata x-position
        :param value: x-position
        :type value: float
        :return:
        """
        self._model.stage_x = value

    @pyqtSlot(float)
    def setStageY(self, value):
        """
        Set the stage metadata y-position
        :param value: y-position
        :type value: float
        :return:
        """
        self._model.stage_y = value

    @pyqtSlot(float)
    def setStageZ(self, value):
        """
        Set the stage metadata z-position
        :param value: z-position
        :type value: float
        :return:
        """
        self._model.stage_z = value

    @pyqtSlot(float)
    def setStageAlpha(self, value):
        """
        Set the stage metadata alpha tilt
        :param value: alpha tilt
        :type value: float
        :return:
        """
        self._model.stage_alpha = value

    @pyqtSlot(float)
    def setStageBeta(self, value):
        """
        Set the stage metadata beta tilt
        :param value: beta tilt
        :type value: float
        :return:
        """
        self._model.stage_beta = value

    @pyqtSlot(str)
    def setStage(self, value):
        """
        Set the stage name metadata
        :param value: name
        :type value: str
        :return:
        """
        self._model.stage = value

    @pyqtSlot(float)
    def setSpotsize(self, value):
        """
        Set the nominal spotsize metadata
        :param value: nominal spotsize
        :type value: float
        :return:
        """
        self._model.spotsize = value

    @pyqtSlot(int)
    def setSpot(self, value):
        """
        Set the spot setting of the microscope
        :param value: spot-setting
        :type value: int
        :return:
        """
        self._model.spot = value

    @pyqtSlot(QDate)
    def setDate(self, value):
        """
        Set the date of the experiment
        :param value: the data of the experiment
        :type value: QDate
        :return:
        """
        self._model.date = value

    @pyqtSlot(float)
    def setScanRotation(self, value):
        """
        Set the scan rotation.

        This should be the rotation used in the scan software, NOT the misorientation between the scan coordinates and the detector coordinates.
        :param value: scan rotation
        :type value: float
        :return:
        """
        self._model.scan_rotation = value

    @pyqtSlot(float)
    def setStepSizeX(self, value):
        """
        Set the scan step size in the x-direction of the scan
        :param value: scan x-step size
        :type value: float
        :return:
        """
        self._model.step_size_x = value

    @pyqtSlot(str)
    def setStepUnitX(self, value):
        """
        Set the unit of the step size in the x-direction of the scan

        :param value: step size unit
        :type value: str
        :return:
        """
        self._model.axes_units = (
            value, self._model.axes_units[1], self._model.axes_units[2], self._model.axes_units[3])

    @pyqtSlot(float)
    def setStepSizeY(self, value):
        """
        Set the scan step size in the y-direction of the scan
        :param value: scan y-step size
        :type value: float
        :return:
        """
        self._model.step_size_y = value

    @pyqtSlot(str)
    def setStepUnitY(self, value):
        """
        Set the unit of the step size in the y-direction of the scan

        :param value: step size unit
        :type value: str
        :return:
        """
        self._model.axes_units = (
            self._model.axes_units[0], value, self._model.axes_units[2], self._model.axes_units[3])

    @pyqtSlot(float, float)
    def setStepSize(self, value_x, value_y):
        """
        Set the step sizes of the 2D scan.

        Using this to set the step sizes will not emit any signals from the model. (Why?)

        :param value_x: the scan step size along x
        :param value_y: the scan step size along y
        :type value_x: float
        :type value_y: float
        :return:
        """
        if self._model.silent:
            self.setStepSizeX(value_x)
            self.setStepSizeY(value_y)
        else:
            self._model.silent = True
            self.setStepSizeX(value_x)
            self.setStepSizeY(value_y)
            self._model.silent = False

    @pyqtSlot()
    def calibrateCameralength(self):
        """
        Calibrate the cameralength based on controller cameralength dictionary
        :return:
        """
        logger.debug(f'Calibration cameralength from {self._model.cameralength} cm at {self._model.beam_energy} kV')
        try:
            actual_cameralength = self._cameralengths[self._model.beam_energy][self._model.cameralength]
        except KeyError as e:
            logger.error(e, exc_info=True)
        else:
            logger.debug(f'Found matching calibration {actual_cameralength}')
            self.setCameralength(actual_cameralength)

    @pyqtSlot()
    def printSelf(self):
        """
        Print the model
        :return:
        """
        logger.info(str(self._model))

    def apply_metadata_fields(self):
        """
        Apply metadata fields and experimental parameters to the signal.
        :return:
        """
        if isinstance(self._model.signal, (pxm.signals.LazyElectronDiffraction2D, pxm.signals.ElectronDiffraction2D)):
            metadata = {
                'Acquisition_instrument': {
                    'TEM': {
                        'mode': self._model.mode,
                        'alpha': self._model.alpha,
                        'spot': self._model.spot,
                        'spotsize': self._model.spotsize,
                        'rotation': self._model.scan_rotation,
                        'stage': {
                            'x': self._model.stage_x,
                            'y': self._model.stage_y,
                            'z': self._model.stage_z,
                            'alpha': self._model.stage_alpha,
                            'beta': self._model.stage_beta,
                            'stage': self._model.stage
                        }
                    },
                },
                'General': {
                    'operator': self._model.operator,
                    'specimen': self._model.specimen,
                    'date': self._model.date.strftime('%Y-%m-%d')
                }
            }
            try:
                self._model.signal.metadata.add_dictionary(metadata)
            except AttributeError as e:
                raise AttributeError(
                    f'Cannot add metadata dictionary {metadata} to {self._model.signal}. Please assign a signal first.') from e

            try:
                self._model.signal.original_metadata.add_dictionary(metadata)
            except AttributeError as e:
                raise AttributeError(
                    f'Cannot add original metadata dictionary {metadata} to {self._model.signal}. Please assign a signal first.') from e

            self._model.signal.set_experimental_parameters(
                beam_energy=self._model.beam_energy,
                camera_length=self._model.cameralength,
                exposure_time=self._model.exposure_time,
                convergence_angle=self._model.convergence_angle,
                rocking_angle=self._model.precession_angle,
                rocking_frequency=self._model.precession_frequency,
                scan_rotation=self._model.scan_rotation
            )
        else:
            if self._model.signal is None:
                raise SaveSignalError(f'Cannot convert signal {self._model.signal}: please load data first.')
            else:
                raise SaveSignalError(f'Cannot convert signal {self._model.signal}: signal type is not supported.')

    def make_hspy(self, signal):
        """
        Set appropriate axes parameters for a signal

        The signal should already be reshaped to (x, y | kx, ky) and rechunked.

        :param signal: The signal to set the axes for. Works inplace, but also returns the signal.
        :type signal: Union[pyxem.signals.ElectronDiffraction2D, pyxem.signals.LazyElectronDiffraction2D]
        :return: The same signal, but with modified axes.
        :rtype: Union[pyxem.signals.ElectronDiffraction2D, pyxem.signals.LazyElectronDiffraction2D]
        """
        try:
            dx = cameralength2scale(
                signal.metadata.Acquisition_instrument.TEM.Detector.Diffraction.camera_length,
                signal.metadata.Acquisition_instrument.TEM.beam_energy,
                self._model.pixel_size[0])
        except ZeroDivisionError as e:
            dx = 1.0
            unit_x = 'px'
            logger.debug(
                f'Could not calculate diffraction scale for x-direction. Proceeding using non-calibrated scale {dx} {unit_x}',
                exc_info=True)

        else:
            unit_x = self._model.axes_units[-2]
            logger.debug(f'Using diffraction scale {dx} {unit_x} for x-direction')

        try:
            dy = cameralength2scale(
                signal.metadata.Acquisition_instrument.TEM.Detector.Diffraction.camera_length,
                signal.metadata.Acquisition_instrument.TEM.beam_energy,
                self._model.pixel_size[1])
        except ZeroDivisionError as e:
            dy = 1.0
            unit_y = 'px'
            logger.debug(
                f'Could not calculate diffraction scale for y-direction. Proceeding using non-calibrated scale {dy} {unit_y}',
                exc_info=True)
        else:
            unit_y = self._model.axes_units[-1]
            logger.debug(f'Using diffraction scale {dy} {unit_y} for y-direction')

        scales = [self._model.step_size_x, self._model.step_size_y, dx, dy]
        offsets = [0., 0., -dx * signal.axes_manager[-2].size / 2, -dy * signal.axes_manager[-1].size / 2]
        units = self._model.axes_units[0:2] + (unit_x, unit_y)

        for ax_no, (name, scale, offset, unit) in enumerate(
                zip(self._model._axes_names, scales, offsets, units)):
            logger.debug(
                f'Setting axis parameters for axis number {ax_no}: \n{tabulate([[name, scale, offset, unit]], headers=("name", "scale", "offset", "units"))}')
            signal.axes_manager[ax_no].name = name
            signal.axes_manager[ax_no].scale = scale
            signal.axes_manager[ax_no].offset = offset
            signal.axes_manager[ax_no].units = unit

        return signal

    def make_blo(self, signal, logarithmic=True):
        """
        Set appropriate axes parameters for a signal for blockfile writing.

        The signal should already be reshaped to (x, y | kx, ky) and rechunked.

        The limits of the data will be scaled to 8-bit.

        :param signal: The signal to prepare for blockfile writing.
        :type signal: Union[pyxem.signals.ElectronDiffraction2D, pyxem.signals.LazyElectronDiffraction2D]
        :param logarithmic: Whether to compute the logarithm of the diffraction patterns or not.
        :type logarithmic: bool
        :return: The same signal, but with modified axes and intensities.
        :rtype: Union[pyxem.signals.ElectronDiffraction2D, pyxem.signals.LazyElectronDiffraction2D]
        """
        blo_signal = signal.deepcopy()
        if logarithmic:
            blo_signal = pxm.signals.ElectronDiffraction2D(np.log(blo_signal + 1).data)
            blo_signal.metadata.add_dictionary(signal.metadata.as_dictionary())
            blo_signal.original_metadata.add_dictionary(signal.original_metadata.as_dictionary())
            parameters = {
                'beam_energy': None,
                'camera_length': None,
                'rocking_angle': None,
                'rocking_frequency': None,
                'exposure_time': None,
            }
            for parameter in parameters:
                try:
                    if parameter == 'camera_length':
                        parameters[parameter] = \
                            signal.metadata.as_dictionary()['Acquisition_instrument']['TEM']['Detector']['Diffraction'][
                                parameter]
                    elif parameter == 'exposure_time':
                        parameters[parameter] = \
                            signal.metadata.as_dictionary()['Acquisition_instrument']['TEM']['Detector']['Diffraction'][
                                parameter]
                    else:
                        parameters[parameter] = signal.metadata.as_dictionary()['Acquisition_instrument']['TEM'][
                            parameter]
                except KeyError as e:
                    warn(
                        f'Cannot set metadata parameter {parameter} for {signal} when converting {self._model.signal} to .blo. Got the following error:\n{e}\nIgnoring error and continuing...')
            blo_signal.set_experimental_parameters(**parameters)
        else:
            pass

        # Convert to 8-bit and scale intensities between minimum and maximum.
        blo_signal = blo_signal / blo_signal.max(axis=(0, 1, 2, 3)) * (2 ** 8 - 1)
        blo_signal.change_dtype('uint8')

        # Set axes parameters
        scales = self._model.step_size + self._model.pixel_size
        units = tuple(self._model._axes_units[0:2]) + ('cm', 'cm')
        offsets = [0., 0., 0., 0.]

        for ax_no, (name, scale, offset, unit) in enumerate(zip(self._model.axes_names, scales, offsets, units)):
            logger.debug(
                f'Setting axis parameters for axis number {ax_no}: \n{tabulate([[name, scale, offset, unit]], headers=("name", "scale", "offset", "units"))}')
            blo_signal.axes_manager[ax_no].name = name
            blo_signal.axes_manager[ax_no].scale = scale
            blo_signal.axes_manager[ax_no].offset = offset
            blo_signal.axes_manager[ax_no].units = unit

        return blo_signal


class SignalModelView(QtWidgets.QWidget):
    """
    Object to view and control the conversion of a .mib signal
    """

    default_stage_names = ('EM31640-2x', 'EM31680-2x', 'DENS wildfire')
    conversion_formats = ('.hspy', '.zarr', '.blo')

    def __init__(self, controller, model, *args, **kwargs):
        """
        Create a view with widgets for the controller and model used to convert .mib signals.

        :param controller: The controller to interact with
        :param model: The model to control through the controller
        :type controller: SignalController
        :type model: SignalModel
        :param args: Optional positional arguments passed to QtWidgets.QWidget()
        :param kwargs: Optional keyword arguments passed to QtWidgets.QWidget()
        """
        super(SignalModelView, self).__init__(*args, **kwargs)

        if not isinstance(controller, SignalController):
            raise TypeError(
                f'Cannot create {self.__class__.__name__} with controller {controller}: Only SignalController objects are accepted')
        self._controller = controller

        if not isinstance(model, SignalModel):
            raise TypeError(
                f'Cannot create {self.__class__.__name__} with model {model}: Only SignalModel objects are accepted')
        self._model = model

        self.setLayout(QtWidgets.QVBoxLayout())

        # File info
        self._file_info_widget = QtWidgets.QGroupBox('File')
        self._file_info_widget.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self._file_info_widget)

        ## IO
        self._file_io_widget = QtWidgets.QWidget()
        self._file_io_widget.setLayout(QtWidgets.QHBoxLayout())
        self._file_io_widget.layout().addWidget(QtWidgets.QLabel('File path:'))
        self._path_widget = QtWidgets.QLineEdit()
        self._load_button = QtWidgets.QPushButton('Load')
        self._browse_button = QtWidgets.QPushButton('Browse')
        self._file_info_widget.layout().addWidget(self._file_io_widget)
        self.setup_file_io_widgets()

        ## Details
        self._file_details_widget = QtWidgets.QWidget()
        self._file_details_widget.setLayout(QtWidgets.QHBoxLayout())
        self._file_details_widget.layout().addWidget(QtWidgets.QLabel('Signal:'))
        self._signal_widget = QtWidgets.QLabel(str(self._model.signal))
        self._file_details_widget.layout().addWidget(self._signal_widget)
        self._file_info_widget.layout().addWidget(self._file_details_widget)
        self._model.signalChanged.connect(self.on_signal_changed)

        # main widgets
        self._main_widgets = QtWidgets.QWidget()
        self._main_widgets.setLayout(QtWidgets.QHBoxLayout())
        self.layout().addWidget(self._main_widgets)

        ##Shape and chunks:
        self._structure_widgets = QtWidgets.QWidget(self._main_widgets)
        self._structure_widgets.setLayout(QtWidgets.QVBoxLayout())
        self._main_widgets.layout().addWidget(self._structure_widgets)

        ###Shape widgets
        self._shape_widget = QtWidgets.QGroupBox('Shape', self._structure_widgets)
        self._shape_widget.setLayout(QtWidgets.QGridLayout())
        self._nx_spinbox = QtWidgets.QSpinBox()
        self._ny_spinbox = QtWidgets.QSpinBox()
        self._ndx_spinbox = QtWidgets.QSpinBox()
        self._ndy_spinbox = QtWidgets.QSpinBox()
        self.setup_shape_widgets()
        self._structure_widgets.layout().addWidget(self._shape_widget)

        ###Chunk widgets
        self._chunk_widget = QtWidgets.QGroupBox('Chunking', self._structure_widgets)
        self._chunk_widget.setLayout(QtWidgets.QGridLayout())
        self._x_chunk_spinbox = QtWidgets.QSpinBox()
        self._y_chunk_spinbox = QtWidgets.QSpinBox()
        self._dx_chunk_spinbox = QtWidgets.QSpinBox()
        self._dy_chunk_spinbox = QtWidgets.QSpinBox()
        self.setup_chunk_widgets()
        self._structure_widgets.layout().addWidget(self._chunk_widget)

        ### Add spacer
        self._structure_widgets.layout().addStretch()

        # WIP

        ## Metadata widgets
        self._metadata_widgets = QtWidgets.QGroupBox('Metadata')
        self._metadata_widgets.setLayout(QtWidgets.QHBoxLayout())
        self._main_widgets.layout().addWidget(self._metadata_widgets)

        ### Auxilliary metadata
        self._aux_metadata_widgets = QtWidgets.QWidget()
        self._aux_metadata_widgets.setLayout(QtWidgets.QGridLayout())
        self._operator_widget = QtWidgets.QLineEdit()
        self._specimen_widget = QtWidgets.QLineEdit()
        self._stage_widgets = QtWidgets.QWidget()
        self._notes_widget = QtWidgets.QTextEdit()
        self._date_widget = QtWidgets.QDateEdit()
        self.setup_aux_metadata_widgets()

        #### Stage metadata
        self._stage_widgets.setLayout(QtWidgets.QGridLayout())
        self._stage_x_widget = QtWidgets.QDoubleSpinBox()
        self._stage_y_widget = QtWidgets.QDoubleSpinBox()
        self._stage_z_widget = QtWidgets.QDoubleSpinBox()
        self._stage_alpha_widget = QtWidgets.QDoubleSpinBox()
        self._stage_beta_widget = QtWidgets.QDoubleSpinBox()
        self._stage_name_widget = QtWidgets.QComboBox()
        self.setup_stage_widgets()

        ### Acquisition metadata
        self._acquisition_metadata_widgets = QtWidgets.QGroupBox('Acquisition parameters')
        self._metadata_widgets.layout().addWidget(self._acquisition_metadata_widgets)
        self._mode_widget = QtWidgets.QComboBox()
        self._alpha_widget = QtWidgets.QSpinBox()
        self._cameralength_widget = QtWidgets.QDoubleSpinBox()
        self._calibrate_widget = QtWidgets.QPushButton('Calibrate')
        self._precession_angle_widget = QtWidgets.QDoubleSpinBox()
        self._precession_frequency_widget = QtWidgets.QDoubleSpinBox()
        self._scan_rotation_widget = QtWidgets.QDoubleSpinBox()
        self._scan_step_size_x_widget = QtWidgets.QDoubleSpinBox()
        self._scan_step_unit_x_widget = QtWidgets.QComboBox()
        self._scan_step_size_y_widget = QtWidgets.QDoubleSpinBox()
        self._scan_step_unit_y_widget = QtWidgets.QComboBox()
        self._convergence_angle_widget = QtWidgets.QDoubleSpinBox()
        self._beam_energy_widget = QtWidgets.QDoubleSpinBox()
        self._spotsize_widget = QtWidgets.QDoubleSpinBox()
        self._spot_widget = QtWidgets.QSpinBox()
        self._exposure_time_widget = QtWidgets.QDoubleSpinBox()
        self.setup_acquisition_metadata_widgets()

        # Conversion widgets
        self._conversion_widget = QtWidgets.QGroupBox('Conversion')
        self._conversion_widget.setLayout(QtWidgets.QHBoxLayout())
        self._extensions_widget = QtWidgets.QGroupBox('Output formats')
        self._extensions_widget.setLayout(QtWidgets.QHBoxLayout())
        self._overwrite_widget = QtWidgets.QCheckBox('Overwrite')
        self._convert_button = QtWidgets.QPushButton('Convert')
        self.layout().addWidget(self._conversion_widget)
        self.setup_conversion_widgets()

        # Print widget
        self._print_button = QtWidgets.QPushButton('Print')
        self.layout().addWidget(self._print_button)
        self._print_button.clicked.connect(self._controller.printSelf)

        # Listen for changes in model and update widgets
        self._model.pathChanged[str].connect(self.on_path_changed)
        self._model.signalChanged.connect(self.on_signal_changed)
        self._model.shapeChanged[tuple].connect(self.on_shape_changed)
        self._model.stageXChanged[float].connect(self.on_stage_x_changed)
        self._model.stageYChanged[float].connect(self.on_stage_y_changed)
        self._model.stageZChanged[float].connect(self.on_stage_z_changed)
        self._model.stageAlphaChanged[float].connect(self.on_stage_alpha_changed)
        self._model.stageBetaChanged[float].connect(self.on_stage_beta_changed)
        self._model.stageChanged[str].connect(self.on_stage_changed)
        self._model.operatorChanged[str].connect(self.on_operator_changed)
        self._model.specimenChanged[str].connect(self.on_specimen_changed)
        self._model.notesChanged[str].connect(self.on_notes_changed)
        self._model.dateChanged[date].connect(self.on_date_changed)
        self._model.beamEnergyChanged[float].connect(self.on_beam_energy_changed)
        self._model.cameralengthChanged[float].connect(self.on_cameralength_changed)
        self._model.modeChanged[str].connect(self.on_mode_changed)
        self._model.alphaChanged[int].connect(self.on_alpha_changed)
        self._model.spotsizeChanged[float].connect(self.on_spotsize_changed)
        self._model.spotChanged[int].connect(self.on_spot_changed)
        self._model.precessionAngleChanged[float].connect(self.on_precession_angle_changed)
        self._model.precessionFrequencyChanged[float].connect(self.on_precession_frequency_changed)
        self._model.convergenceAngleChanged[float].connect(self.on_convergence_angle_changed)
        self._model.scanRotationChanged[float].connect(self.on_scan_rotation_changed)
        self._model.stepSizeChanged[float, float].connect(self.on_step_size_changed)
        self._model.axesUnitsChanged[str, str, str, str].connect(self.on_axes_units_changed)

    def setup_file_io_widgets(self):
        """
        Setup the file io widgets
        :return:
        """
        self._file_io_widget.layout().addWidget(self._path_widget)
        self._file_io_widget.layout().addWidget(self._load_button)
        self._file_io_widget.layout().addWidget(self._browse_button)

        self._path_widget.returnPressed.connect(
            lambda: self.set_path(self._path_widget.text()))  # lambda: self.set_path(self._path_widget.text()))
        self._load_button.clicked.connect(self._controller.readSignal)
        self._browse_button.clicked.connect(lambda: self.set_path(self.browseInputFile()))

    def setup_info_widgets(self):
        """
        Setup the signal info widgets
        :return:
        """
        self._info_widget.layout().addWidget(self._signal_widget)
        self._signal_widget.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum))
        self._signal_widget.setText(str(self._model.signal))

    def setup_shape_widgets(self):
        """
        Setup the shape control widgets
        :return:
        """
        self._shape_widget.layout().addWidget(QtWidgets.QLabel('x'), 0, 0)
        self._shape_widget.layout().addWidget(QtWidgets.QLabel('y'), 1, 0)
        self._shape_widget.layout().addWidget(QtWidgets.QLabel('dx'), 2, 0)
        self._shape_widget.layout().addWidget(QtWidgets.QLabel('dy'), 3, 0)

        self._nx_spinbox.valueChanged.connect(self._controller.setNX)
        self._nx_spinbox.setMaximum(int(9E6))
        self._nx_spinbox.setMinimum(1)
        self._nx_spinbox.setValue(self._model.nx)

        self._ny_spinbox.valueChanged.connect(self._controller.setNY)
        self._ny_spinbox.setMaximum(int(9E6))
        self._ny_spinbox.setMinimum(1)
        self._ny_spinbox.setValue(self._model.ny)

        self._ndx_spinbox.valueChanged.connect(self._controller.setNdX)
        self._ndx_spinbox.setMaximum(512)
        self._ndy_spinbox.setMinimum(1)
        self._ndx_spinbox.setValue(self._model.ndx)
        self._ndx_spinbox.setEnabled(False)

        self._ndy_spinbox.valueChanged.connect(self._controller.setNdY)
        self._ndy_spinbox.setMaximum(512)
        self._ndy_spinbox.setMinimum(1)
        self._ndy_spinbox.setValue(self._model.ndy)
        self._ndy_spinbox.setEnabled(False)

        self._shape_widget.layout().addWidget(self._nx_spinbox, 0, 1)
        self._shape_widget.layout().addWidget(self._ny_spinbox, 1, 1)
        self._shape_widget.layout().addWidget(self._ndx_spinbox, 2, 1)
        self._shape_widget.layout().addWidget(self._ndy_spinbox, 3, 1)

    def setup_chunk_widgets(self):
        """
        Setup the chunk control widgets
        :return:
        """
        self._chunk_widget.layout().addWidget(QtWidgets.QLabel('x'), 0, 0)
        self._chunk_widget.layout().addWidget(QtWidgets.QLabel('y'), 1, 0)
        self._chunk_widget.layout().addWidget(QtWidgets.QLabel('dx'), 2, 0)
        self._chunk_widget.layout().addWidget(QtWidgets.QLabel('dy'), 3, 0)
        self._chunk_widget.layout().addWidget(self._x_chunk_spinbox, 0, 1)
        self._chunk_widget.layout().addWidget(self._y_chunk_spinbox, 1, 1)
        self._chunk_widget.layout().addWidget(self._dx_chunk_spinbox, 2, 1)
        self._chunk_widget.layout().addWidget(self._dy_chunk_spinbox, 3, 1)

        self._x_chunk_spinbox.setMinimum(1)
        self._x_chunk_spinbox.setMaximum(256)
        self._x_chunk_spinbox.setValue(self._model.chunks[0])
        self._x_chunk_spinbox.valueChanged.connect(lambda x: self._controller.setChunk(0, x))

        self._y_chunk_spinbox.setMinimum(1)
        self._y_chunk_spinbox.setMaximum(256)
        self._y_chunk_spinbox.setValue(self._model.chunks[1])
        self._y_chunk_spinbox.valueChanged.connect(lambda x: self._controller.setChunk(1, x))

        self._dx_chunk_spinbox.setMinimum(1)
        self._dx_chunk_spinbox.setMaximum(256)
        self._dx_chunk_spinbox.setValue(self._model.chunks[2])
        self._dx_chunk_spinbox.valueChanged.connect(lambda x: self._controller.setChunk(2, x))

        self._dy_chunk_spinbox.setMinimum(1)
        self._dy_chunk_spinbox.setMaximum(256)
        self._dy_chunk_spinbox.setValue(self._model.chunks[3])
        self._dy_chunk_spinbox.valueChanged.connect(lambda x: self._controller.setChunk(3, x))

    def setup_conversion_widgets(self):
        """
        Setup the converstion widgets
        :return:
        """
        self._extensions_widget.layout().addWidget(QtWidgets.QCheckBox('.hspy'))
        self._extensions_widget.layout().addWidget(QtWidgets.QCheckBox('.zarr'))
        self._extensions_widget.layout().addWidget(QtWidgets.QCheckBox('.blo'))

        self._overwrite_widget.setChecked(True)
        self._conversion_widget.layout().addWidget(self._extensions_widget)
        self._conversion_widget.layout().addWidget(self._overwrite_widget)
        self._conversion_widget.layout().addWidget(self._convert_button)
        self._conversion_widget.layout().addStretch()
        self._convert_button.clicked.connect(self.on_convert_button_clicked)

    def setup_aux_metadata_widgets(self):
        """
        Setup the auxillary metadata widgets
        :return:
        """
        self._aux_metadata_widgets.layout().addWidget(QtWidgets.QLabel('Operator:'), 0, 0)
        self._aux_metadata_widgets.layout().addWidget(QtWidgets.QLabel('Specimen:'), 1, 0)
        self._aux_metadata_widgets.layout().addWidget(QtWidgets.QLabel('Stage:'), 2, 0)
        self._aux_metadata_widgets.layout().addWidget(QtWidgets.QLabel('Notes:'), 3, 0)
        self._aux_metadata_widgets.layout().addWidget(QtWidgets.QLabel('Date:'), 4, 0)
        self._aux_metadata_widgets.layout().addWidget(self._operator_widget, 0, 1)
        self._aux_metadata_widgets.layout().addWidget(self._specimen_widget, 1, 1)
        self._aux_metadata_widgets.layout().addWidget(self._stage_widgets, 2, 1)
        self._aux_metadata_widgets.layout().addWidget(self._notes_widget, 3, 1)
        self._aux_metadata_widgets.layout().addWidget(self._date_widget, 4, 1)
        self._metadata_widgets.layout().addWidget(self._aux_metadata_widgets)

        self._operator_widget.textChanged[str].connect(self._controller.setOperator)
        self._specimen_widget.textChanged[str].connect(self._controller.setSpecimen)
        self._notes_widget.textChanged.connect(lambda: self._controller.setNotes(self._notes_widget.toPlainText()))
        self._date_widget.dateChanged[QDate].connect(self._controller.setDate)

    def setup_stage_widgets(self):
        """
        Setup the stage widgets
        :return:
        """
        self._stage_widgets.layout().addWidget(QtWidgets.QLabel('x [um]'), 0, 0)
        self._stage_widgets.layout().addWidget(QtWidgets.QLabel('y [um]'), 0, 1)
        self._stage_widgets.layout().addWidget(QtWidgets.QLabel('z [um]'), 0, 2)
        self._stage_widgets.layout().addWidget(QtWidgets.QLabel('alpha [deg]'), 0, 3)
        self._stage_widgets.layout().addWidget(QtWidgets.QLabel('beta [deg]'), 0, 4)
        self._stage_widgets.layout().addWidget(QtWidgets.QLabel('Name'), 0, 5)
        self._stage_widgets.layout().addWidget(self._stage_x_widget, 1, 0)
        self._stage_widgets.layout().addWidget(self._stage_y_widget, 1, 1)
        self._stage_widgets.layout().addWidget(self._stage_z_widget, 1, 2)
        self._stage_widgets.layout().addWidget(self._stage_alpha_widget, 1, 3)
        self._stage_widgets.layout().addWidget(self._stage_beta_widget, 1, 4)
        self._stage_widgets.layout().addWidget(self._stage_name_widget, 1, 5)

        for widget in [self._stage_x_widget, self._stage_y_widget, self._stage_z_widget, self._stage_alpha_widget,
                       self._stage_beta_widget]:
            widget.setMinimum(-9999)
            widget.setMaximum(9999)
            widget.setDecimals(2)
            widget.setSingleStep(0.01)
        self._stage_name_widget.addItems(self.default_stage_names)
        if self._model.stage not in [self._stage_name_widget.itemText(idx) for idx in
                                     range(self._stage_name_widget.count())]:
            self._stage_name_widget.addItem(self._model.stage)
        self._stage_name_widget.setCurrentText(self._model.stage)

        self._stage_x_widget.setValue(self._model.stage_x)
        self._stage_y_widget.setValue(self._model.stage_y)
        self._stage_z_widget.setValue(self._model.stage_z)
        self._stage_alpha_widget.setValue(self._model.stage_alpha)
        self._stage_beta_widget.setValue(self._model.stage_beta)

        self._stage_x_widget.valueChanged[float].connect(self._controller.setStageX)
        self._stage_y_widget.valueChanged[float].connect(self._controller.setStageY)
        self._stage_z_widget.valueChanged[float].connect(self._controller.setStageZ)
        self._stage_alpha_widget.valueChanged[float].connect(self._controller.setStageAlpha)
        self._stage_beta_widget.valueChanged[float].connect(self._controller.setStageBeta)
        self._stage_name_widget.currentTextChanged[str].connect(self._controller.setStage)

    def setup_acquisition_metadata_widgets(self):
        """
        Setup the acquisition metadata widgets
        :return:
        """
        self._beam_energy_widget.setMinimum(0)
        self._beam_energy_widget.setMaximum(999)
        self._beam_energy_widget.setDecimals(0)
        self._beam_energy_widget.setSingleStep(10)
        self._beam_energy_widget.setSuffix(' kV')
        self._beam_energy_widget.setValue(self._model.beam_energy)
        self._beam_energy_widget.valueChanged[float].connect(self._controller.setBeamEnergy)

        self._cameralength_widget.setMinimum(0)
        self._cameralength_widget.setMaximum(999)
        self._cameralength_widget.setDecimals(3)
        self._cameralength_widget.setSingleStep(0.001)
        self._cameralength_widget.setSuffix(' cm')
        self._cameralength_widget.setValue(self._model.cameralength)
        self._cameralength_widget.valueChanged[float].connect(self._controller.setCameralength)

        self._calibrate_widget.clicked.connect(self._controller.calibrateCameralength)

        self._mode_widget.addItems(['TEM', 'NBD', 'CBD', 'STEM'])
        if self._model.mode not in [self._mode_widget.itemText(idx) for idx in range(self._mode_widget.count())]:
            self._mode_widget.addItem(self._model.mode)
        self._mode_widget.setCurrentText(self._model.mode)
        self._mode_widget.currentTextChanged[str].connect(self._controller.setMode)

        self._alpha_widget.setMinimum(0)
        self._alpha_widget.setMaximum(9)
        self._alpha_widget.setValue(self._model.alpha)
        self._alpha_widget.valueChanged[int].connect(self._controller.setAlpha)

        self._spotsize_widget.setMinimum(0)
        self._spotsize_widget.setMaximum(5)
        self._spotsize_widget.setDecimals(1)
        self._spotsize_widget.setSingleStep(0.1)
        self._spotsize_widget.setSuffix(' nm')
        self._spotsize_widget.setValue(self._model.spotsize)
        self._spotsize_widget.valueChanged[float].connect(self._controller.setSpotsize)

        self._spot_widget.setMinimum(0)
        self._spot_widget.setMaximum(9)
        self._spot_widget.setValue(self._model.spot)
        self._spot_widget.valueChanged[int].connect(self._controller.setSpot)

        self._exposure_time_widget.setMinimum(0)
        self._exposure_time_widget.setMaximum(1E6)
        self._exposure_time_widget.setDecimals(4)
        self._exposure_time_widget.setSingleStep(0.1)
        self._exposure_time_widget.setSuffix(' ms')
        self._exposure_time_widget.setValue(self._model.exposure_time)
        self._exposure_time_widget.valueChanged[float].connect(self._controller.setExposureTime)

        self._precession_angle_widget.setMinimum(0)
        self._precession_angle_widget.setMaximum(10)
        self._precession_angle_widget.setDecimals(2)
        self._precession_angle_widget.setSingleStep(0.01)
        self._precession_angle_widget.setSuffix(' deg')
        self._precession_angle_widget.setValue(self._model.precession_angle)
        self._precession_angle_widget.valueChanged[float].connect(self._controller.setPrecessionAngle)

        self._precession_frequency_widget.setMinimum(0)
        self._precession_frequency_widget.setMaximum(999)
        self._precession_frequency_widget.setDecimals(2)
        self._precession_frequency_widget.setSingleStep(0.01)
        self._precession_frequency_widget.setSuffix(' Hz')
        self._precession_frequency_widget.setValue(self._model.precession_frequency)
        self._precession_frequency_widget.valueChanged[float].connect(self._controller.setPrecessionFrequency)

        self._convergence_angle_widget.setMinimum(0)
        self._convergence_angle_widget.setMaximum(999)
        self._convergence_angle_widget.setDecimals(2)
        self._convergence_angle_widget.setSingleStep(0.01)
        self._convergence_angle_widget.setSuffix(' mrad')
        self._convergence_angle_widget.setValue(self._model.convergence_angle)
        self._convergence_angle_widget.valueChanged[float].connect(self._controller.setConvergenceAngle)

        self._scan_step_size_x_widget.setMinimum(0)
        self._scan_step_size_x_widget.setMaximum(999)
        self._scan_step_size_x_widget.setDecimals(3)
        self._scan_step_size_x_widget.setSingleStep(0.001)
        self._scan_step_size_x_widget.setSuffix(f' {self._model.axes_units[0]}')
        self._scan_step_size_x_widget.setValue(self._model.step_size_x)
        self._scan_step_size_x_widget.valueChanged[float].connect(self._controller.setStepSizeX)

        self._scan_step_size_y_widget.setMinimum(0)
        self._scan_step_size_y_widget.setMaximum(999)
        self._scan_step_size_y_widget.setDecimals(3)
        self._scan_step_size_y_widget.setSingleStep(0.001)
        self._scan_step_size_y_widget.setSuffix(f' {self._model.axes_units[1]}')
        self._scan_step_size_y_widget.setValue(self._model.step_size_y)
        self._scan_step_size_y_widget.valueChanged[float].connect(self._controller.setStepSizeY)

        self._scan_step_unit_x_widget.addItems(['px', 'nm', 'um'])
        if self._model.axes_units[0] not in [self._scan_step_unit_x_widget.itemText(idx) for idx in
                                             range(self._scan_step_unit_x_widget.count())]:
            self._scan_step_unit_x_widget.addItem(self._model.axes_units[0])
        self._scan_step_unit_x_widget.setCurrentText(self._model.axes_units[0])
        self._scan_step_unit_x_widget.currentTextChanged[str].connect(self._controller.setStepUnitX)

        self._scan_step_unit_y_widget.addItems(['px', 'nm', 'um'])
        if self._model.axes_units[1] not in [self._scan_step_unit_y_widget.itemText(idx) for idx in
                                             range(self._scan_step_unit_y_widget.count())]:
            self._scan_step_unit_y_widget.addItem(self._model.axes_units[1])
        self._scan_step_unit_y_widget.setCurrentText(self._model.axes_units[1])
        self._scan_step_unit_y_widget.currentTextChanged[str].connect(self._controller.setStepUnitY)

        self._scan_rotation_widget.setMinimum(-360)
        self._scan_rotation_widget.setMaximum(360)
        self._scan_rotation_widget.setDecimals(1)
        self._scan_rotation_widget.setSingleStep(0.1)
        self._scan_rotation_widget.setSuffix(' deg')
        self._scan_rotation_widget.setValue(self._model.scan_rotation)
        self._scan_rotation_widget.valueChanged[float].connect(self._controller.setScanRotation)

        self._acquisition_metadata_widgets.setLayout(QtWidgets.QGridLayout())
        self._acquisition_metadata_widgets.layout().addWidget(QtWidgets.QLabel('Beam energy'), 0, 0)
        self._acquisition_metadata_widgets.layout().addWidget(QtWidgets.QLabel('Cameralength'), 1, 0)
        self._acquisition_metadata_widgets.layout().addWidget(QtWidgets.QLabel('Mode'), 2, 0)
        self._acquisition_metadata_widgets.layout().addWidget(QtWidgets.QLabel('Alpha'), 3, 0)
        self._acquisition_metadata_widgets.layout().addWidget(QtWidgets.QLabel('Spotsize'), 4, 0)
        self._acquisition_metadata_widgets.layout().addWidget(QtWidgets.QLabel('Spot'), 5, 0)
        self._acquisition_metadata_widgets.layout().addWidget(QtWidgets.QLabel('Precession angle'), 6, 0)
        self._acquisition_metadata_widgets.layout().addWidget(QtWidgets.QLabel('Precession frequency'), 7, 0)
        self._acquisition_metadata_widgets.layout().addWidget(QtWidgets.QLabel('Scan step X'), 8, 0)
        self._acquisition_metadata_widgets.layout().addWidget(QtWidgets.QLabel('Scan step Y'), 9, 0)
        self._acquisition_metadata_widgets.layout().addWidget(QtWidgets.QLabel('Scan rotation'), 10, 0)
        self._acquisition_metadata_widgets.layout().addWidget(QtWidgets.QLabel('Convergence angle'), 11, 0)
        self._acquisition_metadata_widgets.layout().addWidget(QtWidgets.QLabel('Exposure time'), 12, 0)

        self._acquisition_metadata_widgets.layout().addWidget(self._beam_energy_widget, 0, 1)
        self._acquisition_metadata_widgets.layout().addWidget(self._cameralength_widget, 1, 1)
        self._acquisition_metadata_widgets.layout().addWidget(self._calibrate_widget, 1, 2)
        self._acquisition_metadata_widgets.layout().addWidget(self._mode_widget, 2, 1)
        self._acquisition_metadata_widgets.layout().addWidget(self._alpha_widget, 3, 1)
        self._acquisition_metadata_widgets.layout().addWidget(self._spotsize_widget, 4, 1)
        self._acquisition_metadata_widgets.layout().addWidget(self._spot_widget, 5, 1)
        self._acquisition_metadata_widgets.layout().addWidget(self._precession_angle_widget, 6, 1)
        self._acquisition_metadata_widgets.layout().addWidget(self._precession_frequency_widget, 7, 1)
        self._acquisition_metadata_widgets.layout().addWidget(self._scan_step_size_x_widget, 8, 1)
        self._acquisition_metadata_widgets.layout().addWidget(self._scan_step_size_y_widget, 9, 1)
        self._acquisition_metadata_widgets.layout().addWidget(self._scan_step_unit_x_widget, 8, 2)
        self._acquisition_metadata_widgets.layout().addWidget(self._scan_step_unit_y_widget, 9, 2)
        self._acquisition_metadata_widgets.layout().addWidget(self._scan_rotation_widget, 10, 1)
        self._acquisition_metadata_widgets.layout().addWidget(self._convergence_angle_widget, 11, 1)
        self._acquisition_metadata_widgets.layout().addWidget(self._exposure_time_widget, 12, 1)

    @pyqtSlot(tuple)
    def on_shape_changed(self, shape):
        """
        Update the shape widgets with new values
        :param shape:
        :return:
        """
        self._nx_spinbox.blockSignals(True)
        self._ny_spinbox.blockSignals(True)
        self._ndx_spinbox.blockSignals(True)
        self._ndy_spinbox.blockSignals(True)
        self._nx_spinbox.setValue(shape[0])
        self._ny_spinbox.setValue(shape[1])
        self._ndx_spinbox.setValue(shape[2])
        self._ndy_spinbox.setValue(shape[3])
        self._nx_spinbox.blockSignals(False)
        self._ny_spinbox.blockSignals(False)
        self._ndx_spinbox.blockSignals(False)
        self._ndy_spinbox.blockSignals(False)

        # Check signal datastack size and set color of widgets based on the comparison.
        if self._model.signal is None:
            color = 'lightblue'
        else:
            if np.prod(self._model.signal.axes_manager.shape) == np.prod(
                    [self._nx_spinbox.value(), self._ny_spinbox.value(), self._ndx_spinbox.value(),
                     self._ndy_spinbox.value()]):
                color = 'lightgreen'
            else:
                color = 'red'

        logger.debug(f'Setting background colors of shape spin boxes to {color}')
        style_sheet_prefix = 'QSpinBox { background-color : '
        style_sheet_suffix = '; }'
        self._nx_spinbox.setStyleSheet(f'{style_sheet_prefix}{color}{style_sheet_suffix}')
        self._ny_spinbox.setStyleSheet(f'{style_sheet_prefix}{color}{style_sheet_suffix}')
        self._ndx_spinbox.setStyleSheet(f'{style_sheet_prefix}{color}{style_sheet_suffix}')
        self._ndy_spinbox.setStyleSheet(f'{style_sheet_prefix}{color}{style_sheet_suffix}')

    def on_signal_changed(self):
        """
        Update widgets to match current values in the model
        :return:
        """
        self._signal_widget.setText(str(self._model.signal))
        if self._model.signal is None:
            self._convert_button.setEnabled(False)
        else:
            self._convert_button.setEnabled(True)
        self._path_widget.setText(str(self._model.path))
        self.on_shape_changed(self._model.shape)

        frames = self._model.signal.axes_manager[0].size
        if sqrt(frames).is_integer():
            logger.debug(f'Number of frames {frames} matches a square scan, setting appropriate gui values')
            n = int(sqrt(frames))
            self._nx_spinbox.setValue(n)
            self._ny_spinbox.setValue(n)
        else:
            logger.debug(f'Cannot interpret number of frames {frames} as a square scan.')

    def on_chunks_changed(self):
        """
        Update the chunks to match the chunking in the model
        :return:
        """
        self._x_chunk_spinbox.blockSignals(True)
        self._y_chunk_spinbox.blockSignals(True)
        self._dx_chunk_spinbox.blockSignals(True)
        self._dy_chunk_spinbox.blockSignals(True)

        self._x_chunk_spinbox.setValue(self._model.chunks[0])
        self._y_chunk_spinbox.setValue(self._model.chunks[1])
        self._dx_chunk_spinbox.setValue(self._model.chunks[2])
        self._dy_chunk_spinbox.setValue(self._model.chunks[3])

        self._x_chunk_spinbox.blockSignals(False)
        self._y_chunk_spinbox.blockSignals(False)
        self._dx_chunk_spinbox.blockSignals(False)
        self._dy_chunk_spinbox.blockSignals(False)

    @pyqtSlot(str)
    @pyqtSlot(Path)
    def on_path_changed(self, value):
        """
        Update the path widget with new a value
        :param value:
        :return:
        """
        self._controller.readSignal()
        self._path_widget.setText(str(value))

    @pyqtSlot(float)
    def on_stage_x_changed(self, value):
        """
        Update the stage x widget with new a value
        :param value:
        :return:
        """
        self._stage_x_widget.blockSignals(True)
        self._stage_x_widget.setValue(value)
        self._stage_x_widget.blockSignals(False)

    @pyqtSlot(float)
    def on_stage_y_changed(self, value):
        """
        Update the stage y widget with new a value
        :param value:
        :return:
        """
        self._stage_y_widget.blockSignals(True)
        self._stage_y_widget.setValue(value)
        self._stage_y_widget.blockSignals(False)

    @pyqtSlot(float)
    def on_stage_z_changed(self, value):
        """
        Update the stage z widget with new a value
        :param value:
        :return:
        """
        self._stage_z_widget.blockSignals(True)
        self._stage_z_widget.setValue(value)
        self._stage_z_widget.blockSignals(False)

    @pyqtSlot(float)
    def on_stage_alpha_changed(self, value):
        """
        Update the stage alpha widget with new a value
        :param value:
        :return:
        """
        self._stage_alpha_widget.blockSignals(True)
        self._stage_alpha_widget.setValue(value)
        self._stage_alpha_widget.blockSignals(False)

    @pyqtSlot(float)
    def on_stage_beta_changed(self, value):
        """
        Update the stage beta widget with new a value
        :param value:
        :return:
        """
        self._stage_beta_widget.blockSignals(True)
        self._stage_beta_widget.setValue(value)
        self._stage_beta_widget.blockSignals(False)

    @pyqtSlot(str)
    def on_stage_changed(self, value):
        """
        Update the stage name widget with new content
        :param value:
        :return:
        """
        self._stage_name_widget.blockSignals(True)
        if value not in [self._stage_name_widget.itemText(idx) for idx in range(self._stage_name_widget.count())]:
            self._stage_name_widget.addItem(value)
        self._stage_name_widget.setCurrentText(value)
        self._stage_name_widget.blockSignals(False)

    @pyqtSlot(str)
    def on_operator_changed(self, value):
        """
        Update the operator name widget with new content
        :param value:
        :return:
        """
        self._operator_widget.blockSignals(True)
        self._operator_widget.setText(value)
        self._operator_widget.blockSignals(False)

    @pyqtSlot(str)
    def on_specimen_changed(self, value):
        """
        Update the specimen widget with new content
        :param value:
        :return:
        """
        self._specimen_widget.blockSignals(True)
        self._specimen_widget.setText(value)
        self._specimen_widget.blockSignals(False)

    @pyqtSlot(str)
    def on_notes_changed(self, value):
        """
        Update notes widget with new content
        :param value:
        :return:
        """
        if value == self._notes_widget.toPlainText():
            logger.debug(
                f'Text\n"{value}"\n already matches text in notes widget\n"{self._notes_widget.toPlainText()}"\n. Doing nothing.')
        else:
            logger.debug(
                f'Text\n"{value}"\n does not match text already in notes widget\n"{self._notes_widget.toPlainText()}"\n. Updating widget text contents without sending signals.')
            self._notes_widget.blockSignals(True)
            self._notes_widget.setPlainText(value)
            text_cursor = self._notes_widget.textCursor()
            text_cursor.movePosition(text_cursor.MoveOperation.End)
            self._notes_widget.setTextCursor(text_cursor)
            self._notes_widget.blockSignals(False)

    @pyqtSlot(date)
    def on_date_changed(self, value):
        """
        Update the date widget to a new value
        :param value:
        :return:
        """
        self._date_widget.blockSignals(True)
        self._date_widget.setDate(value)
        self._date_widget.blockSignals(False)

    @pyqtSlot(float)
    def on_beam_energy_changed(self, value):
        """
        Update the beam energy widget to a new value
        :param value:
        :return:
        """
        self._beam_energy_widget.blockSignals(True)
        self._beam_energy_widget.setValue(value)
        self._beam_energy_widget.blockSignals(False)

    @pyqtSlot(float)
    def on_cameralength_changed(self, value):
        """
        Update the cameralength widget to a new value
        :param value:
        :return:
        """
        self._cameralength_widget.blockSignals(True)
        self._cameralength_widget.setValue(value)
        self._cameralength_widget.blockSignals(False)

    @pyqtSlot(str)
    def on_mode_changed(self, value):
        """
        Update the mode widget to a new value
        :param value:
        :return:
        """
        self._mode_widget.blockSignals(True)
        if value not in [self._mode_widget.itemText(idx) for idx in range(self._mode_widget.count())]:
            self._mode_widget.addItem(value)
        self._mode_widget.setCurrentText(value)
        self._mode_widget.blockSignals(False)

    @pyqtSlot(int)
    def on_alpha_changed(self, value):
        """
        Update the alpha widget to a new value
        :param value:
        :return:
        """
        self._alpha_widget.blockSignals(True)
        self._alpha_widget.setValue(value)
        self._alpha_widget.blockSignals(False)

    @pyqtSlot(float)
    def on_precession_angle_changed(self, value):
        """
        Update the precession angle widget to a new value
        :param value:
        :return:
        """
        self._precession_angle_widget.blockSignals(True)
        self._precession_angle_widget.setValue(value)
        self._precession_angle_widget.blockSignals(False)

    @pyqtSlot(float)
    def on_precession_frequency_changed(self, value):
        """
        Update the precession frequency widget to a new value
        :param value:
        :return:
        """
        self._precession_frequency_widget.blockSignals(True)
        self._precession_frequency_widget.setValue(value)
        self._precession_frequency_widget.blockSignals(False)

    @pyqtSlot(float)
    def on_spotsize_changed(self, value):
        """
        Update the spotsize widget to a new value
        :param value:
        :return:
        """
        self._spotsize_widget.blockSignals(True)
        self._spotsize_widget.setValue(value)
        self._spotsize_widget.blockSignals(False)

    @pyqtSlot(int)
    def on_spot_changed(self, value):
        """
        Update the spot widget to a new value
        :param value:
        :return:
        """
        self._spot_widget.blockSignals(True)
        self._spot_widget.setValue(value)
        self._spot_widget.blockSignals(False)

    @pyqtSlot(float, float)
    def on_step_size_changed(self, value_x, value_y):
        """
        Update the step size widgets to new values
        :param value_x:
        :param value_y:
        :return:
        """
        self._scan_step_size_x_widget.blockSignals(True)
        self._scan_step_size_y_widget.blockSignals(True)
        self._scan_step_size_x_widget.setValue(value_x)
        self._scan_step_size_y_widget.setValue(value_y)
        self._scan_step_size_x_widget.blockSignals(False)
        self._scan_step_size_y_widget.blockSignals(False)

    @pyqtSlot(str, str, str, str)
    def on_axes_units_changed(self, units_x, units_y, units_kx, units_ky):
        """
        Update the units widgets to new values
        :param units_x:
        :param units_y:
        :param units_kx:
        :param units_ky:
        :return:
        """
        if units_x not in [self._scan_step_unit_x_widget.itemText(idx) for idx in
                           range(self._scan_step_unit_x_widget.count())]:
            self._scan_step_unit_x_widget.addItem(units_x)

        if units_y not in [self._scan_step_unit_y_widget.itemText(idx) for idx in
                           range(self._scan_step_unit_x_widget.count())]:
            self._scan_step_unit_y_widget.addItem(units_x)

        self._scan_step_unit_x_widget.setCurrentText(units_x)
        self._scan_step_unit_y_widget.setCurrentText(units_y)

        self._scan_step_size_x_widget.setSuffix(f' {units_x}')
        self._scan_step_size_y_widget.setSuffix(f' {units_y}')

    @pyqtSlot(float)
    def on_scan_rotation_changed(self, value):
        """
        Update the scan rotation widgets to a new value
        :param value:
        :return:
        """
        self._scan_rotation_widget.blockSignals(True)
        self._scan_rotation_widget.setValue(value)
        self._scan_rotation_widget.blockSignals(False)

    @pyqtSlot(float)
    def on_exposure_time_changed(self, value):
        """
        Update the exposure time widget to a new value
        :param value:
        :return:
        """
        self._exposure_time_widget.blockSignals(True)
        self._exposure_time_widget.setValue(value)
        self._exposure_time_widget.blockSignals(False)

    @pyqtSlot(float)
    def on_convergence_angle_changed(self, value):
        """
        Update the convergence angle widget to a new value
        :param value:
        :return:
        """
        self._convergence_angle_widget.blockSignals(True)
        self._convergence_angle_widget.setValue(value)
        self._convergence_angle_widget.blockSignals(False)

    @pyqtSlot()
    def on_convert_button_clicked(self):
        """
        Start conversion
        :return:
        """
        widgets = [self._extensions_widget.layout().itemAt(idx).widget() for idx in
                   range(self._extensions_widget.layout().count())]
        logger.debug(f'Widgets: {widgets}')
        chkbox_widgets = [widget for widget in widgets if isinstance(widget, QtWidgets.QCheckBox)]
        logger.debug(f'Checkbox widgets: {chkbox_widgets}')
        active_widgets = [widget for widget in chkbox_widgets if widget.isChecked()]
        logger.debug(f'Active widgets: {active_widgets}')
        extensions = [widget.text() for widget in active_widgets]
        logger.debug(f'Chosen extensions: {extensions}')
        self._controller.saveSignal(extensions, self._overwrite_widget.isChecked())

    def set_path(self, path):
        """
        Attempt to set the path of the controller.

        If any exception is raised during setting the path, the exception is logged, ignored, and the path widget is updated/reset to reflect actual path of the current signal
        :param path:
        :return:
        """
        try:
            self._controller.setPath(path)
        except Exception as e:
            logger.error(e, exc_info=True)
            logger.debug('Ignoring error. Resetting path-widget text')
            self._path_widget.setText(str(self._model.path))

    @pyqtSlot(name='browseInputFile', result=str)
    def browseInputFile(self):
        """
        Browse for a filename through a dialog
        :return:
        """
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            None,
            "Select .mib file",
            "",
            "mib Files (*.mib);;All Files (*)",
            options=options)
        return fileName


def wavelength(acceleration_voltage, m0=9.1093837015 * 1e-31, e=1.60217662 * 1e-19, h=6.62607004 * 1e-34, c=299792458):
    """
    Return the wavelength of an accelerated electron in [Å]

    :param acceleration_voltage: The acceleration voltage of the electron [kV]
    :param c: Speed of light in vacuum [m/s]
    :param h: Planck' constant [m^2 kg/s]
    :param e: Elementary charge of electorn [C]
    :param m0: Rest mass of electron [kg]
    :type m0: float
    :type e: float
    :type h: float
    :type c: float
    :returns: wavelength of electron in Å
    :rtype: float
    """
    V = acceleration_voltage * 1E3
    return h / sqrt(2 * m0 * e * V * (1.0 + (e * V / (2 * m0 * c ** 2)))) * 1E10


def cameralength2scale(cameralength, beamenergy, pixelsize):
    """
    Return the pixel scale of a diffraction pattern.

    :param cameralength: The cameralength of the pattern in cm
    :param beamenergy: The energy of the beam in kV
    :param pixelsize: The pixel size of the detector in cm
    :return: scale in 1/Å
    :type cameralength: float
    :type beamenergy: float
    :type pixelsize: float
    :rtype: float
    """
    return abs(np.arctan(pixelsize / (cameralength * wavelength(beamenergy))))


def load_hdr(filename):
    """load a header file"""
    filename = Path(filename)
    hdr_content = dict()
    if filename.exists() and filename.suffix == '.hdr':
        with filename.open('r') as hdrfile:
            lines = hdrfile.readlines()
            for lineno, line in enumerate(lines):
                if 0 < lineno < len(lines) - 1:
                    field, value = line.split(':', maxsplit=1)
                    field = field.strip()
                    value = value.strip()
                    hdr_content[field] = value
    else:
        raise FileNotFoundError(f'HDR file "{filename.absolute()}" does not exist or is not a valid .hdr file.')
    return hdr_content


def run_gui(logging_level=logging.INFO):
    """
    Run conversion GUI

    Starts a GUI for converting .mib data to other formats, while also reshaping the data, rechunking the data, and adding various metadata and calibrations.

    Output is logged during operation.

    :param logging_level: The logging level to use
    :return:
    """
    logger.setLevel(logging_level)

    mygui = QtWidgets.QApplication(sys.argv)
    logger.debug('Creating model')
    model = SignalModel()
    logger.debug('Creating controller for model')
    controller = SignalController(model)
    logger.debug('Creating view')
    microscope_view = SignalModelView(controller, model)

    logger.debug('Creating main window')
    mainwindow = QtWidgets.QMainWindow()
    logger.debug('\tSetting view as central widget')
    mainwindow.setCentralWidget(microscope_view)

    logger.debug('Showing mainwindow')
    mainwindow.show()
    sys.exit(mygui.exec_())


if __name__ == '__main__':
    logger.info('starting GUI')
    run_gui()
