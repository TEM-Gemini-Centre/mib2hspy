# from math import nan, isnan
from datetime import datetime, date
from tabulate import tabulate
import pandas as pd
import numpy as np
from math import nan, isnan, sqrt
from string import Formatter
from pandas.core.computation.ops import UndefinedVariableError


class Error(Exception):
    pass


class CalibrationError(Error):
    pass


class MicroscopeParameterError(Error):
    pass


class Parameter(object):
    """
    A parameter for storing various microscope parameter values
    """
    allowed_value_types = (int, float, str, datetime, date)

    def __init__(self, parameter_name, value, units):
        """
        Create a parameter
        :param parameter_name: Name of parameter
        :type parameter_name: str
        :param value: The value of the parameter
        :type value: int, float, str, datetime
        :param units: The units of the parameter
        :type units: str
        """
        super(Parameter, self).__init__()
        if not isinstance(parameter_name, str):
            raise TypeError('Parameter name must be a string!')
        if not isinstance(units, str):
            raise TypeError('Units must be a string!')
        if not isinstance(value, self.allowed_value_types):
            raise TypeError('Value must be int, float, str, or datetime!')
        self.name = parameter_name
        self.value = value
        self.units = units

    def set_name(self, newname):
        """
        Set the name of the parameter
        :param newname: new parameter name
        :type newname: str
        :return:
        """
        if not isinstance(newname, str):
            raise TypeError()
        self.name = newname

    def set_units(self, newunits):
        """
        Set the units of the parameter
        :param newunits: new parameter units
        :type newunits: str
        :return:
        """
        if not isinstance(newunits, str):
            raise TypeError()
        self.units = newunits

    def set_value(self, newvalue):
        """
        Set the value of the parameter
        :param newvalue: new parameter value
        :type newvalue: int, float, str, datetime, date
        :return:
        """
        if not isinstance(newvalue, self.allowed_value_types):
            raise TypeError(
                'Value {newvalue!r} of type {invalid_type} is not of supported types {self.allowed_value_types}!'.format(
                    newvalue=newvalue, invalid_type=type(newvalue), self=self))
        self.value = newvalue

    def __str__(self):
        return '{self.__class__.__name__} {self.name}: {self.value} {self.units}'.format(
            self=self)

    def __repr__(self):
        return '{self.__class__.__name__}({self.name!r}, {self.value!r}, {self.units!r})'.format(
            self=self)

    def __format__(self, format_spec):
        if format_spec == 'q':
            return QueryFormatter().format('{self!q}'.format(self=self))
        else:
            return '{self.value:{f}}'.format(self=self, f=format_spec)

    def __float__(self):
        return float(self.value)

    def __int__(self):
        return int(self.value)

    def __mul__(self, other):
        return self.value * other

    def __rmul__(self, other):
        return other * self.value

    def __add__(self, other):
        return self.value + other

    def __radd__(self, other):
        return other + self.value

    def __neg__(self):
        return -self.value

    def __sub__(self, other):
        return self.value - other

    def __rsub__(self, other):
        return other - self.value

    def __truediv__(self, other):
        return self.value / other

    def __rtruediv__(self, other):
        return other / self.value

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other

    def __ge__(self, other):
        return self.value >= other

    def __gt__(self, other):
        return self.value > other

    def __lt__(self, other):
        return self.value < other

    def __le__(self, other):
        return self.value <= other

    def __pow__(self, power, modulo=None):
        return self.value.__pow__(power, modulo)

    def is_defined(self):
        """
        Check whether the value of the parameter is well-defined or not (i.e. not `nan`, `None`, `""`, or `"None"`)

        :returns: False if value is None, 'None', '', or nan
        :rtype: bool
        """
        if self.value is None:
            return False
        if isinstance(self.value, str):
            if self.value == '' or self.value == 'None':
                return False
            else:
                return True
        return not isnan(self.value)

    def as_dict(self):
        """
        Return parameter as a dictionary

        :returns: dict({name:{'Value': value, 'Units': units}})
        :rtype: dict
        """
        return {'{self.name}'.format(self=self): {'Value': self.value, 'Units': self.units}}

    def set_value_from_calibrationtable(self, calibrationtable, query, print_result=False):
        """
        Sets the value of the parameter to a matching entry in a calibration table.

        :param calibrationtable: The calibration table to search in. Must contain a column named "Nominal <name> (<units>)" and "<name> (<units>)" that matches the parameter name and units. The table will also be filtered with additional queries.
        :param query: Additional queries to the calibration table, see pandas.DataFrame.query for more information.
        :type calibrationtable: pandas.DataFrame
        :type query: str
        :return:
        """
        if not isinstance(calibrationtable, pd.DataFrame):
            raise TypeError(
                'Expected calibration table to be of type {expected_type}, not {wrong_type}\nGot: {calibrationtable!r}'.format(
                    expected_type=pd.DataFrame, wrong_type=type(calibrationtable), calibrationtable=calibrationtable))
        if not isinstance(query, str):
            raise TypeError('Expected query to be of type {expected_type}, not {wrong_type}\nGot: {query!r}'.format(
                expected_type=str, wrong_type=type(query), query=query))

        if isinstance(self, CalibratedParameter):
            query = query + ' & ' + QueryFormatter().convert_field(self, 'q')
        else:
            pass

        try:
            calibration_rows = calibrationtable.query(query)
            key = '{self.name} ({self.units})'.format(self=self)
            values = calibration_rows[key].values  # Get the actual values from the calibration rows.
        except UndefinedVariableError:
            print(
                'Unable to query calibration table for \n"{query}"\ndue to missing (required) columns. Please check that the calibration file column headers for errors. Continuing without calibrating this value.\n'.format(
                    query=query, table=calibrationtable))
        except KeyError as e:
            print(
                'No column was found for {key} in \n{calibration_rows}.\nPlease check that the calibration file column headers for errors. Continuing withoug calibrating this value.\n'.format(
                    key=key, calibration_rows=calibration_rows))
        else:
            if len(values) > 0:
                if len(values) > 1:
                    print(
                        'Multiple calibration rows fits with query "{query}".\nUsing last entry.\n'.format(query=query))
                value = values[-1]
            else:
                print('No calibration found for {self!r} in calibration table after querying for "{query}".\n'.format(
                    self=self, table=calibrationtable, query=query))
                value = nan
            if bool(print_result):
                print('Result from query "{query}" to calibration table: {value!r}\n'.format(query=query,
                                                                                             table=calibrationtable,
                                                                                             value=value))
            self.set_value(value)


class QueryFormatter(Formatter):
    """
    Formatter for creating query strings from parameters
    """

    def convert_field(self, value, conversion):
        """
        Overloaded convert_field method.

        Converts the value (returned by get_field()) given a conversion type (as in the tuple returned by the parse() method). The default version understands ‘s’ (str), ‘r’ (repr) and ‘a’ (ascii) conversion types.

        :param value: Value to be formatted
        :param conversion: Conversion field
        :type value: Any
        :type conversion: str
        :return: formatted string based on conversion string
        """
        if conversion == 'q':
            if isinstance(value, CalibratedParameter):
                if isinstance(value.nominal_value, str):
                    return '`Nominal {value.name} ({value.units})` == "{value.nominal_value}"'.format(value=value)
                else:
                    if isnan(value.nominal_value):
                        return '`Nominal {value.name} ({value.units})` == @{value.nominal_value}'.format(value=value)
                    else:
                        return '`Nominal {value.name} ({value.units})` == {value.nominal_value}'.format(value=value)
            elif isinstance(value, Parameter):
                # Handle empty units specially for Parameters.
                if value.units == '':
                    units = ''
                else:
                    units = ' ({value.units})'.format(value=value)
                if isinstance(value.value, str):
                    return '`{value.name}{units}` == "{value.value}"'.format(value=value, units=units)
                else:
                    if isnan(value.value):
                        return '`{value.name}{units}` == @{value.value}'.format(value=value, units=units)
                    else:
                        return '`{value.name}{units}` == {value.value}'.format(value=value, units=units)
            else:
                return super().convert_field(value, conversion)
        else:
            return super().convert_field(value, conversion)


class CalibrationQueryFormatter(QueryFormatter):
    """
    A class for creating calibration queries
    """

    def __init__(self, microscope_parameters):
        """
        Create a formatter for querying calibrations.

        :param microscope_parameters: The microscope parameters to use when creating queries. Only values in these parameters may be converted/formatted as queries.
        :type microscope_parameters: MicroscopeParameters
        """
        if not isinstance(microscope_parameters, MicroscopeParameters):
            raise TypeError(
                'Can only create calibration query objects for microscope parameters of type MicroscopeParameters, not {!r}'.format(
                    microscope_parameters))
        self.microscope_parameters = microscope_parameters
        super(CalibrationQueryFormatter, self).__init__()

    def __call__(self, value):
        """
        Creates a query for the requested value.

        :param value: Value to create a query for
        :type value: Parameter
        :return: Query string to be used with pandas.DataFrame.query()
        :rtype: str
        """
        return self.convert_field(value, 'q')

    def convert_field(self, value, conversion):
        """
        Converts a field from a format string.

        Creates a string suitable for querying a pandas.DataFrame for microscope calibrations for the value ig the conversion character is `"q"`, otherwise, the superclass convert_field method is called

        :param value: The value to convert. If this is a value in the microscope parameters of this formatter, ta query is created, otherwise a standard conversion is performed.
        :type value: Any
        :param conversion: The conversion string. If given as "q", a query is created, otherwise a standard conversion is performed
        :type conversion: str
        :return: The converted field
        :rtype: str
        """
        if conversion == 'q':
            if not value in self.microscope_parameters:
                raise ValueError(
                    'Value {value!r} is not in {self.microscope_parameters!r}'.format(value=value, self=self))
            if isinstance(value, Magnification):
                return self.create_query(value, self.microscope_parameters.mode, self.microscope_parameters.mag_mode,
                                         self.microscope_parameters.camera)
            elif isinstance(value, ImageScale):
                return self.create_query(self.microscope_parameters.mode, self.microscope_parameters.mag_mode,
                                         self.microscope_parameters.camera, self.microscope_parameters.magnification)
            elif isinstance(value, Cameralength):
                return self.create_query(value, self.microscope_parameters.camera)
            elif isinstance(value, DiffractionScale):
                return self.create_query(self.microscope_parameters.camera, self.microscope_parameters.cameralength)
            elif isinstance(value, SpotSize):
                return self.create_query(value, self.microscope_parameters.mode,
                                         self.microscope_parameters.condenser_aperture)
            elif isinstance(value, CondenserAperture):
                return self.create_query(value, self.microscope_parameters.magnification)
            elif isinstance(value, ConvergenceAngle):
                return self.create_query(value, self.microscope_parameters.condenser_aperture,
                                         self.microscope_parameters.magnification, self.microscope_parameters.mode,
                                         self.microscope_parameters.alpha)
            elif isinstance(value, RockingAngle):
                return self.create_query(value, self.microscope_parameters.mode, self.microscope_parameters.alpha)
            elif isinstance(value, ScanStep):
                if self.microscope_parameters.mode == 'STEM':
                    return self.create_query(value, self.microscope_parameters.mode)
                else:
                    return self.create_query(value, self.microscope_parameters.mode, self.microscope_parameters.alpha)
            else:
                return super().convert_field(value, conversion)
        else:
            return super().convert_field(value, conversion)

    def create_query(self, *args):
        """
        Creates a query for dataframes
        :param args: Arbitrary number of required parameters to query for.
        :return: A query string
        :rtype: str
        """
        required_parameters = [self.microscope_parameters.acceleration_voltage, self.microscope_parameters.microscope]
        parameters = [arg for arg in args]
        [parameters.append(required_parameter) for required_parameter in required_parameters]
        return ' & '.join([super(CalibrationQueryFormatter, self).convert_field(parameter, 'q') for parameter in parameters])


class CalibratedParameter(Parameter):
    """
    A calibrated parameter with a nominal value in addition to its calibrated value.
    """

    def __init__(self, parameter_name, value, units, nominal_value):
        """
        Create a calibrated parameter
        :param parameter_name: Name of parameter
        :param value: Actual (calibrated) value of the parameter
        :type value: int, float, str, datetime
        :param units: The units of the parameter
        :type units: str
        :param nominal_value: The nominal value of the parameter
        :type nominal_value: type(value)
        """
        super(CalibratedParameter, self).__init__(parameter_name, value, units)
        self.nominal_value = nominal_value

    def __str__(self):
        return '{self.__class__.__name__} {self.name}: {self.value} ({self.nominal_value}) {self.units}'.format(
            self=self)

    def __repr__(self):
        return '{self.__class__.__name__}({self.name!r}, {self.value!r}, {self.units!r}, {self.nominal_value!r})'.format(
            self=self)

    def __format__(self, format_spec):
        if format_spec == 'q':
            return QueryFormatter().format('{self!q}'.format(self=self))
        else:
            return '{self.value:{f}} ({self.nominal_value:{f}}) {self.units}'.format(self=self, f=format_spec)

    def nominal_value_is_defined(self):
        """
        Check whether the nominal value of the parameter is well-defined or not (i.e. not `nan`, `None`, `""`, or `"None"`)

        :returns: False if value is None, 'None', '', or nan
        :rtype: bool
        """
        if self.nominal_value is None:
            return False
        if isinstance(self.nominal_value, str):
            if self.nominal_value == '' or self.nominal_value == 'None':
                return False
            else:
                return True
        return not isnan(self.nominal_value)

    def set_nominal_value(self, newvalue):
        if not isinstance(newvalue, (int, float)):
            raise TypeError(
                'Invalid nominal value {nomval!r}. Nominal value must be same type as value {self.value!r}'.format(
                    nomval=newvalue, self=self))
        self.nominal_value = newvalue

    def as_dict(self):
        """Return calibrated parameter as a dictionary"""
        return {'{self.name}'.format(self=self): {'Nominal_value': self.nominal_value, 'Value': self.value,
                                                  'Units': self.units}}


class AccelerationVoltage(Parameter):
    def __init__(self, acceleration_voltage):
        """
        Create acceleration voltage object.
        :param acceleration_voltage: The acceleration voltage in V
        :type acceleration_voltage: float
        :return:
        """
        super(AccelerationVoltage, self).__init__('Acceleration Voltage', acceleration_voltage, 'V')

    def wavelength(self, m0=9.1093837015 * 1e-31, e=1.60217662 * 1e-19, h=6.62607004 * 1e-34, c=299792458):
        """
        Return the wavelength of an accelerated electron in [Å]

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
        V = self.value
        return h / sqrt(2 * m0 * e * V * (1.0 + (e * V / (2 * m0 * c ** 2)))) * 1E10


class Mode(Parameter):
    def __init__(self, mode):
        if not isinstance(mode, str):
            raise TypeError('Mode must be given as a string, not {!r}'.format(mode))
        super(Mode, self).__init__('Mode', mode, '')


class Alpha(Parameter):
    def __init__(self, alpha):
        if not isinstance(alpha, float):
            raise TypeError('Alpha must be given as a float, not {!r}'.format(alpha))
        super(Alpha, self).__init__('Alpha', alpha, '')


class MagMode(Parameter):
    def __init__(self, mag_mode):
        if not isinstance(mag_mode, str):
            raise TypeError('Magnification mode must be given as a string, not {!r}'.format(mag_mode))
        super(MagMode, self).__init__('Mag mode', mag_mode, '')


class Magnification(CalibratedParameter):
    def __init__(self, actual_magnification, nominal_magnification):
        super(Magnification, self).__init__('Magnification', actual_magnification, '', nominal_magnification)


class Cameralength(CalibratedParameter):
    def __init__(self, actual_cameralength, nominal_cameralength, units='cm'):
        super(Cameralength, self).__init__('Cameralength', actual_cameralength, units, nominal_cameralength)


class Spot(Parameter):
    def __init__(self, spot):
        super(Spot, self).__init__('Spot', spot, '')


class SpotSize(CalibratedParameter):
    def __init__(self, actual_spotsize, nominal_spotsize, units='nm'):
        super(SpotSize, self).__init__('Spotsize', actual_spotsize, units, nominal_spotsize)


class CondenserAperture(CalibratedParameter):
    def __init__(self, actual_aperture_size, nominal_aperture_size, units='um'):
        super(CondenserAperture, self).__init__('Condenser aperture', actual_aperture_size, units,
                                                nominal_aperture_size)


class ConvergenceAngle(CalibratedParameter):
    def __init__(self, actual_angle, nominal_angle, units='mrad'):
        super(ConvergenceAngle, self).__init__('Convergence angle', actual_angle, units, nominal_angle)


class RockingAngle(CalibratedParameter):
    def __init__(self, actual_angle, nominal_angle, units='deg'):
        super(RockingAngle, self).__init__('Rocking angle', actual_angle, units, nominal_angle)


class RockingFrequency(Parameter):
    def __init__(self, frequency):
        super(RockingFrequency, self).__init__('Rocking frequency', frequency, 'Hz')


class ScanStep(CalibratedParameter):
    def __init__(self, actual_step, nominal_step, direction, units='nm'):
        direction = str(direction)
        if len(direction) > 1:
            print('Direction for scan step is specified as a string with {n} characters: {direction}'.format(
                n=len(direction), direction=direction))
        else:
            direction = direction.capitalize()

        super(ScanStep, self).__init__('Step {direction!s}'.format(direction=direction), actual_step, units,
                                       nominal_step)
        self.direction = direction


class AcquisitionDate(Parameter):
    def __init__(self, date):
        super(AcquisitionDate, self).__init__('Acquisition Date', date, '')


class Camera(Parameter):
    def __init__(self, camera):
        if not isinstance(camera, str):
            raise TypeError('Camera must be given as a string, not {!r}'.format(camera))
        super(Camera, self).__init__('Camera', camera, '')


class Microscope(Parameter):
    def __init__(self, microscope):
        if not isinstance(microscope, str):
            raise TypeError('Microscope must be given as a string, not {!r}'.format(microscope))
        super(Microscope, self).__init__('Microscope', microscope, '')


class DiffractionScale(Parameter):
    def __init__(self, scale):
        """
        Create a diffraction scale

        :param scale: The scale of the image (1/Å per pixel)
        :type scale: float
        """
        if not isinstance(scale, float):
            raise TypeError('Scale must be given as float, not {scale!r}'.format(scale=scale))

        super(DiffractionScale, self).__init__('Scale', scale, units='1/Å')


class ImageScale(Parameter):
    def __init__(self, scale):
        """
        Create an image scale.

        :param scale: The scale of the image (nm/px)
        :type scale: float
        """
        if not isinstance(scale, float):
            raise TypeError('Scale must be given as float, not {scale!r}'.format(scale=scale))

        super(ImageScale, self).__init__('Scale', scale, units='nm')


class ExposureTime(Parameter):
    def __init__(self, exposure_time):
        """
        Create an exposure time object
        :param exposure_time: The exposure time in ms
        :type exposure_time: float
        """
        if not isinstance(exposure_time, float):
            raise TypeError('Exposure time given as float, not {exposure_time!r}'.format(exposure_time=exposure_time))
        super(ExposureTime, self).__init__('Exposure time', exposure_time, units='ms')


class MicroscopeParameters(object):
    def __init__(self,
                 acceleration_voltage=AccelerationVoltage(nan),
                 mode=Mode('None'),
                 alpha=Alpha(nan),
                 mag_mode=MagMode('None'),
                 magnification=Magnification(nan, nan),
                 image_scale=ImageScale(nan),
                 cameralength=Cameralength(nan, nan),
                 diffraction_scale=DiffractionScale(nan),
                 spot=Spot(nan),
                 spotsize=SpotSize(nan, nan),
                 condenser_aperture=CondenserAperture(nan, nan),
                 convergence_angle=ConvergenceAngle(nan, nan),
                 rocking_angle=RockingAngle(nan, nan),
                 rocking_frequency=RockingFrequency(nan),
                 scan_step_x=ScanStep(nan, nan, 'X'),
                 scan_step_y=ScanStep(nan, nan, 'Y'),
                 acquisition_date=AcquisitionDate('None'),
                 camera=Camera('None'),
                 exposure_time=ExposureTime(nan),
                 microscope=Microscope('None')
                 ):
        """
        Creates an object for controlling microscope parameters.

        :param acceleration_voltage: The acceleration voltage of the microscope in kV
        :type acceleration_voltage: AccelerationVoltage
        :param mode: The mode setting of the microscope (e.g. TEM, STEM, NBD, CBD, etc).
        :type mode: Mode
        :param alpha: The alpha setting of the microscope (condenser minilens setting)
        :type alpha: Alpha
        :param mag_mode: The magnification mode of the microscope (MAG, SAMAG, LM, etc)
        :type mag_mode: MagMode
        :param magnification: The magnification of the microscope.
        :type magnification: Magnification
        :param image_scale: The scale of images acquired with the microscope parameters (nm/px).
        :type image_scale: ImageScale
        :param cameralength: The cameralength of the microscope in cm
        :type cameralength: Cameralength
        :param diffraction_scale: The scale of diffraction patterns acquired with the microscope parameters (1/Å per px).
        :type diffraction_scale: DiffractionScale
        :param spot: The spot setting of the microscope
        :type spot: Spot
        :param spotsize: The spotsize of the microscope.
        :type spotsize: SpotSize
        :param condenser_aperture: The condenser aperature of the microscope in microns.
        :type condenser_aperture: CondenserAperture
        :param convergence_angle: The convergence angle of the microscope in mrad.
        :type convergence_angle: ConvergenceAngle
        :param rocking_angle: The rocking (precession) angle of the microscope in degrees.
        :type rocking_angle: RockingAngle
        :param rocking_frequency: The rocking (precession) angle of the microscope in Hz.
        :type rocking_frequency: RockingFrequency
        :param scan_step_x: The scan step size in the x-direction in nm
        :type scan_step_x: ScanStep
        :param scan_step_y: The scan step size in the y-direction in nm
        :type scan_step_y: ScanStep
        :param acquisition_date: The date of acquisition
        :type acquisition_date: AcquisitionDate
        :param camera: The name of the camera for the microscope.
        :type camera: Camera
        :param exposure_time: The exposure time of the experiment.
        :type exposure_time: ExposureTime
        :param microscope: The name of the microscope.
        :type microscope: Microscope
        """

        if not isinstance(acceleration_voltage, AccelerationVoltage):
            raise TypeError()
        if not isinstance(mode, Mode):
            raise TypeError()
        if not isinstance(mag_mode, MagMode):
            raise TypeError()
        if not isinstance(magnification, Magnification):
            raise TypeError()
        if not isinstance(image_scale, ImageScale):
            raise TypeError()
        if not isinstance(cameralength, Cameralength):
            raise TypeError()
        if not isinstance(diffraction_scale, DiffractionScale):
            raise TypeError()
        if not isinstance(spot, Spot):
            raise TypeError()
        if not isinstance(spotsize, SpotSize):
            raise TypeError()
        if not isinstance(condenser_aperture, CondenserAperture):
            raise TypeError()
        if not isinstance(convergence_angle, ConvergenceAngle):
            raise TypeError()
        if not isinstance(rocking_angle, RockingAngle):
            raise TypeError()
        if not isinstance(rocking_frequency, RockingFrequency):
            raise TypeError()
        if not isinstance(scan_step_x, ScanStep):
            raise TypeError()
        if not isinstance(scan_step_y, ScanStep):
            raise TypeError()
        if not isinstance(acquisition_date, AcquisitionDate):
            raise TypeError()
        if not isinstance(camera, Camera):
            raise TypeError()
        if not isinstance(exposure_time, ExposureTime):
            raise TypeError()
        if not isinstance(microscope, Microscope):
            raise TypeError()

        super(MicroscopeParameters, self).__init__()
        self._acceleration_voltage = acceleration_voltage
        self._mode = mode
        self._alpha = alpha
        self._mag_mode = mag_mode
        self._magnification = magnification
        self._image_scale = image_scale
        self._cameralength = cameralength
        self._diffraction_scale = diffraction_scale
        self._spot = spot
        self._spotsize = spotsize
        self._condenser_aperture = condenser_aperture
        self._convergence_angle = convergence_angle
        self._rocking_angle = rocking_angle
        self._rocking_frequency = rocking_frequency
        self._scan_step_x = scan_step_x
        self._scan_step_y = scan_step_y
        self._acquisition_date = acquisition_date
        self._camera = camera
        self._exposure_time = exposure_time
        self._microscope = microscope

        self._parameters = [
            self._acceleration_voltage,
            self._mode,
            self._alpha,
            self._magnification,
            self._image_scale,
            self._cameralength,
            self._diffraction_scale,
            self._mag_mode,
            self._rocking_angle,
            self._rocking_frequency,
            self._scan_step_y,
            self._scan_step_x,
            self._convergence_angle,
            self._condenser_aperture,
            self._spot,
            self._spotsize,
            self._acquisition_date,
            self._camera,
            self._exposure_time,
            self._microscope
        ]

    @property
    def acceleration_voltage(self):
        return self._acceleration_voltage

    @acceleration_voltage.setter
    def acceleration_voltage(self, acceleration_voltage):
        self._acceleration_voltage.set_value(acceleration_voltage)

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode):
        self._mode.set_value(mode)

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, alpha):
        self._alpha.set_value(alpha)

    @property
    def mag_mode(self):
        return self._mag_mode

    @mag_mode.setter
    def mag_mode(self, mag_mode):
        self._mag_mode.set_value(mag_mode)

    @property
    def magnification(self):
        return self._magnification

    @magnification.setter
    def magnification(self, magnification):
        if isinstance(magnification, (int, float)):
            self._magnification.set_value(magnification)
        else:
            try:
                self._magnification.set_value(magnification[1])
                self._magnification.set_nominal_value(magnification[0])
            except IndexError as e:
                raise MicroscopeParameterError(
                    'Cannot set magnification of microscope to {mag}: {e!r}'.format(mag=magnification, e=e))

    @property
    def cameralength(self):
        return self._cameralength

    @cameralength.setter
    def cameralength(self, cameralength):
        if isinstance(cameralength, (int, float)):
            self._cameralength.set_value(cameralength)
        else:
            try:
                self._cameralength.set_value(cameralength[1])
                self._cameralength.set_nominal_value(cameralength[0])
            except IndexError as e:
                raise MicroscopeParameterError(
                    'Cannot set cameralength of microscope to {cl}: {e!r}'.format(cl=cameralength, e=e))

    @property
    def image_scale(self):
        return self._image_scale

    @image_scale.setter
    def image_scale(self, scale):
        self._image_scale.set_value(scale)

    @property
    def diffraction_scale(self):
        return self._diffraction_scale

    @diffraction_scale.setter
    def diffraction_scale(self, scale):
        self._diffraction_scale.set_value(scale)

    @property
    def spot(self):
        return self._spot

    @spot.setter
    def spot(self, spot):
        self._spot.set_value(spot)

    @property
    def spotsize(self):
        return self._spotsize

    @spotsize.setter
    def spotsize(self, spotsize):
        if isinstance(spotsize, (int, float)):
            self._spotsize.set_value(spotsize)
        else:
            try:
                self._spotsize.set_value(spotsize[1])
                self._spotsize.set_nominal_value(spotsize[0])
            except IndexError as e:
                raise MicroscopeParameterError(
                    'Cannot set spotsize of microscope to {spotsize}: {e!r}'.format(spotsize=spotsize, e=e))

    @property
    def condenser_aperture(self):
        return self._condenser_aperture

    @condenser_aperture.setter
    def condenser_aperture(self, condenser_aperture):
        if isinstance(condenser_aperture, (int, float)):
            self._condenser_aperture.set_value(condenser_aperture)
        else:
            try:
                self._condenser_aperture.set_value(condenser_aperture[1])
                self._condenser_aperture.set_nominal_value(condenser_aperture[0])
            except IndexError as e:
                raise MicroscopeParameterError(
                    'Cannot set condenser_aperture of microscope to {ca}: {e!r}'.format(ca=condenser_aperture, e=e))

    @property
    def convergence_angle(self):
        return self._convergence_angle

    @convergence_angle.setter
    def convergence_angle(self, convergence_angle):
        if isinstance(convergence_angle, (int, float)):
            self._convergence_angle.set_value(convergence_angle)
        else:
            try:
                self._convergence_angle.set_value(convergence_angle[1])
                self._convergence_angle.set_nominal_value(convergence_angle[0])
            except IndexError as e:
                raise MicroscopeParameterError(
                    'Cannot set convergence_angle of microscope to {ca}: {e!r}'.format(ca=convergence_angle, e=e))

    @property
    def rocking_angle(self):
        return self._rocking_angle

    @rocking_angle.setter
    def rocking_angle(self, rocking_angle):
        if isinstance(rocking_angle, (int, float)):
            self._rocking_angle.set_value(rocking_angle)
        else:
            try:
                self._rocking_angle.set_value(rocking_angle[1])
                self._rocking_angle.set_nominal_value(rocking_angle[0])
            except IndexError as e:
                raise MicroscopeParameterError(
                    'Cannot set rocking_angle of microscope to {ra}: {e!r}'.format(ra=rocking_angle, e=e))

    @property
    def rocking_frequency(self):
        return self._rocking_frequency

    @rocking_frequency.setter
    def rocking_frequency(self, rocking_frequency):
        self._rocking_frequency.set_value(rocking_frequency)

    @property
    def scan_step_x(self):
        return self._scan_step_x

    @scan_step_x.setter
    def scan_step_x(self, step):
        if isinstance(step, (int, float)):
            self._scan_step_x.set_value(step)
        else:
            try:
                self._scan_step_x.set_value(step[1])
                self._scan_step_x.set_nominal_value(step[0])
            except IndexError as e:
                raise MicroscopeParameterError(
                    'Cannot set X step of microscope to {step}: {e!r}'.format(step=step, e=e))

    @property
    def scan_step_y(self):
        return self._scan_step_y

    @scan_step_y.setter
    def scan_step_y(self, step):
        if isinstance(step, (int, float)):
            self._scan_step_y.set_value(step)
        else:
            try:
                self._scan_step_y.set_value(step[1])
                self._scan_step_y.set_nominal_value(step[0])
            except IndexError as e:
                raise MicroscopeParameterError(
                    'Cannot set Y step of microscope to {step}: {e!r}'.format(step=step, e=e))

    @property
    def acquisition_date(self):
        return self._acquisition_date

    @acquisition_date.setter
    def acquisition_date(self, acquisition_date):
        self._acquisition_date.set_value(acquisition_date)

    @property
    def camera(self):
        return self._camera

    @camera.setter
    def camera(self, camera):
        self._camera.set_value(camera)

    @property
    def exposure_time(self):
        return self._exposure_time

    @exposure_time.setter
    def exposure_time(self, exposure_time):
        self._exposure_time.set_value(exposure_time)

    @property
    def microscope(self):
        return self._microscope

    @microscope.setter
    def microscope(self, microscope):
        self._microscope.set_value(microscope)

    def __str__(self):
        parameter_table = tabulate([[parameter.name, parameter.value, parameter.units,
                                     parameter.nominal_value] if isinstance(parameter, CalibratedParameter) else [
            parameter.name, parameter.value, parameter.units, ''] for parameter in self],
                                   headers=['Parameter', 'Value', 'Units', 'Nominal value'])
        return parameter_table

    def __iter__(self):
        for parameter in self._parameters:
            yield parameter

    def set_acceleration_voltage(self, acceleration_voltage):
        """
        Sets the acceleration voltage of the microscope
        :param acceleration_voltage: Acceleration voltage in kV
        :type acceleration_voltage: float
        :return:
        """
        self._acceleration_voltage.set_value(acceleration_voltage * 1E3)

    def set_mode(self, mode):
        """
        Sets the mode of the microscope
        :param mode: The mode of the microscope.
        :type mode: str
        :return:
        """
        self._mode.set_value(mode)

    def set_alpha(self, alpha):
        """
        Sets the alpha parameter of the microscope (condenser minilens setting)
        :param alpha: The alpha setting of the microscope
        :type alpha: int
        :return: 
        """
        self._alpha.set_value(alpha)

    def set_mag_mode(self, mag_mode):
        """
        Sets the magnificaiton mode of the microscope (i.e either MAG1/2, LOWMAG, or SAMAG for JEOL microscopes)
        :param mag_mode: The magnification mode of the microscope
        :type mag_mode: str
        :return: 
        """
        self._mag_mode.set_value(mag_mode)

    def set_magnification(self, magnification):
        """
        Sets the actual magnification of the microscope.
        :param magnification: The actual (calibrated) magnification of the microscope
        :type magnification: float
        :return: 
        """
        self._magnification.set_value(magnification)

    def set_nominal_magnification(self, magnification):
        """
        Sets the nominal magnification of the microscope.
        :param magnification: The nominal magnification of the microscope.
        :type magnification: float
        :return: 
        """
        self._magnification.set_nominal_value(magnification)

    def set_image_scale(self, scale):
        """
        Sets the image scale.
        :param scale: The scale given in nm/px
        :type scale: float
        :return: 
        """
        self._image_scale.set_value(scale)

    def set_cameralength(self, cameralength):
        """
        Sets the actual cameralength of the microscope.
        :param cameralength: The actual (calibrated) cameralength of the microscope in cm
        :type cameralength: float
        :return: 
        """
        self._cameralength.set_value(cameralength)

    def set_nominal_cameralength(self, cameralength):
        """
        Sets the nominal cameralength of the microscope.
        :param cameralength: The nominal cameralength of the microscope in cm
        :type cameralength: float
        :return:
        """
        self._cameralength.set_nominal_value(cameralength)

    def set_diffraction_scale(self, scale):
        """
        Sets the diffraction scale.
        :param scale: The scale given in 1/Å/px
        :type scale: float
        :return: 
        """
        self._diffraction_scale.set_value(scale)

    def set_spot(self, spot):
        """
        Sets the spot setting of the microscope. Only used for certain modes (e.g. TEM mode)

        :param spot: The spot setting of the microscope (condenser lens "X" setting)
        :type spot: int
        :return:
        """
        self._spot.set_value(spot)

    def setSpotsize(self, spotsize):
        """
        Sets the actual spotsize of the microscope.
        :param spotsize: The actual (calibrated) spotsize of the microscope in nm
        :type spotsize: float
        :return:
        """
        self._spotsize.set_value(spotsize)

    def set_nominal_spotsize(self, spotsize):
        """
        Sets the nominal spotsize of the microscope.
        :param spotsize: The nominal spotsize of the microscope in nm
        :type spotsize: float
        :return:
        """
        self._spotsize.set_nominal_value(spotsize)

    def set_condenser_aperture(self, aperturesize):
        """
        Sets the actual condenser aperture size of the microscope.
        :param aperturesize: The actual (calibrated) condenser aperture size in microns
        :type aperturesize: float
        :return:
        """
        self._condenser_aperture.set_value(aperturesize)

    def set_nominal_condenser_aperture(self, aperturesize):
        """
        Sets the nominal condenser aperture size of the microscope.
        :param aperturesize: The nominal condenser aperture size in microns
        :type aperturesize: float
        :return:
        """
        self._condenser_aperture.set_nominal_value(aperturesize)

    def set_convergence_angle(self, angle):
        """
        Sets the actual convergence angle of the microscope/beam.
        :param angle: The actual (calibrated) semi-convergence angle of the microscope in mrad
        :type angle: float
        :return:
        """
        self._convergence_angle.set_value(angle)

    def set_nominal_convergence_angle(self, angle):
        """
        Sets the nominal convergence angle of the microscope/beam.
        :param angle: The nominal semi-convergence angle of the microscope in mrad.
        :type angle: float
        :return:
        """
        self._convergence_angle.set_nominal_value(angle)

    def set_rocking_angle(self, angle):
        """
        Sets the actual rocking (precession) angle of the microscope.
        :param angle: The actual (calibrated) rocking/precession angle of the microscope.
        :type angle: float
        :return:
        """
        self._rocking_angle.set_value(angle)

    def set_nominal_rocking_angle(self, angle):
        """
        Sets the nominal rocking (precession) angle of the microscope.
        :param angle: The nominal rocking/precession angle of the microscope
        :type angle: float
        :return:
        """
        self._rocking_angle.set_nominal_value(angle)

    def set_rocking_frequency(self, frequency):
        """
        Sets the (nominal) rocking (precession) frequency of the microscope.
        :param frequency: The nominal rocking/precession frequency of the microscope.
        :type frequency: float
        :return:
        """
        self._rocking_frequency.set_value(frequency)

    def set_scan_step_x(self, step):
        """
        Sets the actual scan step size in the x-direction.
        :param step: The actual (calibrated) scan step size
        :type step: float
        :return:
        """
        self._scan_step_x.set_value(step)

    def set_nominal_scan_step_x(self, step):
        """
        Sets the nominal scan step size in the x-direction.
        :param step: The nominal scan step size
        :type step: float
        :return:
        """
        self._scan_step_x.set_nominal_value(step)

    def set_scan_step_y(self, step):
        """
        Sets the actual scan step size in the y-direction.
        :param step: The actual (calibrated) scan step size
        :type step: float
        :return:
        """
        self._scan_step_y.set_value(step)

    def set_nominal_scan_step_y(self, step):
        """
        Sets the nominal scan step size in the y-direction.
        :param step: The nominal scan step size
        :type step: float
        :return:
        """
        self._scan_step_y.set_nominal_value(step)

    def set_acquisition_date(self, date):
        """
        Sets the acquisition date of the data
        :param date: The date of acquisition
        :type date: datetime
        :return:
        """
        self._acquisition_date.set_value(date)

    def set_camera(self, camera):
        """
        Sets the camera name
        :param camera: The name of the camera
        :type camera: str
        :return:
        """
        self._camera.set_value(camera)

    def set_microscope(self, microscope):
        """
        Sets the microscope name
        :param microscope: The name of the microscope
        :type microscope: str
        :return:
        """
        self._microscope.set_value(microscope)

    def set_values_from_calibrationtable(self, calibrationtable, print_results=False):
        """
        Sets the values of CalibratedParameters based on a calibration table.
        :param calibrationtable: the table to pick values from.
        :param print_results:
        :return:
        """
        query_formatter = CalibrationQueryFormatter(self)

        for parameter in self:
            try:
                if isinstance(parameter, CalibratedParameter):
                    try:
                        query = query_formatter(parameter)
                    except Exception as e:
                        raise CalibrationError(e)
                    else:
                        try:
                            parameter.set_value_from_calibrationtable(calibrationtable, query, print_results)
                        except UndefinedVariableError:
                            print(
                                'Query {query} did not yield any matches in {table!r}. Continuing without calibrating this value.'.format(
                                    query=query, table=calibrationtable))
            except CalibrationError as e:
                print(
                    'Calibration error occurred when calibrating parameter {parameter!r}:\n{e}.\nContinuing without calibrating this value.'.format(
                        parameter=parameter, e=e))
                raise e

        # Calibrate the scales after all the calibrated parameters have been set.
        for parameter in [self._image_scale, self._diffraction_scale]:
            try:
                try:
                    query = query_formatter(parameter)
                except Exception as e:
                    raise CalibrationError(e)
                else:
                    try:
                        parameter.set_value_from_calibrationtable(calibrationtable, query, print_results)
                    except UndefinedVariableError:
                        print(
                            'Query {query} did not yield any matches in {table!r}. Continuing without calibrating this value.'.format(
                                query=query, table=calibrationtable))
            except CalibrationError as e:
                print(
                    'Calibration error occurred when calibrating parameter {parameter!r}:\n{e}.\nContinuing without calibrating this value.'.format(
                        parameter=parameter, e=e))
                raise e

    def get_parameters(self):
        """
        Return the parameters of the microscope.
        :return: parameters of the microscope.
        :rtype: list
        """
        return list(self._parameters)

    def as_dataframe2D(self):
        """
        Return the parameters of the microscope as a 2D pandas dataframe
        :return: parameters.
        :rtype: pandas.DataFrame
        """
        return pd.DataFrame([[parameter.name, parameter.nominal_value, parameter.value, parameter.units] if isinstance(
            parameter, CalibratedParameter) else [parameter.name, '', parameter.value, parameter.units] for parameter in
                             self], columns=['Name', 'Nominal Value', 'Value', 'Units'])

    def dataframe1D(self):
        """
        Return the parameters as a 1D dataframe.
        :return: parameters. The parameters of the microscope in a horizontal dataframe
        :rtype: pandas.DataFrame
        """
        return pd.DataFrame([[
            self._mode.value,
            self._alpha.value,
            self._spot.value,
            self._spotsize.nominal_value,
            self._spotsize.value,
            self._convergence_angle.nominal_value,
            self._convergence_angle.value,
            self._condenser_aperture.nominal_value,
            self._condenser_aperture.value,
            self._magnification.nominal_value,
            self._magnification.value,
            self._cameralength.nominal_value,
            self._cameralength.value,
            self._rocking_angle.nominal_value,
            self._rocking_angle.value,
            self._rocking_frequency.value,
            self._scan_step_x.nominal_value,
            self._scan_step_x.value,
            self._scan_step_y.nominal_value,
            self._scan_step_y.value,
            self._acquisition_date.value,
            self._camera.value,
            self._microscope.value
        ]], columns=[
            self._mode.name,
            self._alpha.name,
            self._spot.name,
            'Nominal {}'.format(self._spotsize.name),
            self._spotsize.name,
            'Nominal {}'.format(self._convergence_angle.name),
            self._convergence_angle.name,
            'Nominal {}'.format(self._condenser_aperture.name),
            self._condenser_aperture.name,
            'Nominal {}'.format(self._magnification.name),
            self._magnification.name,
            'Nominal {}'.format(self._cameralength.name),
            self._cameralength.name,
            'Nominal {}'.format(self._rocking_angle.name),
            self._rocking_angle.name,
            self._rocking_frequency.name,
            'Nominal {}'.format(self._scan_step_x.name),
            self._scan_step_x.name,
            'Nominal {}'.format(self._scan_step_y.name),
            self._scan_step_y.name,
            self._acquisition_date.name,
            self._camera.name,
            self._microscope.name
        ])

    def get_parameters_as_dict(self):
        """
        Return a dictionary of the parameters of the microscope
        :return: parameters
        :rtype: dict
        """
        params = {}
        [params.update({parameter.name.replace(' ', '_').lower(): {'Nominal value': parameter.nominal_value,
                                                                   'Actual value': parameter.value,
                                                                   'Units': parameter.units}}) if isinstance(
            parameter, CalibratedParameter) else params.update(
            {parameter.name.replace(' ', '_').lower(): {'Value': parameter.value, 'Units': parameter.units}}) for
         parameter in self]
        return params

    def get_defined_parameters_(self, as_dict=False):
        """
        Return the defined parameters of the microscope as either a list or as a dictionary.
        :param as_dict: Whether to return a dictionary or not.
        :type as_dict: bool
        :return: defined_parameters. Parameters where parameter.is_defined() is True
        :rtype: list or dict.
        """
        defined_parameters = [parameter for parameter in self if parameter.is_defined()]
        if as_dict:
            params = {}
            [params.update({
                parameter.name.replace(' ', '_').lower():
                    {
                        'nominal_value': parameter.nominal_value,
                        'actual_value': parameter.value
                    }
            }) if isinstance(parameter, CalibratedParameter) else
             params.update({
                 parameter.name.replace(' ', '_').lower():
                     {
                         'Value': parameter.value
                     }
             }) for parameter in defined_parameters]
        else:
            params = defined_parameters
        return params


class Detector(object):
    """
    A detector object
    """

    def __init__(self,
                 nx=Parameter('Pixels x', nan, 'px'),
                 ny=Parameter('Pixels y', nan, 'px'),
                 dx=Parameter('Pixels size x', nan, 'm'),
                 dy=Parameter('Pixels size y', nan, 'm'),
                 ):
        """
        Create a detector object.
        :param nx: The number of pixels in x-direction
        :param ny: The number of pixels in y-direction
        :param dx: The pixel size in x-direction
        :param dy: The pixel size in y-direction
        :type nx: int
        :type ny: int
        :type dx: float
        :type dy: float
        """

        if not isinstance(nx, Parameter):
            raise TypeError()
        if not isinstance(ny, Parameter):
            raise TypeError()
        if not isinstance(dx, Parameter):
            raise TypeError()
        if not isinstance(dy, Parameter):
            raise TypeError()

        super(Detector, self).__init__()
        self.nx = nx
        self.ny = ny
        self.dx = dx
        self.dy = dy

    def __str__(self):
        return '{self.__class__.__name__} with {self.nx:} x {self.ny} pixels and pixel sizes [m] {self.dx} and {self.dy})'.format(
            self=self)

    def get_shape(self):
        """
        Get the number of pixels in x and y directions
        :return: shape as np.array((Nx, Ny))
        :rtype: numpy.ndarray
        """
        return np.array([self.nx.value, self.ny.value])

    def get_pixel_size(self):
        """
        Get the pixel size as an array
        :return: pixel sizes in m as np.array((Dx, Dy))
        :rtype: numpy.ndarray
        """
        return np.array([self.dx.value, self.dy.value])

    def get_physical_size(self):
        """
        Get the physical size of the detector.
        :return: The physical size of the detector in m as np.array((float_x, float_y))
        :rtype: numpy.ndarray
        """
        return self.get_shape() * self.get_pixel_size()

    def set_nx(self, value):
        """
        Sets the number of pixels in x-direction.
        :param value: The number of pixels in x-direction
        :type value: int
        :return:
        """
        self.nx.set_value(value)

    def set_ny(self, value):
        """
        Sets the number of pixels in y-direction
        :param value: The number of pixels in y-direction
        :type value: int
        :return:
        """
        self.ny.set_value(value)

    def set_dx(self, value):
        """
        Sets the pixel size in x-direction
        :param value: The pixel size in m
        :type value: float
        :return:
        """
        self.dx.set_value(value)

    def set_dy(self, value):
        """
        Sets the pixel size in y-direction
        :param value: The pixel size in m
        :type value: float
        :return:
        """
        self.dy.set_value(value)
