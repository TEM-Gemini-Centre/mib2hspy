from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from ..Tools import Microscope, Parameter, CalibratedParameter, Detector
from datetime import datetime
from math import nan


class QParameter(QObject, Parameter):
    nameChanged = pyqtSignal([], name='nameChanged')
    unitsChanged = pyqtSignal([], name='unitsChanged')
    valueChanged = pyqtSignal([], name='valueChanged')
    parameterChanged = pyqtSignal([], name='parameterChanged')

    def __init__(self, name, value, units, parent=None):
        if parent is not None:
            QObject.__init__(self, parent)
        else:
            QObject.__init__(self)
        Parameter.__init__(self, name, value, units)

    @pyqtSlot(str, name='setName', result=None)
    def setName(self, newname):
        Parameter.set_name(self, newname)
        self.parameterChanged.emit()
        self.nameChanged.emit()

    @pyqtSlot(str, name='setUnits', result=None)
    def setUnits(self, newunits):
        Parameter.set_units(self, newunits)
        self.parameterChanged.emit()
        self.unitsChanged.emit()

    @pyqtSlot(int, name='setValue', result=None)
    @pyqtSlot(float, name='setValue', result=None)
    @pyqtSlot(str, name='setValue', result=None)
    @pyqtSlot(datetime, name='setValue', result=None)
    def setValue(self, newvalue):
        Parameter.set_value(self, newvalue)
        self.parameterChanged.emit()
        self.valueChanged.emit()


class QCalibratedParameter(QObject, CalibratedParameter):
    nameChanged = pyqtSignal([], name='nameChanged')
    unitsChanged = pyqtSignal([], name='unitsChanged')
    valueChanged = pyqtSignal([], name='valueChanged')
    nominalValueChanged = pyqtSignal([], name='nominalValueChanged')
    parameterChanged = pyqtSignal([], name = 'parameterChanged')

    def __init__(self, name, value, units, nominal_value, parent=None):
        if parent is not None:
            QObject.__init__(self, parent)
        else:
            QObject.__init__(self)
        CalibratedParameter.__init__(self, name, value, units, nominal_value)


    @pyqtSlot(str, name='setName', result=None)
    def setName(self, newname):
        CalibratedParameter.set_name(self, newname)
        self.parameterChanged.emit()
        self.nameChanged.emit()

    @pyqtSlot(str, name='setUnits', result=None)
    def setUnits(self, newunits):
        CalibratedParameter.set_units(self, newunits)
        self.parameterChanged.emit()
        self.unitsChanged.emit()

    @pyqtSlot(int, name='setValue', result=None)
    @pyqtSlot(float, name='setValue', result=None)
    @pyqtSlot(str, name='setValue', result=None)
    @pyqtSlot(datetime, name='setValue', result=None)
    def setValue(self, newvalue):
        CalibratedParameter.set_value(self, newvalue)
        self.parameterChanged.emit()
        self.valueChanged.emit()

    @pyqtSlot(int, name='setNominalValue', result=None)
    @pyqtSlot(float, name='setNominalValue', result=None)
    @pyqtSlot(str, name='setNominalValue', result=None)
    @pyqtSlot(datetime, name='setNominalValue', result=None)
    def setNominalValue(self, newvalue):
        CalibratedParameter.set_nominal_value(self, newvalue)
        self.parameterChanged.emit()
        self.valueChanged.emit()


class QMicroscope(QObject, Microscope):
    accelerationVoltageChanged = pyqtSignal([], name='accelerationVoltageChanged')
    modeChanged = pyqtSignal([], name='modeChanged')
    alphaChanged = pyqtSignal([], name='alphaChanged')
    magModeChanged = pyqtSignal([], name='magModeChanged')
    magnificationChanged = pyqtSignal([], name = 'magnificationChanged')
    cameralengthChanged = pyqtSignal([], name='cameralengthChanged')
    spotChanged = pyqtSignal([], name = 'spotChanged')
    spotsizeChanged = pyqtSignal([], name='spotsizeChanged')
    condenserApertureChanged = pyqtSignal([], name = 'condenserApertureChanged')
    convergenceAngleChanged = pyqtSignal([], name='convergenceAngleChanged')
    rockingAngleChanged = pyqtSignal([], name='rockingAngleChanged')
    rockingFrequencyChanged = pyqtSignal([], name = 'rockingFrequencyChanged')
    scanStepXChanged = pyqtSignal([], name = 'scanStepXChanged')
    scanStepYChanged = pyqtSignal([], name = 'scanStepYChanged')
    acquisitionDateChanged = pyqtSignal([], name='acquisitionDateChanged')

    def __init__(self,
                 acceleration_voltage=QParameter('HT', nan, 'V'),
                 mode=QParameter('Mode', '', ''),
                 alpha=QParameter('Alpha', nan, ''),
                 mag_mode=QParameter('Magnification Mode', '', ''),
                 magnification=QCalibratedParameter('Magnification', nan, '', nan),
                 cameralength=QCalibratedParameter('Camera length', nan, 'cm', nan),
                 spot=QParameter('Spot', nan, ''),
                 spotsize=QCalibratedParameter('Spotsize', nan, 'nm', nan),
                 condenser_aperture=QCalibratedParameter('Condenser aperture', nan, 'um', nan),
                 convergence_angle=QCalibratedParameter('Convergence angle', nan, 'mrad', nan),
                 rocking_angle=QCalibratedParameter('Rocking angle', nan, 'deg', nan),
                 rocking_frequency=QParameter('Rocking frequency', nan, 'Hz'),
                 scan_step_x=QCalibratedParameter('Step X', nan, 'nm', nan),
                 scan_step_y=QCalibratedParameter('Step Y', nan, 'nm', nan),
                 acquisition_date=QParameter('Acquisition Date', '', '')
                 ):
        """
        Creates a microscope object.
        :param acceleration_voltage: The acceleartion voltage of the microscope in kV
        :type acceleration_voltage: QParameter
        :param mode: The mode setting of the microscope (e.g. TEM, STEM, NBD, CBD, etc).
        :type mode: QParameter
        :param alpha: The alpha setting of the microscope (condenser minilens setting)
        :type alpha: QParameter
        :param mag_mode: The magnification mode of the microscope (MAG, SAMAG, LM, etc)
        :type mag_mode: QParameter
        :param magnification: The magnification of the microscope.
        :type magnification: QCalibratedParameter
        :param cameralength: The cameralength of the microscope in cm
        :type cameralength: QCalibratedParameter
        :param spot: The spot setting of the microscope
        :type spot: QParameter
        :param spotsize: The spotsize of the microscope.
        :type spotsize: QCalibratedParameter
        :param condenser_aperture: The condenser aperature of the microscope in microns.
        :type condenser_aperture: QCalibratedParameter
        :param convergence_angle: The convergence angle of the microscope in mrad.
        :type convergence_angle: QCalibratedParameter
        :param rocking_angle: The rocking (precession) angle of the microscope in degrees.
        :type rocking_angle: QCalibratedParameter
        :param rocking_frequency: The rocking (precession) angle of the microscope in Hz.
        :type rocking_frequency: QParameter
        :param scan_step_x: The scan step size in the x-direction in nm
        :type scan_step_x: QCalibratedParameter
        :param scan_step_y: The scan step size in the y-direction in nm
        :type scan_step_y: QCalibratedParameter
        :param acquisition_date: The date of acquisition
        :type acquisition_date: QParameter
        """

        if not isinstance(acceleration_voltage, QParameter):
            raise TypeError()
        if not isinstance(mode, QParameter):
            raise TypeError()
        if not isinstance(mag_mode, QParameter):
            raise TypeError()
        if not isinstance(magnification, QCalibratedParameter):
            raise TypeError()
        if not isinstance(cameralength, QCalibratedParameter):
            raise TypeError()
        if not isinstance(spot, QParameter):
            raise TypeError()
        if not isinstance(spotsize, QCalibratedParameter):
            raise TypeError()
        if not isinstance(condenser_aperture, QCalibratedParameter):
            raise TypeError()
        if not isinstance(convergence_angle, QCalibratedParameter):
            raise TypeError()
        if not isinstance(rocking_angle, QCalibratedParameter):
            raise TypeError()
        if not isinstance(rocking_frequency, QParameter):
            raise TypeError()
        if not isinstance(scan_step_x, QCalibratedParameter):
            raise TypeError()
        if not isinstance(scan_step_y, QCalibratedParameter):
            raise TypeError()
        if not isinstance(acquisition_date, QParameter):
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

        self.acceleration_voltage.parameterChanged.connect(self.accelerationVoltageChanged)
        self.mode.parameterChanged.connect(self.modeChanged)
        self.alpha.parameterChanged.connect(self.alphaChanged)
        self.mag_mode.parameterChanged.connect(self.magModeChanged)
        self.magnification.parameterChanged.connect(self.magnificationChanged)
        self.cameralength.parameterChanged.connect(self.cameralengthChanged)
        self.spot.parameterChanged.connect(self.spotChanged)
        self.spotsize.parameterChanged.connect(self.spotsizeChanged)
        self.condenser_aperture.parameterChanged.connect(self.condenserApertureChanged)
        self.convergence_angle.parameterChanged.connect(self.convergenceAngleChanged)
        self.rocking_angle.parameterChanged.connect(self.rockingAngleChanged)
        self.rocking_frequency.parameterChanged.connect(self.rockingFrequencyChanged)
        self.scan_step_x.parameterChanged.connect(self.scanStepXChanged)
        self.scan_step_y.parameterChanged.connect(self.scanStepYChanged)
        self.acquisition_date.parameterChanged.connect(self.acquisitionDateChanged)

    @pyqtSlot(int)
    @pyqtSlot(float)
    def setAccelerationVoltage(self, newvalue):
        self.acceleration_voltage.setValue(newvalue * 1E3)

    @pyqtSlot(str)
    def setMode(self, newvalue):
        self.mode.setValue(newvalue)

    @pyqtSlot(int)
    @pyqtSlot(float)
    def setAlpha(self, newvalue):
        self.alpha.setValue(newvalue)

    @pyqtSlot(str)
    def setMagMode(self, newvalue):
        self.mag_mode.setValue(newvalue)

    @pyqtSlot(int)
    @pyqtSlot(float)
    def setMagnification(self, newvalue):
        self.magnification.setValue(newvalue)

    @pyqtSlot(int)
    @pyqtSlot(float)
    def setNominalMagnification(self, newvalue):
        self.magnification.setNominalValue(newvalue)

    @pyqtSlot(int, int)
    @pyqtSlot(float, float)
    @pyqtSlot(int, float)
    @pyqtSlot(float, int)
    def setMagnification(self, newvalue, new_nom_value):
        self.magnification.setValue(newvalue, new_nom_value)

    @pyqtSlot(int)
    @pyqtSlot(float)
    def setCameralength(self, newvalue):
        self.cameralength.setValue(newvalue)

    @pyqtSlot(int)
    @pyqtSlot(float)
    def setNominalCameralength(self, newvalue):
        self.cameralength.setNominalValue(newvalue)

    @pyqtSlot(int, int)
    @pyqtSlot(float, float)
    @pyqtSlot(int, float)
    @pyqtSlot(float, int)
    def setCameralength(self, newvalue, new_nom_value):
        self.cameralength.setValue(newvalue, new_nom_value)

    @pyqtSlot(int)
    def setSpot(self, newvalue):
        self.spot.setValue(newvalue)

    @pyqtSlot(int)
    @pyqtSlot(float)
    def setSpotsize(self, newvalue):
        self.spotsize.setValue(newvalue)

    @pyqtSlot(int)
    @pyqtSlot(float)
    def setNominalSpotsize(self, newvalue):
        self.spotsize.setNominalValue(newvalue)

    @pyqtSlot(int, int)
    @pyqtSlot(float, float)
    @pyqtSlot(int, float)
    @pyqtSlot(float, int)
    def setSpotsize(self, newvalue, new_nom_value):
        self.spotsize.setValue(newvalue, new_nom_value)

    @pyqtSlot(int)
    @pyqtSlot(float)
    def setCondenserAperture(self, newvalue):
        self.condenser_aperture.setValue(newvalue)

    @pyqtSlot(int)
    @pyqtSlot(float)
    def setNominalCondenserAperture(self, newvalue):
        self.condenser_aperture.setNominalValue(newvalue)

    @pyqtSlot(int, int)
    @pyqtSlot(float, float)
    @pyqtSlot(int, float)
    @pyqtSlot(float, int)
    def setCondenserAperture(self, newvalue, new_nom_value):
        self.condenser_aperture.setValue(newvalue)
        self.condenser_aperture.setNominalValue(new_nom_value)

    @pyqtSlot(int)
    @pyqtSlot(float)
    def setConvergenceAngle(self, newvalue):
        self.convergence_angle.setValue(newvalue)

    @pyqtSlot(int)
    @pyqtSlot(float)
    def setNominalConvergenceAngle(self, newvalue):
        self.convergence_angle.setNominalValue(newvalue)

    @pyqtSlot(int, int)
    @pyqtSlot(float, float)
    @pyqtSlot(int, float)
    @pyqtSlot(float, int)
    def setConvergenceAngle(self, newvalue, new_nom_value):
        self.convergence_angle.setValue(newvalue, new_nom_value)

    @pyqtSlot(int)
    @pyqtSlot(float)
    def setRockingAngle(self, newvalue):
        self.rocking_angle.setValue(newvalue)

    @pyqtSlot(int)
    @pyqtSlot(float)
    def setNominalRockingAngle(self, newvalue):
        self.rocking_angle.setNominalValue(newvalue)

    @pyqtSlot(int, int)
    @pyqtSlot(float, float)
    @pyqtSlot(int, float)
    @pyqtSlot(float, int)
    def setRockingAngle(self, newvalue, new_nom_value):
        self.rocking_angle.setValue(newvalue, new_nom_value)

    @pyqtSlot(int)
    @pyqtSlot(float)
    def setRockingFrequency(self, newvalue):
        self.rocking_frequency.setValue(newvalue)

    @pyqtSlot(int)
    @pyqtSlot(float)
    def setStepX(self, newvalue):
        self.step_x.setValue(newvalue)

    @pyqtSlot(int)
    @pyqtSlot(float)
    def setNominalStepX(self, newvalue):
        self.step_x.setNominalValue(newvalue)

    @pyqtSlot(int, int)
    @pyqtSlot(float, float)
    @pyqtSlot(int, float)
    @pyqtSlot(float, int)
    def setStepX(self, newvalue, new_nom_value):
        self.step_x.setValue(newvalue, new_nom_value)

    @pyqtSlot(int)
    @pyqtSlot(float)
    def setStepY(self, newvalue):
        self.step_y.setValue(newvalue)

    @pyqtSlot(int)
    @pyqtSlot(float)
    def setNominalStepY(self, newvalue):
        self.step_y.setNominalValue(newvalue)

    @pyqtSlot(int, int)
    @pyqtSlot(float, float)
    @pyqtSlot(int, float)
    @pyqtSlot(float, int)
    def setStepY(self, newvalue, new_nom_value):
        self.step_y.setValue(newvalue, new_nom_value)

    @pyqtSlot(str)
    @pyqtSlot(datetime)
    def setAcquisitionDate(self, newvalue):
        self.acquisition_date.setValue(newvalue)

class QDetctor(QObject, Detector):
    pass
