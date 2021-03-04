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


class Parameter(object):
    """
    A parameter
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
                #Handle empty units specially for Parameters.
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
            elif isinstance(value, Cameralength):
                return self.create_query(value)
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

        query = query + ' & ' + QueryFormatter().convert_field(self, 'q')
        try:
            calibration_rows = calibrationtable.query(query)
            key = '{self.name} ({self.units})'.format(self=self)
            values = calibration_rows[key].values  # Get the actual values from the calibration rows.
        except UndefinedVariableError:
            print(
                'Unable to query calibration table for \n"{query}"\ndue to missing (required) columns. Please check that the calibration file column headers for errors. Continuing without calibrating this value.\n'.format(
                    query=query, table=calibrationtable))
        except KeyError as e:
            print('No column was found for {key} in \n{calibration_rows}.\nPlease check that the calibration file column headers for errors. Continuing withoug calibrating this value.\n'.format(key=key, calibration_rows=calibration_rows))
        else:
            if len(values) > 0:
                if len(values) > 1:
                    print('Multiple calibration rows fits with query "{query}".\nUsing last entry.\n'.format(query=query))
                value = values[-1]
            else:
                print('No calibration found for {self!r} in calibration table after querying for "{query}".\n'.format(self=self, table=calibrationtable, query=query))
                value = nan
            if bool(print_result):
                print('Result from query "{query}" to calibration table: {value!r}\n'.format(query=query,
                                                                                                     table=calibrationtable,
                                                                                                     value=value))
            self.set_value(value)

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


class MicroscopeParameters(object):
    def __init__(self,
                 acceleration_voltage=AccelerationVoltage(nan),
                 mode=Mode('None'),
                 alpha=Alpha(nan),
                 mag_mode=MagMode('None'),
                 magnification=Magnification(nan, nan),
                 cameralength=Cameralength(nan, nan),
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
                 microscope=Microscope('None')
                 ):
        """
        Creates a microscope object.
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
        :param cameralength: The cameralength of the microscope in cm
        :type cameralength: Cameralength
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
        if not isinstance(cameralength, Cameralength):
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
        if not isinstance(microscope, Microscope):
            raise TypeError()

        super(MicroscopeParameters, self).__init__()
        self.acceleration_voltage = acceleration_voltage
        self.mode = mode
        self.alpha = alpha
        self.mag_mode = mag_mode
        self.magnification = magnification
        self.cameralength = cameralength
        self.spot = spot
        self.spotsize = spotsize
        self.condenser_aperture = condenser_aperture
        self.convergence_angle = convergence_angle
        self.rocking_angle = rocking_angle
        self.rocking_frequency = rocking_frequency
        self.scan_step_x = scan_step_x
        self.scan_step_y = scan_step_y
        self.acquisition_date = acquisition_date
        self.camera = camera
        self.microscope = microscope

    def __str__(self):
        parameter_table = tabulate([[parameter.name, parameter.value, parameter.units,
                                     parameter.nominal_value] if isinstance(parameter, CalibratedParameter) else [
            parameter.name, parameter.value, parameter.units, ''] for parameter in self],
                                   headers=['Parameter', 'Value', 'Units', 'Nominal value'])
        return parameter_table

    def __iter__(self):
        parameters = [
            self.acceleration_voltage,
            self.mode,
            self.alpha,
            self.magnification,
            self.cameralength,
            self.mag_mode,
            self.rocking_angle,
            self.rocking_frequency,
            self.scan_step_y,
            self.scan_step_x,
            self.convergence_angle,
            self.condenser_aperture,
            self.spot,
            self.spotsize,
            self.acquisition_date,
            self.camera,
            self.microscope
        ]

        for parameter in parameters:
            yield parameter

    def set_acceleration_voltage(self, acceleration_voltage):
        """
        Sets the acceleration voltage of the microscope
        :param acceleration_voltage: Acceleration voltage in kV
        :type acceleration_voltage: float
        :return:
        """
        self.acceleration_voltage.set_value(acceleration_voltage * 1E3)

    def set_mode(self, mode):
        """
        Sets the mode of the microscope
        :param mode: The mode of the microscope.
        :type mode: str
        :return:
        """
        self.mode.set_value(mode)

    def set_alpha(self, alpha):
        """
        Sets the alpha parameter of the microscope (condenser minilens setting)
        :param alpha: The alpha setting of the microscope
        :type alpha: int
        :return: 
        """
        self.alpha.set_value(alpha)

    def set_mag_mode(self, mag_mode):
        """
        Sets the magnificaiton mode of the microscope (i.e either MAG1/2, LOWMAG, or SAMAG for JEOL microscopes)
        :param mag_mode: The magnification mode of the microscope
        :type mag_mode: str
        :return: 
        """
        self.mag_mode.set_value(mag_mode)

    def set_magnification(self, magnification):
        """
        Sets the actual magnification of the microscope.
        :param magnification: The actual (calibrated) magnification of the microscope
        :type magnification: float
        :return: 
        """
        self.magnification.set_value(magnification)

    def set_nominal_magnification(self, magnification):
        """
        Sets the nominal magnification of the microscope.
        :param magnification: The nominal magnification of the microscope.
        :type magnification: float
        :return: 
        """
        self.magnification.set_nominal_value(magnification)

    def set_cameralength(self, cameralength):
        """
        Sets the actual cameralength of the microscope.
        :param cameralength: The actual (calibrated) cameralength of the microscope in cm
        :type cameralength: float
        :return: 
        """
        self.cameralength.set_value(cameralength)

    def set_nominal_cameralength(self, cameralength):
        """
        Sets the nominal cameralength of the microscope.
        :param cameralength: The nominal cameralength of the microscope in cm
        :type cameralength: float
        :return:
        """
        self.cameralength.set_nominal_value(cameralength)

    def set_spot(self, spot):
        """
        Sets the spot setting of the microscope. Only used for certain modes (e.g. TEM mode)

        :param spot: The spot setting of the microscope (condenser lens "X" setting)
        :type spot: int
        :return:
        """
        self.spot.set_value(spot)

    def setSpotsize(self, spotsize):
        """
        Sets the actual spotsize of the microscope.
        :param spotsize: The actual (calibrated) spotsize of the microscope in nm
        :type spotsize: float
        :return:
        """
        self.spotsize.set_value(spotsize)

    def set_nominal_spotsize(self, spotsize):
        """
        Sets the nominal spotsize of the microscope.
        :param spotsize: The nominal spotsize of the microscope in nm
        :type spotsize: float
        :return:
        """
        self.spotsize.set_nominal_value(spotsize)

    def set_condenser_aperture(self, aperturesize):
        """
        Sets the actual condenser aperture size of the microscope.
        :param aperturesize: The actual (calibrated) condenser aperture size in microns
        :type aperturesize: float
        :return:
        """
        self.condenser_aperture.set_value(aperturesize)

    def set_nominal_condenser_aperture(self, aperturesize):
        """
        Sets the nominal condenser aperture size of the microscope.
        :param aperturesize: The nominal condenser aperture size in microns
        :type aperturesize: float
        :return:
        """
        self.condenser_aperture.set_nominal_value(aperturesize)

    def set_convergence_angle(self, angle):
        """
        Sets the actual convergence angle of the microscope/beam.
        :param angle: The actual (calibrated) semi-convergence angle of the microscope in mrad
        :type angle: float
        :return:
        """
        self.convergence_angle.set_value(angle)

    def set_nominal_convergence_angle(self, angle):
        """
        Sets the nominal convergence angle of the microscope/beam.
        :param angle: The nominal semi-convergence angle of the microscope in mrad.
        :type angle: float
        :return:
        """
        self.convergence_angle.set_nominal_value(angle)

    def set_rocking_angle(self, angle):
        """
        Sets the actual rocking (precession) angle of the microscope.
        :param angle: The actual (calibrated) rocking/precession angle of the microscope.
        :type angle: float
        :return:
        """
        self.rocking_angle.set_value(angle)

    def set_nominal_rocking_angle(self, angle):
        """
        Sets the nominal rocking (precession) angle of the microscope.
        :param angle: The nominal rocking/precession angle of the microscope
        :type angle: float
        :return:
        """
        self.rocking_angle.set_nominal_value(angle)

    def set_rocking_frequency(self, frequency):
        """
        Sets the (nominal) rocking (precession) frequency of the microscope.
        :param frequency: The nominal rocking/precession frequency of the microscope.
        :type frequency: float
        :return:
        """
        self.rocking_frequency.set_value(frequency)

    def set_scan_step_x(self, step):
        """
        Sets the actual scan step size in the x-direction.
        :param step: The actual (calibrated) scan step size
        :type step: float
        :return:
        """
        self.scan_step_x.set_value(step)

    def set_nominal_scan_step_x(self, step):
        """
        Sets the nominal scan step size in the x-direction.
        :param step: The nominal scan step size
        :type step: float
        :return:
        """
        self.scan_step_x.set_nominal_value(step)

    def set_scan_step_y(self, step):
        """
        Sets the actual scan step size in the y-direction.
        :param step: The actual (calibrated) scan step size
        :type step: float
        :return:
        """
        self.scan_step_y.set_value(step)

    def set_nominal_scan_step_y(self, step):
        """
        Sets the nominal scan step size in the y-direction.
        :param step: The nominal scan step size
        :type step: float
        :return:
        """
        self.scan_step_y.set_nominal_value(step)

    def set_acquisition_date(self, date):
        """
        Sets the acquisition date of the data
        :param date: The date of acquisition
        :type date: datetime
        :return:
        """
        self.acquisition_date.set_value(date)

    def set_camera(self, camera):
        """
        Sets the camera name
        :param camera: The name of the camera
        :type camera: str
        :return:
        """
        self.camera.set_value(camera)

    def set_microscope(self, microscope):
        """
        Sets the microscope name
        :param microscope: The name of the microscope
        :type microscope: str
        :return:
        """
        self.microscope.set_value(microscope)

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
                            print('Query {query} did not yield any matches in {table!r}. Continuing without calibrating this value.'.format(query=query, table=calibrationtable))
            except CalibrationError as e:
                print('Calibration error occurred when calibrating parameter {parameter!r}:\n{e}.\nContinuing without calibrating this value.'.format(parameter=parameter, e=e))
                raise e

    def get_parameters(self):
        """
        Return the parameters of the microscope.
        :return: parameters of the microscope.
        :rtype: list
        """
        return [parameter for parameter in self]

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
            self.mode.value,
            self.alpha.value,
            self.spot.value,
            self.spotsize.nominal_value,
            self.spotsize.value,
            self.convergence_angle.nominal_value,
            self.convergence_angle.value,
            self.condenser_aperture.nominal_value,
            self.condenser_aperture.value,
            self.magnification.nominal_value,
            self.magnification.value,
            self.cameralength.nominal_value,
            self.cameralength.value,
            self.rocking_angle.nominal_value,
            self.rocking_angle.value,
            self.rocking_frequency.value,
            self.scan_step_x.nominal_value,
            self.scan_step_x.value,
            self.scan_step_y.nominal_value,
            self.scan_step_y.value,
            self.acquisition_date.value,
            self.camera.value,
            self.microscope_name.value
        ]], columns=[
            self.mode.name,
            self.alpha.name,
            self.spot.name,
            'Nominal {}'.format(self.spotsize.name),
            self.spotsize.name,
            'Nominal {}'.format(self.convergence_angle.name),
            self.convergence_angle.name,
            'Nominal {}'.format(self.condenser_aperture.name),
            self.condenser_aperture.name,
            'Nominal {}'.format(self.magnification.name),
            self.magnification.name,
            'Nominal {}'.format(self.cameralength.name),
            self.cameralength.name,
            'Nominal {}'.format(self.rocking_angle.name),
            self.rocking_angle.name,
            self.rocking_frequency.name,
            'Nominal {}'.format(self.scan_step_x.name),
            self.scan_step_x.name,
            'Nominal {}'.format(self.scan_step_y.name),
            self.scan_step_y.name,
            self.acquisition_date.name,
            self.camera.name,
            self.microscope_name.name
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
