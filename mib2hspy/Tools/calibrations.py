import pandas as pd
import datetime as dt
import re
from math import nan, sqrt, pi, atan, tan, isnan


class Calibration(object):
    def __init__(self, nominal_value, actual_value, units, name, date, label=None):
        """
        Create a calibration object
        :param nominal_value: The nominal value
        :param actual_value: The actual value
        :param units: The units of the values
        :param name: The name of the calibration/measure
        :param date: The date of the calibration in the format "yyyy-mm-dd"
        :param label: A label to use for the calibration. Default is None
        :type nominal_value: Union[int, float]
        :type actual_value: Union[int, float]
        :type units: str
        :type name: str
        :type date: Union[str. datetime.date, datetime.datetime]
        """
        if nominal_value is None:
            nominal_value = nan
        if actual_value is None:
            actual_value = nan
        self.nominal_value = float(nominal_value)
        self.actual_value = float(actual_value)
        self.units = str(units)
        self.name = str(name)
        if isinstance(date, (dt.date, dt.datetime)):
            date = date.strftime('%Y-%m-%d')
        self.date = dt.datetime.strptime(date, '%Y-%m-%d').date()
        self.label = label

    def __repr__(self):
        return '{self.__class__.__name__}({self.nominal_value!r}, {self.actual_value!r}, {self.units!r}, {self.name!r}, {self.date!r}, label={self.label!r})'.format(
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
        if self.label is not None:
            return pd.DataFrame([[self.label, self.nominal_value, self.actual_value, self.date]],
                                columns=['Label', 'Nominal {self.name} ({self.units})'.format(self=self),
                                         '{self.name} ({self.units})'.format(self=self), 'Date'])
        else:
            return pd.DataFrame([[self.nominal_value, self.actual_value, self.date]],
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
                 spot_size=None, camera=None, microscope=None, **kwargs):
        """
        Create a microscope calibration.
        :param args: Positional arguments passed to Calibration().
        :param scale: The scale of the calibrated image.
        :param acceleration_voltage: The acceleration voltage of the microscope in V. Default is None.
        :param mode: The mode of the microscope. Default is None.
        :param mag_mode: The magnification mode of the microscope. Default is None.
        :param alpha: The alpha-setting of the microscope. Default is None.
        :param spot: The spot-setting of the microscope. Default is None.
        :param spot_size: The nominal spot-size of the microscope in nm. Default is None.
        :param camera: The name of the camera to calibrate. Default is None.
        :param microscope: The name of the microscope. Default is None.
        :param kwargs: Optional keyword arguments passed to Calibration()
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
        super().__init__(*args, **kwargs)
        if scale is not None:
            if not isinstance(scale, Scale):
                raise TypeError(
                    'Scale must be either None or Scale, not {scale!r} of type {t}'.format(scale=scale, t=type(scale)))
        self.scale = scale
        self.parameters = {'Acceleration Voltage (V)': acceleration_voltage,
                           'Mode': mode,
                           'Mag mode': mag_mode,
                           'Alpha': alpha,
                           'Spot': spot,
                           'Nominal Spotsize (nm)': spot_size,
                           'Camera': camera,
                           'Microscope': microscope
                           }

    def __repr__(self):
        return '{self.__class__.__name__}({self.nominal_value!r}, {self.actual_value!r}, {self.units!r}, {self.name!r}, {self.date!r}, {self.scale!r}, {parameters}'.format(
            self=self, parameters=', '.join(
                ['{key}={value}'.format(key=key, value=self.parameters[key]) for key in self.parameters]))

    def as_dataframe(self, ignore_nans=True):
        """
        Return a dataframe with the microscope calibration values and parameters.
        :param ignore_nans: Whether to ignore parameters with nan values or not. Default is True
        :type ignore_nans: bool
        :return: dataframe with nominal and actual values, along with relevant parameters
        :rtype: pandas.DataFrame
        """
        df = super().as_dataframe()
        df['{self.scale.name} ({self.scale.units})'.format(self=self)] = self.scale.scale
        for key in self.parameters:
            value = self.parameters[key]
            if value is None:
                pass
            elif isinstance(value, str):
                df[key] = value
            else:
                if ignore_nans:
                    if not isnan(value):
                        df[key] = value
                else:
                    df[key] = value
        return df


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
        super().__init__(nominal_mag, actual_mag, '', 'Magnification', date, scale=scale, label='IMG', **kwargs)

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
        super().__init__(nominal_cameralength, actual_cameralength, units, 'Cameralength', date, scale=scale,
                         label='DIFF', **kwargs)
        self.scale = DiffractionScale(self.scale)
        self.scale_deg = self.scale.to_deg(self.parameters['Acceleration Voltage (V)'])
        self.scale_rad = self.scale.to_rad(self.parameters['Acceleration Voltage (V)'])
        self.scale_mrad = self.scale.to_mrad(self.parameters['Acceleration Voltage (V)'])

    def __str__(self):
        return '{self.name} {self:.3g} {self.units}'.format(self=self)

    def as_dataframe(self):
        df = super().as_dataframe()
        df['{self.scale_mrad.name} ({self.scale_mrad.units})'.format(self=self)] = [float(self.scale_mrad)]
        df['{self.scale_deg.name} ({self.scale_deg.units})'.format(self=self)] = [float(self.scale_deg)]
        return df

    def calibrate_cameralength(self):
        """
        Calibrate the cameralength based on the parameters of the calibration.
        :return:
        """
        acceleration_voltage = float(self.parameters['Acceleration_voltage'])
        camera = str(self.parameters['Camera'])
        if camera is not None:
            if 'Merlin' in camera:
                pixel_size = 55  # um
            elif 'US1000' in camera:
                pixel_size = 14  # um
            else:
                raise ValueError(
                    'No camera recognized for {self}, cannot determine pixel size for cameralength calculations.'.format(
                        self=self))
        else:
            raise ValueError(
                'No camera set for {self}, cannot determine pixel size for cameralength calculations.'.format(
                    self=self))

        if acceleration_voltage is not None:
            if not isnan(acceleration_voltage):
                cameralength = self.scale.calculate_cameralength(acceleration_voltage,
                                                                 pixel_size) * 1E-4  # convert to cm
            else:
                raise ValueError(
                    'Acceleration voltage for {self} is nan, cannot caluclate cameralength.'.format(self=self))
        else:
            raise ValueError('No Acceleration voltage set for {self}, cannot calculate cameralength.'.format(self=self))
        self.actual_value = cameralength
        self.units = 'cm'

    def calibrate_scale(self):
        """
        Calculates the correct scale for the calibration given values set by the parameters in the object
        :return:
        """
        acceleration_voltage = float(self.parameters['Acceleration_voltage'])
        camera = str(self.parameters['Camera'])
        if 'Merlin' in camera:
            pixel_size = 55
        elif 'US1000' in camera:
            pixel_size = 14
        else:
            raise ValueError('Could not recognize camera for {self}, cannot calibrate scale'.format(self=self))
        if not isnan(acceleration_voltage):
            scale = (pixel_size * 1E-6) / (self.actual_value * 1E-2) / (wavelength(acceleration_voltage))
        else:
            raise ValueError('Could not calculate scale for {self}, acceleration voltage is NaN.'.format(self=self))
        self.scale.scale = scale
        self.scale.units = '1/Å'
        self.scale_deg = self.scale.to_deg(acceleration_voltage)
        self.scale_rad = self.scale.to_rad(acceleration_voltage)
        self.scale_mrad = self.scale.to_mrad(acceleration_voltage)


class StepSize(MicroscopeCalibration):
    def __init__(self, nominal_stepsize, actual_stepsize, date, amplitude=nan, direction=None, units='nm', **kwargs):
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
        if 'mode' not in kwargs:
            raise ValueError('`mode` must be specified for a step size calibration')
        if 'alpha' not in kwargs:
            raise ValueError('`alpha` must be specified for a step size calibration')
        super().__init__(nominal_stepsize, actual_stepsize, units, 'Step{direction}'.format(direction=direction), date,
                         label='STEP', **kwargs)
        self.direction = direction
        if amplitude is None:
            amplitude = nan
        self.amplitude = float(amplitude)

    def __repr__(self):
        return '{self.__class__.__name__}(self.nominal_stepsize!r}, {self.actual_stepsize!r}, {self.date!r}, ' \
               'amplitude={self.amplitude!r}, direction={self.direction!r}, units={self.units!r}, ' \
               '{parameters}'.format(self=self, parameters=', '.join(['{key}={value}'.format(key=key,
                                                                                             value=self.parameters[
                                                                                                 key]) for key in
                                                                      self.parameters]))

    def __str__(self):
        return '{self.name} {self:.3g} {self.units}'.format(self=self)


class PrecessionAngle(MicroscopeCalibration):
    default_deflectors = {'Upper_1': {'X': {'A': nan, 'P': nan}, 'Y': {'A': nan, 'P': nan}},
                          'Upper_2': {'X': {'A': nan, 'P': nan}, 'Y': {'A': nan, 'P': nan}},
                          'Lower_1': {'X': {'A': nan, 'P': nan}, 'Y': {'A': nan, 'P': nan}},
                          'Lower_2': {'X': {'A': nan, 'P': nan}, 'Y': {'A': nan, 'P': nan}}}

    def __init__(self, nominal_precession_angle, actual_precession_angle, precession_excitation, date, units='deg',
                 deflectors={}, **kwargs):
        """
        Create a precession angle calibration
        :param nominal_precession_angle: The nominal precession angle in degrees
        :param actual_precession_angle: The actual precession angle in degrees
        :param date: The date of the calibration acquisition in the format "yyyy-mm-dd".
        :param units: The units of the precession angle. Default is "deg"
        :param precession_excitation: The excitation of the precession system in %.
        :param deflectors: The deflector amplitudes and phases. Default is {'Upper_1':{'X':{'A':nan,'P':nan},'Y':{'A':nan,'P':nan}}, 'Upper_2':{'X':{'A':nan,'P':nan},'Y':{'A':nan,'P':nan}}, 'Lower_1':{'X':{'A':nan,'P':nan},'Y':{'A':nan,'P':nan}}, 'Lower_2':{'X':{'A':nan,'P':nan},'Y':{'A':nan,'P':nan}}
        :param kwargs: Optional keyword arguments passed to MicroscopeCalibration defining microscope properties. Required properties are "Mode" and "Alpha".
        :type nominal_precession_angle: float
        :type actual_precession_angle: float
        :type date: str
        :type units: str
        :type precession_excitation: float
        :type deflectors: Union[dict, list]
        """
        if 'mode' not in kwargs:
            raise ValueError('`mode` must be specified for a precession angle calibration')
        if 'alpha' not in kwargs:
            raise ValueError('`alpha` must be specified for a precession angle calibration')

        super().__init__(nominal_precession_angle, actual_precession_angle, units, 'Precession Angle', date,
                         label='PREC', **kwargs)
        self.precession_excitation = precession_excitation

        if isinstance(deflectors, dict):
            self.deflectors = [Deflector(deflectors.get('Upper_1', {}).get('X', {}).get('A', nan), 'Upper 1 X',
                                         phase=deflectors.get('Upper_1', {}).get('X', {}).get('P', nan)),
                               Deflector(deflectors.get('Upper_1', {}).get('Y', {}).get('A', nan), 'Upper 1 Y',
                                         phase=deflectors.get('Upper_1', {}).get('Y', {}).get('P', nan)),
                               Deflector(deflectors.get('Upper_2', {}).get('X', {}).get('A', nan), 'Upper 2 X',
                                         phase=deflectors.get('Upper_2', {}).get('X', {}).get('P', nan)),
                               Deflector(deflectors.get('Upper_2', {}).get('Y', {}).get('A', nan), 'Upper 2 Y',
                                         phase=deflectors.get('Upper_2', {}).get('Y', {}).get('P', nan)),
                               Deflector(deflectors.get('Lower_1', {}).get('X', {}).get('A', nan), 'Lower 1 X',
                                         phase=deflectors.get('Lower_1', {}).get('X', {}).get('P', nan)),
                               Deflector(deflectors.get('Lower_1', {}).get('Y', {}).get('A', nan), 'Lower 1 Y',
                                         phase=deflectors.get('Lower_1', {}).get('Y', {}).get('P', nan)),
                               Deflector(deflectors.get('Lower_2', {}).get('X', {}).get('A', nan), 'Lower 2 X',
                                         phase=deflectors.get('Lower_2', {}).get('X', {}).get('P', nan)),
                               Deflector(deflectors.get('Lower_2', {}).get('Y', {}).get('A', nan), 'Lower 2 Y',
                                         phase=deflectors.get('Lower_2', {}).get('Y', {}).get('P', nan))
                               ]
        elif isinstance(deflectors, list):
            if not all([isinstance(deflector, Deflector) for deflector in deflectors]):
                raise TypeError('Objects in {deflectors} must be of type Deflector'.format(deflectors=deflectors))
            self.deflectors = deflectors
        else:
            raise TypeError(
                'Deflectors must be given as a dictionary or as a list. Not {deflectors} of type {t}'.format(
                    deflectors=deflectors, t=type(deflectors)))

    def __repr__(self):
        return '{self.__class__.__name__}({self.nominal_value_angle!r}, {self.actual_value_angle!r}, {self.precession_excitation!r}, {self.date!r}, {self.units!r}, {self.deflectors!r}, {parameters}'.format(
            self=self, parameters=', '.join(
                ['{key}={value!r}'.format(key=key, value=self.parameters[key]) for key in self.parameters]))

    def __str__(self):
        return '{self.name} {self:.2f} {self.units}\n\t{deflectors}'.format(self=self, deflectors='\n\t'.join(
            [str(deflector) for deflector in self.deflectors]))

    def as_dataframe(self, ignore_nans=True):
        """
        Return alignment as a dataframe
        :return:
        """
        df = super().as_dataframe()
        df['Precession excitation (%)'] = self.precession_excitation
        for deflector in self.deflectors:
            if ignore_nans:
                if deflector.no_nans():
                    deflector.add_to_dataframe(df)
            else:
                deflector.add_to_dataframe(df)
        return df


class Spotsize(MicroscopeCalibration):
    def __init__(self, actual_spotsize, date, units='nm', **kwargs):
        """
        Create a spotsize calibraton
        :param actual_spotsize: The actual spotsize
        :param date: The date of the calibration acquisition in the format "yyyy-mm-dd"
        :param units: The units of the cameralength. Default is "nm"
        :param kwargs: Optional keyword arguments passed to MicroscopeCalibration defining microscope parameters such as high tension.
        :type actual_spotsize: float
        :type date: str
        :type units: str
        :type scale: Union[int, float, Scale]
        """
        super().__init__(kwargs.get('spot_size', None), actual_spotsize, units, 'Spotsize', date, label='SPOT', **kwargs)

    def __str__(self):
        return '{self.name} {self:.3g} {self.units}'.format(self=self)


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
        return '{self.__class__.__name__}({s})'.format(self=self, s=', '.join(
            ['{calibration!r}'.format(calibration=calibration) for calibration in self.calibrations]))

    def __iter__(self):
        for calibration in self.calibrations:
            yield calibration

    def __getitem__(self, item):
        if isinstance(item, (int, slice)):
            return self.calibrations[item]
        elif isinstance(item, str):
            df = self.dataframe
            if item in df.columns:
                return df[item]
            else:
                return df.query(item)
        else:
            raise TypeError(
                'Cannot use {item} for getting items in {self}. Only types int, slice, and str are supported, not {t}'.format(
                    item=item, self=self, t=type(item)))

    def __setitem__(self, key, value):
        if isinstance(key, (int, slice)):
            if isinstance(value, Calibration):
                self.calibrations[key] = value
            else:
                raise TypeError(
                    'Cannot add object {value} to {self}. Only Calibration objects may be added.'.format(value=value,
                                                                                                         self=self))
        else:
            raise TypeError(
                'Cannot set item {value} at {key} in {self}, keys must either be int or slice obejcts'.format(
                    value=value, key=key, self=self))


class Deflector(object):
    def __init__(self, amplitude, name, phase=nan):
        if amplitude is None:
            amplitude = nan
        if phase is None:
            phase = nan
        self.amplitude = float(amplitude)
        self.phase = float(phase)
        self.name = name

    def __repr__(self):
        return '{self.__class__.__name__}({self.amplitude!r}, {self.name!r}, phase={self.phase!r})'.format(self=self)

    def __format__(self, format_spec):
        return 'Amplitude: {self.amplitude:{f}} %, Phase: {self.phase:{f}} deg'.format(self=self, f=format_spec)

    def __str__(self):
        return '{self.__class__.__name__} {self.name}: {self:.2g}'.format(self=self)

    def no_nans(self):
        return not (isnan(self.amplitude) or isnan(self.phase))

    def get_formatted_name(self):
        return '{self.__class__.__name__} {self.name}'.format(self=self)

    def get_column_values(self):
        return [self.amplitude, self.phase]

    def get_column_names(self):
        return ['{name} Amplitude (%)'.format(name=self.get_formatted_name()),
                '{name} Phase (deg)'.format(name=self.get_formatted_name())]

    def as_dataframe(self):
        return pd.DataFrame([self.get_column_values()],
                            columns=self.get_column_names())

    def add_to_dataframe(self, dataframe):
        for name, value in zip(self.get_column_names(), self.get_column_values()):
            try:
                dataframe[name] = [value]
            except Exception as e:
                print(name, value)
                raise e


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


def generate_from_dataframe(dataframe):
    """
    Create calibration objects from a dataframe.
    :param dataframe: The dataframe containing calibration data.
    :type dataframe: pandas.DataFrame
    :return: The generated calibration data.
    :rtype: CalibrationList
    """

    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError()

    calibrations = CalibrationList()
    for index, row in dataframe.iterrows():
        label = row.get('Label')
        acc_voltage = row.get('Acceleration Voltage (V)')
        mode = row.get('Mode')
        alpha = row.get('Alpha')
        mag_mode = row.get('Mag mode')
        spot = row.get('Spot')
        spot_size = row.get('Spotsize (nm)')
        camera = row.get('Camera')
        microscope = row.get('Microscope')
        date = row.get('Date')
        if label == 'IMG':
            nominal_value = row.get('Nominal Magnification ()')
            actual_value = row.get('Magnification')
            scale = row.get('Scale (nm)')
            calibration = Magnification(nominal_value, actual_value, date, scale=scale,
                                        acceleration_voltage=acc_voltage, mode=mode, alpha=alpha,
                                        mag_mode=mag_mode, spot=spot, spot_size=spot_size, camera=camera,
                                        microscope=microscope)
            calibrations += calibration
        elif label == 'DIFF':
            nominal_value = row.get('Nominal Cameralength (cm)')
            actual_value = row.get('Cameralength (cm)')
            scale = row.get('Scale (1/Å)')
            calibration = Cameralength(nominal_value, actual_value, date, scale=scale, acceleration_voltage=acc_voltage,
                                       mode=mode, alpha=alpha,
                                       mag_mode=mag_mode, spot=spot, spot_size=spot_size, camera=camera,
                                       microscope=microscope)
            calibrations += calibration
        elif label == 'STEP':
            nominal_step = row.get('Nominal Step (nm)')
            nominal_step_x = row.get('Nominal Step X (nm)')
            nominal_step_y = row.get('Nominal Step Y (nm)')

            if nominal_step is not None:
                direction = ''
            elif nominal_step_x is not None:
                direction = 'X'
                nominal_step = nominal_step_x
            elif nominal_step_y is not None:
                direction = 'Y'
                nominal_step = nominal_step_y
            else:
                direction = ''
            step = row.get('Step {direction} (nm)'.format(direction=direction))

            calibration = StepSize(nominal_step, step, date, direction=direction, acceleration_voltage=acc_voltage,
                                   mode=mode, alpha=alpha,
                                   mag_mode=mag_mode, spot=spot, spot_size=spot_size, camera=camera,
                                   microscope=microscope)
            calibrations += calibration
        elif label == 'PREC':
            nominal_value = row.get('Nominal Precession Angle (deg)')
            actual_value = row.get('Precession Angle (deg)')
            excitation = row.get('Precession excitation (%)')
            deflectors = {
                'Upper_1': {
                    'X': {
                        'A': row.get('Deflector Upper 1 X Amplitude (%)'),
                        'P': row.get('Deflector Upper 1 X Phase (deg)'),
                    },
                    'Y': {
                        'A': row.get('Deflector Upper 1 Y Amplitude (%)'),
                        'P': row.get('Deflector Upper 1 Y Phase (deg)'),
                    }
                },
                'Upper_2': {
                    'X': {
                        'A': row.get('Deflector Upper 2 X Amplitude (%)'),
                        'P': row.get('Deflector Upper 2 X Phase (deg)'),
                    },
                    'Y': {
                        'A': row.get('Deflector Upper 2 Y Amplitude (%)'),
                        'P': row.get('Deflector Upper 2 Y Phase (deg)'),
                    }
                },
                'Lower_1': {
                    'X': {
                        'A': row.get('Deflector Lower 1 X Amplitude (%)'),
                        'P': row.get('Deflector Lower 1 X Phase (deg)'),
                    },
                    'Y': {
                        'A': row.get('Deflector Lower 1 Y Amplitude (%)'),
                        'P': row.get('Deflector Lower 1 Y Phase (deg)'),
                    }
                },
                'Lower_2': {
                    'X': {
                        'A': row.get('Deflector Lower 2 X Amplitude (%)'),
                        'P': row.get('Deflector Lower 2 X Phase (deg)'),
                    },
                    'Y': {
                        'A': row.get('Deflector Lower 2 Y Amplitude (%)'),
                        'P': row.get('Deflector Lower 2 Y Phase (deg)'),
                    }
                },

            }
            calibration = PrecessionAngle(nominal_value, actual_value, excitation, date,
                                          acceleration_voltage=acc_voltage, mode=mode, alpha=alpha,
                                          mag_mode=mag_mode, spot=spot, spot_size=spot_size, camera=camera,
                                          microscope=microscope, deflectors=deflectors)
            calibrations += calibration
        elif label == 'SPOT':
            nominal_value = row.get('Nominal Spotsize (nm)')
            actual_value = row.get('Spotsize (nm)')
            calibration = Spotsize(nominal_value, actual_value, date, acceleration_voltage=acc_voltage, mode=mode, alpha=alpha, mag_mode=mag_mode, spot=spot, spot_size=spot_size, camera=camera, microscope=microscope)
            calibrations += calibration
        else:
            print('Did not recognize label {label}. Cannot generate calibration object.'.format(label=label))

    return calibrations

def make_calibration_from_GMS(signal):
    pass

def make_calibration_from_hyperspy(signal):
    pass
