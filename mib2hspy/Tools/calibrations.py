import pandas as pd
import datetime as dt
from math import nan, sqrt, pi, atan, tan


class Calibration(object):
    def __init__(self, nominal_value, actual_value, units, name, date):
        """
        Create a calibration object
        :param nominal_value: The nominal value
        :param actual_value: The actual value
        :param units: The units of the values
        :param name: The name of the calibration/measure
        :param date: The date of the calibration in the format "yyyy-mm-dd"
        :type nominal_value: Union[int, float]
        :type actual_value: Union[int, float]
        :type units: str
        :type name: str
        :type date: str
        """
        self.nominal_value = float(nominal_value)
        self.actual_value = float(actual_value)
        self.units = str(units)
        self.name = str(name)
        self.date = dt.datetime.strptime(date, '%Y-%m-%d').date()

    def __repr__(self):
        return '{self.__class__.__name__}({self.nominal_value!r}, {self.actual_value!r}, {self.units!r}, {self.name!r}, {self.date!r})'.format(
            self=self)

    def __format__(self, format_spec):
        return '{self.nominal_value:{f}}: {self.actual_value:{f}}'.format(self=self, f=format_spec)

    def __str__(self):
        return '{self.__class__.__name__} {self.name} ({self.date!s}):\n\t{self:.2f} {self.units}'.format(self=self)

    def as_dataframe(self):
        """
        Return the calibration as a dataframe.
        :return: dataframe with calibration data
        :rtype: pandas.DataFrame
        """
        return pd.DataFrame([self.nominal_value, self.actual_value, self.date],
                            columns=['Nominal {self.name} ({self.units})'.format(self=self),
                                     '{self.name} ({self.units})'.format(self=self), 'Date'])

    def add_to_dataframe(self, dataframe, remove_duplicates=True):
        """
        Add the calibration to a dataframe
        :param remove_duplicates: Whether to drop any duplicates
        :param dataframe: The dataframe to add the calibration to
        :type dataframe: pandas.DataFrame
        :type remove_duplicates: bool
        :return: A dataframe with the calibration added, unless it is a duplicate and remove_duplicates is True
        :rtype: pandas.DataFrame
        """
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError('Cannot add {self!r} to DataFrame {dataframe!r}.'.format(self=self, dataframe=dataframe))
        df = pd.concat([dataframe, self.as_dataframe()], ignore_index=True, join='outer')
        df.sort_values(by='Date', axis=0, inplace=True, ascending=True)
        if remove_duplicates:
            df.drop_duplicates(inplace=True, ignore_index=True, keep='last')

        return df


class MicroscopeCalibration(Calibration):
    def __init__(self, *args, scale=None, acceleration_voltage=None, mode=None, mag_mode=None, alpha=None, spot=None,
                 spot_size=None, camera=None, microscope=None):
        """
        Create a microscope calibration.
        :param args: Positional arguments passed to Calibration().
        :param scale: The scale of the calibrated image.
        :param acceleration_voltage: The acceleration voltage of the microscope. Default is None.
        :param mode: The mode of the microscope. Default is None.
        :param mag_mode: The magnification mode of the microscope. Default is None.
        :param alpha: The alpha-setting of the microscope. Default is None.
        :param spot: The spot-setting of the microscope. Default is None.
        :param spot_size: The nominal spot-size of the microscope. Default is None.
        :param camera: The name of the camera to calibrate. Default is None.
        :param microscope: The name of the microscope. Default is None.
        :type scale: Scale
        :type acceleration_voltage: Union[int, float]
        :type mode: str
        :type mag_mode: str
        :type alpha: Union[int, float, str]
        :type spot: Union[int, float, str]
        :type spot_size: Union[int, float, str]
        :type camera: str
        :type microscope: str
        """
        super().__init__(*args)
        if scale is not None:
            if not isinstance(scale, Scale):
                raise TypeError(
                    'Scale must be either None or Scale, not {scale!r} of type {t}'.format(scale=scale, t=type(scale)))
        self.scale = scale
        self.parameters = {'Acceleration_voltage': acceleration_voltage,
                           'Mode': mode,
                           'Mag_mode': mag_mode,
                           'Alpha': alpha,
                           'Spot': spot,
                           'Spot_size': spot_size,
                           'Camera': camera,
                           'Microscope': microscope
                           }

    def __repr__(self):
        return '{self.__class__.__name__}({self.nominal_value!r}, {self.actual_value!r}, {self.units!r}, {self.name!r}, {self.date!r}, {self.scale!r}, {parameters}'.format(
            self=self, parameters=', '.join(
                ['{key}={value}'.format(key=key, value=self.parameters[key]) for key in self.parameters]))

    def as_dataframe(self):
        """
        Return a dataframe with the microscope calibration values and parameters.
        :return: dataframe with nominal and actual values, along with relevant parameters
        :rtype: pandas.DataFrame
        """
        if self.scale is None:
            return pd.DataFrame([[self.nominal_value, self.actual_value, self.date] + list(self.parameters.values())],
                                columns=['Nominal {self.name} ({self.units})'.format(self=self),
                                         '{self.name} ({self.units})'.format(self=self), 'Date'] + list(
                                    self.parameters.keys()))
        elif isinstance(self.scale, DiffractionScale):
            return pd.DataFrame([[self.nominal_value, self.actual_value, float(self.scale), float(self.scale_mrad),
                                  float(self.scale_deg), self.date] + list(self.parameters.values())],
                                columns=['Nominal {self.name} ({self.units})'.format(self=self),
                                         '{self.name} ({self.units})'.format(self=self),
                                         '{self.scale.name} ({self.scale.units})'.format(self=self),
                                         '{self.scale_mrad.name} ({self.scale_mrad.units})'.format(self=self),
                                         '{self.scale_deg.name} ({self.scale_deg.units})'.format(self=self),
                                         'Date'] + list(self.parameters.keys()))
        else:
            return pd.DataFrame([[self.nominal_value, self.actual_value, float(self.scale), self.date] + list(
                self.parameters.values())],
                                columns=['Nominal {self.name} ({self.units})'.format(self=self),
                                         '{self.name} ({self.units})'.format(self=self),
                                         '{self.scale.name} ({self.scale.units})'.format(self=self), 'Date'] + list(
                                    self.parameters.keys()))


class Magnification(MicroscopeCalibration):
    def __init__(self, nominal_mag, actual_mag, date, scale=None, **kwargs):
        """
        Create a magnification calibration.
        :param nominal_mag: The nominal magnification
        :param actual_mag: The actual magnification
        :param date: The date of the calibration acquisition in the format "yyyy-mm-dd"
        :param scale: The scale of the image
        :param kwargs: Optional keyword arguments passed to MicroscopeCalibration defining microscope parameters such as high tension.
        :type nominal_mag: Union[int, float]
        :type actual_mag: Union[int, float]
        :type date: str
        :type scale: Union[int, float, Scale]
        """
        if scale is None:
            scale = ImageScale(nan)
        else:
            scale = ImageScale(scale)
        super().__init__(nominal_mag, actual_mag, '', 'Magnification', date, scale=scale, **kwargs)

    def __str__(self):
        return '{self.name} {self:.0f}'.format(self=self)


class Cameralength(MicroscopeCalibration):
    def __init__(self, nominal_cameralength, actual_cameralength, date, units='cm', scale=None, **kwargs):
        """
        Create a cameralength calibraton
        :param nominal_cameralength: The nominal cameralength
        :param actual_cameralength: The actual cameralength
        :param date: The date of the calibration acquisition in the format "yyyy-mm-dd"
        :param units: The units of the cameralength. Default is "cm"
        :param scale: The scale of the cameralength. Default is None
        :param kwargs: Optional keyword arguments passed to MicroscopeCalibration defining microscope parameters such as high tension.
        :type nominal_cameralength: Union[int, float]
        :type actual_cameralength: float
        :type date: str
        :type units: str
        :type scale: Union[int, float, Scale]
        """
        if scale is None:
            scale = DiffractionScale(nan)
        elif isinstance(scale, (int, float)):
            scale = DiffractionScale(scale)
        elif isinstance(scale, Scale):
            scale = DiffractionScale(scale)
        super().__init__(nominal_cameralength, actual_cameralength, units, 'Cameralength', date, scale=scale, **kwargs)
        self.scale = DiffractionScale(self.scale)
        self.scale_deg = self.scale.to_deg(self.parameters['Acceleration_voltage'])
        self.scale_rad = self.scale.to_rad(self.parameters['Acceleration_voltage'])
        self.scale_mrad = self.scale.to_mrad(self.parameters['Acceleration_voltage'])

    def __str__(self):
        return '{self.name} {self:.3g} {self.units}'.format(self=self)


class StepSize(MicroscopeCalibration):
    def __init__(self, nominal_stepsize, actual_stepsize, date, direction=None, units='nm', **kwargs):
        """
        Create a stepsize calibration.
        :param nominal_stepsize: The nominal stepsize
        :param actual_stepsize: The actual stepsize
        :param date: The date of the calibration acquisition in the format "yyyy-mm-dd"
        :param direction: The direction of the stepsize. Default is None
        :param units: The units of the stepsize. Default is "nm"
        :param kwargs: Optional keyword arguments passed to MicroscopeCalibration defining microscope properties. Required properties are "Mode" and "Alpha".
        :type nominal_stepsize: float
        :type actual_stepsize: float
        :type date: str
        :type direction: str
        :type units: str
        """
        if direction is None:
            direction = ''
        else:
            direction = ' ' + direction
        if 'Mode' not in kwargs:
            raise ValueError('Mode must be specified for a step size calibration')
        if 'Alpha' not in kwargs:
            raise ValueError('Alpha must be specified for a step size calibration')
        super().__init__(nominal_stepsize, actual_stepsize, units, 'Step{direction}'.format(direction=direction), date,
                         **kwargs)

    def __str__(self):
        return '{self.name} {self:.3g} {self.units}'.format(self=self)


class PrecessionAngle(MicroscopeCalibration):
    def __init__(self, nominal_precession_angle, actual_precession_angle, date, units='deg', amplitude_x=nan,
                 amplitude_y=nan, **kwargs):
        """
        Create a precession angle calibration
        :param nominal_precession_angle: The nominal precession angle in degrees
        :param actual_precession_angle: The actual precession angle in degrees
        :param date: The date of the calibration acquisition in the format "yyyy-mm-dd".
        :param units: The units of the precession angle. Default is "deg"
        :param amplitude_x: The deflector amplitude in x as %. Default is nan
        :param amplitude_y: The deflector amplitude in y as %. Default is nan
        :param kwargs: Optional keyword arguments passed to MicroscopeCalibration defining microscope properties. Required properties are "Mode" and "Alpha".
        :type nominal_precession_angle: float
        :type actual_precession_angle: float
        :type date: str
        :type units: str
        :type amplitude_y: float
        :type amplitude_x: float
        """
        if 'Mode' not in kwargs:
            raise ValueError('Mode must be specified for a step size calibration')
        if 'Alpha' not in kwargs:
            raise ValueError('Alpha must be specified for a step size calibration')

        super().__init__(nominal_precession_angle, actual_precession_angle, units, 'Precession Angle', date, **kwargs)
        self.amplitudes = (amplitude_x, amplitude_y)

    @property
    def amp_x(self):
        return self.amplitudes[0]

    @property
    def amp_y(self):
        return self.amplitudes[1]

    def __str__(self):
        return '{self.name} {self:.2f} {self.units} ({self.amp_x:.2f}%, {self.amp_y:.2f}%)'.format(self=self)


class Scale(object):
    def __init__(self, scale, units, name='Scale'):
        """
        Create a scale object
        :param scale: The scale
        :param units: The units of the scale
        :param name: The name of the scale. Default is "Scale"
        :type scale: float
        :type units: str
        :type name: str
        """
        self.scale = float(scale)
        self.units = str(units)
        self.name = str(name)

    def __repr__(self):
        return '{self.__class__.__name__}({self.scale!r}, {self.units!r}, {self.name!r})'.format(self=self)

    def __format__(self, format_spec):
        return '{self.scale:{f}}'.format(self=self, f=format_spec)

    def __str__(self):
        return '{self.__class__.__name__} {self.name}={self:.3g} {self.units}'.format(self=self)

    def __float__(self):
        return float(self.scale)

    def __add__(self, other):
        return float(self) + other

    def __radd__(self, other):
        return other + float(self)

    def __iadd__(self, other):
        self.scale += other
        return self

    def __sub__(self, other):
        return float(self) - other

    def __rsub__(self, other):
        return other - float(self)

    def __isub__(self, other):
        self.scale -= other
        return self

    def __mul__(self, other):
        return float(self) * other

    def __rmul__(self, other):
        return other * float(self)

    def __imul__(self, other):
        self.scale *= other
        return self

    def __truediv__(self, other):
        return float(self) / other

    def __rtruediv__(self, other):
        return other / float(self)

    def __itruediv__(self, other):
        self.scale /= other
        return self

    def __pow__(self, power, modulo=None):
        return float(self).__pow__(power, modulo)

    def __eq__(self, other):
        return float(self) == other

    def __ne__(self, other):
        return float(self) != other

    def __gt__(self, other):
        return float(self) > other

    def __ge__(self, other):
        return float(self) >= other

    def __lt__(self, other):
        return float(self) < other

    def __le__(self, other):
        return float(self) <= other

    def __neg__(self):
        return Scale(-float(self), self.units, self.name)


class ImageScale(Scale):
    def __init__(self, scale):
        """
        Create an image scale
        :param scale: The scale of the image
        :type scale: Union[int, float, Scale]
        """
        if isinstance(scale, Scale):
            units = scale.units
            scale = scale.scale
        else:
            units = 'nm/px'
        super().__init__(scale, units)


class DiffractionScale(Scale):
    def __init__(self, scale):
        """
        Create a diffraction scale
        :param scale: The scale of the diffraction pattern
        :type scale: Union[int, float, Scale]
        """
        if isinstance(scale, Scale):
            units = scale.units
            scale = scale.scale
        else:
            units = '1/Å'
        super().__init__(scale, units)

    def to_rad(self, acceleration_voltage, inplace=False):
        if acceleration_voltage is None:
            acceleration_voltage = nan
        acceleration_voltage = float(acceleration_voltage)
        if self.units == '1/Å':
            new_scale = self.scale * wavelength(acceleration_voltage)
        elif self.units == '1/nm':
            new_scale = 10 * self.scale * wavelength(acceleration_voltage)
        elif self.units == 'Å':
            new_scale = 1 / self.scale * wavelength(acceleration_voltage)
        elif self.units == 'nm':
            new_scale = 10 * 1 / self.scale * wavelength(acceleration_voltage)
        elif self.units == 'deg':
            new_scale = self.scale * pi / 180
        elif self.units == 'mrad':
            new_scale = self.scale / 1000
        elif self.units == 'rad':
            if inplace:
                return self
            else:
                new_scale = DiffractionScale(self.scale)
                new_scale.units = 'rad'
                return new_scale
        else:
            raise ValueError('Units of {self} cannot be converted to rad')

        if inplace:
            self.scale = new_scale
            self.units = 'rad'
            return self
        else:
            new_scale = DiffractionScale(new_scale)
            new_scale.units = 'rad'
            return new_scale

    def to_mrad(self, acceleration_voltage, inplace=False):
        new_scale = self.to_rad(acceleration_voltage)
        new_scale *= 1000
        new_scale.units = 'mrad'
        if inplace:
            self.scale = new_scale.scale
            self.units = new_scale.units
            return self
        else:
            return new_scale

    def to_deg(self, acceleration_voltage, inplace=False):
        new_scale = self.to_rad(acceleration_voltage)
        new_scale *= 180 / pi
        new_scale.units = 'deg'
        if inplace:
            self.scale = new_scale.scale
            self.units = new_scale.units
            return self
        else:
            return new_scale

    def to_inv_angstroms(self, acceleration_voltage, inplace=False):
        new_scale = self.to_rad(acceleration_voltage)
        new_scale /= wavelength(acceleration_voltage)
        new_scale.units = '1/Å'
        if inplace:
            self.scale = new_scale.scale
            self.units = new_scale.units
            return self
        else:
            return new_scale

    def to_inv_nm(self, acceleration_voltage, inplace=False):
        new_scale = self.to_inv_angstroms(acceleration_voltage)
        new_scale /= 10
        new_scale.units = '1/nm'
        if inplace:
            self.scale = new_scale.scale
            self.units = new_scale.units
            return self
        else:
            return new_scale

    def to_nm(self, acceleration_voltage, inplace=False):
        new_scale = self.to_inv_nm(acceleration_voltage)
        new_scale.scale = 1 / new_scale.scale
        new_scale.units = 'nm'
        if inplace:
            self.scale = new_scale.scale
            self.units = new_scale.units
            return self
        else:
            return new_scale

    def to_angstroms(self, acceleration_voltage, inplace=False):
        new_scale = self.to_inv_angstroms(acceleration_voltage)
        new_scale.scale = 1 / new_scale.scale
        new_scale.units = 'Å'
        if inplace:
            self.scale = new_scale.scale
            self.units = new_scale.units
            return self
        else:
            return new_scale

    def calculate_cameralength(self, acceleration_voltage, pixel_size):
        return pixel_size / tan(float(self.to_rad(acceleration_voltage)))


class CalibrationList(object):
    def __init__(self, *args):
        self.calibrations = []
        for arg in args:
            if isinstance(arg, Calibration):
                self.calibrations.append(arg)

    @property
    def dataframe(self):
        df = pd.DataFrame()
        for calibration in self:
            df = calibration.add_to_dataframe(df, remove_duplicates=False)
        return df

    def __add__(self, other):
        if not isinstance(other, Calibration):
            raise TypeError('Only calibration objects can be added to a calibration list')
        return self.calibrations + [other]

    def __iadd__(self, other):
        if not isinstance(other, Calibration):
            raise TypeError('Only calibration objects can be added to a calibration list')
        self.calibrations += [other]
        return self

    def __sub__(self, other):
        if not isinstance(other, Calibration):
            raise TypeError('Only calibration objects can be added to a calibration list')
        l = self.calibrations.copy()
        [l.remove(other) for i in range(l.count(other))]
        return l

    def __isub__(self, other):
        if not isinstance(other, Calibration):
            raise TypeError('Only calibration objects can be added to a calibration list')
        [self.calibrations.remove(other) for i in range(self.calibrations.count(other))]
        return self

    def __repr__(self):
        return '{self.__class__.__name__}({s})'.format(self=self, s=', '.join(['{calibration!r}'.format(calibration=calibration) for calibration in self.calibrations]))

    def __iter__(self):
        for calibration in self.calibrations:
            yield calibration

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.calibrations[item]
        elif isinstance(item, str):
            return self.dataframe.query(item)
            #try:

            #return self.dataframe[item]
        else:
            return NotImplemented

    def __setitem__(self, key, value):
        if isinstance(key, int):
            if isinstance(value, Calibration):
                self.calibrations[key] = value
            else:
                raise TypeError()
        else:
            raise TypeError()

def wavelength(V, m0=9.1093837015 * 1e-31, e=1.60217662 * 1e-19, h=6.62607004 * 1e-34, c=299792458):
    """
    Return the wavelength of an accelerated electron in [Å]

    :param c: Speed of light in vacuum [m/s]
    :param h: Planck' constant [m^2 kg/s]
    :param e: Elementary charge of electorn [C]
    :param m0: Rest mass of electron [kg]
    :param V: Acceleration voltage [V]
    :type V: float
    :type m0: float
    :type e: float
    :type h: float
    :type c: float
    :returns: wavelength of electron in Å
    :rtype: float
    """

    return h / sqrt(2 * m0 * e * V * (1.0 + (e * V / (2 * m0 * c ** 2)))) * 1E10
