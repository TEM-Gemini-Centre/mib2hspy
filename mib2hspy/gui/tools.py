from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from ..Tools import Microscope, Parameter, CalibratedParameter, Detector
from datetime import datetime

class QParameter(QObject, Parameter):
    nameChanged = pyqtSignal([], name='nameChanged')
    unitsChanged = pyqtSignal([], name='unitsChanged')
    valueChanged = pyqtSignal([], name='valueChanged')

    def __init__(self, parent, name, value, units):
        QObject.__init__(self, parent)
        Parameter.__init__(self, name, value, units)

    @pyqtSlot(str, name='setName', result=None)
    def setName(self, newname):
        Parameter.set_name(self, newname)
        self.nameChanged.emit()

    @pyqtSlot(str, name='setUnits', result=None)
    def setUnits(self, newunits):
        Parameter.set_units(self, newunits)
        self.unitsChanged.emit()

    @pyqtSlot(int, name='setValue', result=None)
    @pyqtSlot(float, name='setValue', result=None)
    @pyqtSlot(str, name='setValue', result=None)
    @pyqtSlot(datetime, name='setValue', result=None)
    def setValue(self, newvalue):
        Parameter.set_value(self, newvalue)
        self.valueChanged.emit()


class QCalibratedParameter(QObject, CalibratedParameter):
    pass


class QMicroscope(QObject, Microscope):
    pass


class QDetctor(QObject, Detector):
    pass
