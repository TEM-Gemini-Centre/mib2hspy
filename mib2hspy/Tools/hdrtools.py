from pathlib import Path

class MedipixHDRfield(object):
    def __init__(self, name, value):
        super(MedipixHDRfield, self).__init__()
        self.name = name
        self.value = value

    def __str__(self):
        return ('{self.name}: {self.value}')

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def __add__(self, other):
        return self.value + other

    def __radd__(self, other):
        return other + self.value

    def __sub__(self, other):
        return self.value - other

    def __rsub__(self, other):
        return other - self.value

    def __mul__(self, other):
        return self.value * other

    def __rmul__(self, other):
        return other * self.value

    def __truediv__(self, other):
        return self.value / other

    def __rtruediv__(self, other):
        return other / self.value

    def __pow__(self, power, modulo=None):
        return self.value.__pow__(power, modulo=modulo)

    def as_dict(self):
        return {self.name.lower.replace(' ', ''): self.value}


class MedipixHDRcontent(object):
    def __init__(self, filename):
        """Create a MedipixHDRcontent object"""
        super(MedipixHDRcontent, self).__init__()
        self.filename = Path(filename)
        self.timestamp = MedipixHDRfield('Time and Date Stamp (day, mnth, yr, hr, min, s)', '')
        self.chipID = MedipixHDRfield('Chip ID', '')
        self.chip_type = MedipixHDRfield('Chip Type (Medipix 3.0, Medipix 3.1, Medipix 3RX)', '')
        self.assembly_size = MedipixHDRfield('Assembly Size (NX1, 2X2)', '')
        self.chip_mode = MedipixHDRfield('Chip Mode  (SPM, CSM, CM, CSCM)', '')
        self.counter_depth = MedipixHDRfield('Counter Depth (number)', '')
        self.gain = MedipixHDRfield('Gain', '')
        self.active_counters = MedipixHDRfield('Active Counters', '')
        self.thresholds = MedipixHDRfield('Thresholds (keV)', '')
        self.dacs = MedipixHDRfield('DACs', '')
        self.bpc_file = MedipixHDRfield('bpc File', '')
        self.dac_file = MedipixHDRfield('DAC File', '')
        self.gap_fill_mode = MedipixHDRfield('Gap Fill Mode', '')
        self.flat_field_file = MedipixHDRfield('Flat Field File', '')
        self.dead_time_file = MedipixHDRfield('Dead Time File', '')
        self.acquisition_type = MedipixHDRfield('Acquisition Type (Normal, Th_scan, Config)', '')
        self.frames_in_acquisition = MedipixHDRfield('Frames in Acquisition (Number)', '')
        self.frames_per_trigger = MedipixHDRfield('Frames per Trigger (Number)', '')
        self.trigger_start = MedipixHDRfield('Trigger Start (Positive, Negative, Internal)', '')
        self.trigger_stop = MedipixHDRfield('Trigger Stop (Positive, Negative, Internal)', '')
        self.sensor_bias = MedipixHDRfield('Sensor Bias (V)', '')
        self.sensor_polarity = MedipixHDRfield('Sensor Polarity (Positive, Negative)', '')
        self.temperature = MedipixHDRfield('Temperature (C)', '')
        self.humidity = MedipixHDRfield('Humidity (%)', '')
        self.medipix_clock = MedipixHDRfield('Medipix Clock (MHz)', '')
        self.readout_system = MedipixHDRfield('Readout System', '')
        self.software_version = MedipixHDRfield('Software Version', '')

    def __repr__(self):
        return '{self.__class__.__name__}({self.directory!r})'.format(self=self)

    def __str__(self):
        content = '\n\t'.join(['{field.name}: {field.value}'.format(field=field) for field in self])
        return 'Content of Medipix HDR file "{self.directory}":\n\t{content}'.format(self=self, content=content)

    def set_filename(self, filename):
        if not isinstance(filename, (str, Path)):
            raise TypeError()
        filename = Path(filename)
        if filename.suffix == '.hdr':
            self.filename = filename
        else:
            raise ValueError('Filename "{filename}" is not a HDR file'.format(filename=filename))

    def __iter__(self):
        fields = [
            self.timestamp,
            self.chipID,
            self.chip_type,
            self.assembly_size,
            self.chip_mode,
            self.counter_depth,
            self.gain,
            self.active_counters,
            self.thresholds,
            self.dacs,
            self.bpc_file,
            self.dac_file,
            self.gap_fill_mode,
            self.flat_field_file,
            self.dead_time_file,
            self.acquisition_type,
            self.frames_in_acquisition,
            self.frames_per_trigger,
            self.trigger_start,
            self.trigger_stop,
            self.sensor_bias,
            self.sensor_polarity,
            self.temperature,
            self.humidity,
            self.medipix_clock,
            self.readout_system,
            self.software_version,
        ]
        for field in fields:
            yield field

    def __getitem__(self, item):
        if not isinstance(item, str):
            raise TypeError()
        for field in self:
            if field.name == item:
                return field
        raise IndexError('Item "{item}" does not exist in {self}'.format(item=item, self=self))

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TypeError()
        if not isinstance(value, str):
            raise TypeError()
        field = self[key]
        field.value = value

    def load_hdr(self, filename=None):
        """load the header file"""
        if filename is not None:
            self.set_filename(filename)
        if self.filename.exists() and self.filename.suffix == '.hdr':
            with self.filename.open('r') as hdrfile:
                lines = hdrfile.readlines()
                for lineno, line in enumerate(lines):
                    if 0 < lineno < len(lines)-1:
                        field, value = line.split(':', maxsplit=1)
                        field = field.strip()
                        value = value.strip()
                        try:
                            self[field] = value
                        except IndexError as e:
                            raise e
        else:
            msg = 'HDR file "{self.directory}" does not exist. Please set correct HDR directory before loading content'.format(
                self=self)
            raise FileNotFoundError(msg)

    def as_dict(self):
        """Return the header object as a dictionary"""
        dictionary = {}
        for field in self:
            dictionary.update(field.as_dict())
        return dictionary

    def clear(self):
        """Clears the header object of content"""
        for field in self:
            field.value = ''
        self.filename = Path('.')