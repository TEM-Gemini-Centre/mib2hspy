from math import nan, isnan


class Parameter(object):
    def __init__(self, parameter_name, value, units):
        super(Parameter, self).__init__()
        if not isinstance(parameter_name, str):
            raise TypeError('Parameter name must be a string!')
        if not isinstance(units, str):
            raise TypeError('Units must be a string!')
        self.name = parameter_name
        self.value = value
        self.units = units

    def set_name(self, newname):
        if not isinstance(newname, str):
            raise TypeError()
        self.name = newname

    def set_units(self, newunits):
        if not isinstance(newunits, str):
            raise TypeError()
        self.units = newunits

    def set_value(self, newvalue):
        if not isinstance(newvalue, (int, float, str)):
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
        """Check whether the value of the parameter is well-defined or not (i.e. not `nan`, `None`, `""`, or `"None"`)

        Returns False if value is None.
        Returns False if value is ""
        Returns ~isnan(value) else.
        """
        if self.value is None:
            return False
        if isinstance(self.value, str):
            if self.value == '' or self.value == 'None':
                return False
        return not isnan(self.value)

    def as_dict(self):
        """Return parameter as a dictionary"""
        return {'{self.name}'.format(self=self): {'Value': self.value, 'Units': self.units}}


class CalibratedParameter(Parameter):
    def __init__(self, parameter_name, value, units, nominal_value):
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
        if not isinstance(newvalue, type(self.value)):
            raise TypeError(
                'Invalid nominal value {nomval!r}. Nominal value must be same type as value {self.value!r}'.format(
                    nomval=newvalue, self=self))
        self.nominal_value = newvalue

    def as_dict(self):
        """Return calibrated parameter as a dictionary"""
        return {'{self.name}'.format(self=self): {'Nominal_value': self.nominal_value, 'Value': self.value,
                                                  'Units': self.units}}
