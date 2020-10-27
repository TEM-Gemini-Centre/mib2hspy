from math import nan, isnan
from datetime import datetime
from tabulate import tabulate
import pandas as pd
import numpy as np


class Parameter(object):
    """
    A parameter
    """

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
        if not isinstance(value, (int, float, str, datetime)):
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
        :type newvalue: int, float, str, datetime
        :return:
        """
        if not isinstance(newvalue, (int, float, str, datetime)):
            raise TypeError()
        self.value = newvalue

    def __str__(self):
        return '{self.__class__.__name__} {self.name}: {self.value} {self.units}'.format(
            self=self)

    def __repr__(self):
        return '{self.__class__.__name__}({self.name!r}, {self.value!r}, {self.units!r})'.format(
            self=self)

    def __format__(self, format_spec):
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
        return '{self.value:{f}} ({self.nominal_value:{f}}) {self.units}'.format(self=self, f=format_spec)

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


class Microscope(object):
    def __init__(self,
                 acceleration_voltage=Parameter('HT', nan, 'V'),
                 mode=Parameter('Mode', '', ''),
                 alpha=Parameter('Alpha', nan, ''),
                 mag_mode=Parameter('Magnification Mode', '', ''),
                 magnification=CalibratedParameter('Magnification', nan, '', nan),
                 cameralength=CalibratedParameter('Camera length', nan, 'cm', nan),
                 spot=Parameter('Spot', nan, ''),
                 spotsize=CalibratedParameter('Spotsize', nan, 'nm', nan),
                 condenser_aperture=CalibratedParameter('Condenser aperture', nan, 'um', nan),
                 convergence_angle=CalibratedParameter('Convergence angle', nan, 'mrad', nan),
                 rocking_angle=CalibratedParameter('Rocking angle', nan, 'deg', nan),
                 rocking_frequency=Parameter('Rocking frequency', nan, 'Hz'),
                 scan_step_x=CalibratedParameter('Step X', nan, 'nm', nan),
                 scan_step_y=CalibratedParameter('Step Y', nan, 'nm', nan),
                 acquisition_date=Parameter('Acquisition Date', '', '')
                 ):
        """
        Creates a microscope object.
        :param acceleration_voltage: The acceleartion voltage of the microscope in kV
        :type acceleration_voltage: Parameter
        :param mode: The mode setting of the microscope (e.g. TEM, STEM, NBD, CBD, etc).
        :type mode: Parameter
        :param alpha: The alpha setting of the microscope (condenser minilens setting)
        :type alpha: Parameter
        :param mag_mode: The magnification mode of the microscope (MAG, SAMAG, LM, etc)
        :type mag_mode: Parameter
        :param magnification: The magnification of the microscope.
        :type magnification: CalibratedParameter
        :param cameralength: The cameralength of the microscope in cm
        :type cameralength: CalibratedParameter
        :param spot: The spot setting of the microscope
        :type spot: Parameter
        :param spotsize: The spotsize of the microscope.
        :type spotsize: CalibratedParameter
        :param condenser_aperture: The condenser aperature of the microscope in microns.
        :type condenser_aperture: CalibratedParameter
        :param convergence_angle: The convergence angle of the microscope in mrad.
        :type convergence_angle: CalibratedParameter
        :param rocking_angle: The rocking (precession) angle of the microscope in degrees.
        :type rocking_angle: CalibratedParameter
        :param rocking_frequency: The rocking (precession) angle of the microscope in Hz.
        :type rocking_frequency: Parameter
        :param scan_step_x: The scan step size in the x-direction in nm
        :type scan_step_x: CalibratedParameter
        :param scan_step_y: The scan step size in the y-direction in nm
        :type scan_step_y: CalibratedParameter
        :param acquisition_date: The date of acquisition
        :type acquisition_date: Parameter
        """

        if not isinstance(acceleration_voltage, Parameter):
            raise TypeError()
        if not isinstance(mode, Parameter):
            raise TypeError()
        if not isinstance(mag_mode, Parameter):
            raise TypeError()
        if not isinstance(magnification, CalibratedParameter):
            raise TypeError()
        if not isinstance(cameralength, CalibratedParameter):
            raise TypeError()
        if not isinstance(spot, Parameter):
            raise TypeError()
        if not isinstance(spotsize, CalibratedParameter):
            raise TypeError()
        if not isinstance(condenser_aperture, CalibratedParameter):
            raise TypeError()
        if not isinstance(convergence_angle, CalibratedParameter):
            raise TypeError()
        if not isinstance(rocking_angle, CalibratedParameter):
            raise TypeError()
        if not isinstance(rocking_frequency, Parameter):
            raise TypeError()
        if not isinstance(scan_step_x, CalibratedParameter):
            raise TypeError()
        if not isinstance(scan_step_y, CalibratedParameter):
            raise TypeError()
        if not isinstance(acquisition_date, Parameter):
            raise TypeError()

        super(Microscope, self).__init__()
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
            self.acquisition_date
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
            self.acquisition_date.value
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
            self.acquisition_date.name
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
