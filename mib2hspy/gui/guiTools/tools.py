import sys
import pandas as pd
import traceback

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QAbstractTableModel, QRunnable, QAbstractItemModel
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QSizePolicy

from pathlib import Path

from datetime import datetime

import logging


class QMicroscope(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        """

        :param microscope_parameters: The microscope parameters connected to the parameter view
        :param args: Optional positional arguments passed to the QWidget constructor.
        :param kwargs: Optional keyword arguments passed to the QWidget constructor.
        :type microscope_parameters: Union[MicroscopeParameters, None]
        """
        super(QMicroscope, self).__init__(*args, **kwargs)

        # Set up main layout
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.setLayout(self.mainLayout)

        # Set up group boxes
        self.controlGroup = QtWidgets.QGroupBox(self)
        self.controlGroup.setTitle('Nominal acquisition parameters')
        self.controlGroupLayout = QtWidgets.QVBoxLayout()
        #self.controlGroupLayout.addStretch()
        self.controlGroup.setLayout(self.controlGroupLayout)
        self.mainLayout.addWidget(self.controlGroup)

        self.viewGroup = QtWidgets.QGroupBox(self)
        self.viewGroup.setTitle('Acquisition parameter view')
        self.viewGroupLayout = QtWidgets.QVBoxLayout()
        self.viewGroup.setLayout(self.viewGroupLayout)
        self.mainLayout.addWidget(self.viewGroup)

        #Set up view widgets
        self.tableView = QtWidgets.QTableView()
        self.viewGroupLayout.addWidget(self.tableView)

        # Set up control widgets
        self.controlScrollArea = QtWidgets.QScrollArea(self.controlGroup)
        self.controlGroupLayout.addWidget(self.controlScrollArea)
        self.controlScrollArea.setWidgetResizable(True)
        self.controlScrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.controlScrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.controlScrollAreaLayout = QtWidgets.QGridLayout()

        # HT
        self.highTensionCheckBox = QtWidgets.QCheckBox('High Tension', self)
        self.highTensionSpinBox = QtWidgets.QSpinBox(self)
        self.highTensionUnitsLabel = QtWidgets.QLabel('keV')
        self.controlScrollAreaLayout.addWidget(self.highTensionCheckBox, 0, 0)
        self.controlScrollAreaLayout.addWidget(self.highTensionSpinBox, 0, 1)
        self.controlScrollAreaLayout.addWidget(self.highTensionUnitsLabel, 0, 2)

        # Magnification
        self.magnificationCheckBox = QtWidgets.QCheckBox('Magnification')
        self.magnificationSpinBox = QtWidgets.QSpinBox()
        self.magnificationSelector = QtWidgets.QComboBox()
        self.controlScrollAreaLayout.addWidget(self.magnificationCheckBox, 1, 0)
        self.controlScrollAreaLayout.addWidget(self.magnificationSpinBox, 1, 1)
        self.controlScrollAreaLayout.addWidget(self.magnificationSelector, 1, 2)

        # Cameralength
        self.cameraLengthCheckBox = QtWidgets.QCheckBox('Cameralength')
        self.cameraLengthSpinBox = QtWidgets.QSpinBox()
        self.cameraLengthUnitsLabel = QtWidgets.QLabel('cm')
        self.controlScrollAreaLayout.addWidget(self.cameraLengthCheckBox, 2, 0)
        self.controlScrollAreaLayout.addWidget(self.cameraLengthSpinBox, 2, 1)
        self.controlScrollAreaLayout.addWidget(self.cameraLengthUnitsLabel, 2, 2)

        # Mode
        self.modeCheckBox = QtWidgets.QCheckBox('Mode')
        self.modeSelector = QtWidgets.QComboBox()
        self.controlScrollAreaLayout.addWidget(self.modeCheckBox, 3, 0)
        self.controlScrollAreaLayout.addWidget(self.modeSelector, 3, 1)

        #Alpha
        self.alphaCheckBox = QtWidgets.QCheckBox('Alpha')
        self.alphaSpinBox = QtWidgets.QSpinBox()
        self.controlScrollAreaLayout.addWidget(self.alphaCheckBox, 4, 0)
        self.controlScrollAreaLayout.addWidget(self.alphaSpinBox, 4, 1)

        #Spot
        self.spotCheckBox = QtWidgets.QCheckBox('Spot')
        self.spotSpinBox = QtWidgets.QSpinBox()
        self.controlScrollAreaLayout.addWidget(self.spotCheckBox, 5, 0)
        self.controlScrollAreaLayout.addWidget(self.spotSpinBox, 5, 1)

        #Spotsize
        self.spotSizeCheckBox = QtWidgets.QCheckBox('Spotsize')
        self.spotSizeSpinBox = QtWidgets.QDoubleSpinBox()
        self.spotSizeUnitsLabel = QtWidgets.QLabel('nm')
        self.controlScrollAreaLayout.addWidget(self.spotSizeCheckBox, 6, 0)
        self.controlScrollAreaLayout.addWidget(self.spotSizeSpinBox, 6, 1)
        self.controlScrollAreaLayout.addWidget(self.spotSizeUnitsLabel, 6, 2)

        #Condenser aperture
        self.condenserApertureCheckBox = QtWidgets.QCheckBox('Condenser Aperture')
        self.condenserApertureSpinBox = QtWidgets.QSpinBox()
        self.condenserApertureUnitsLabel = QtWidgets.QLabel('um')
        self.controlScrollAreaLayout.addWidget(self.condenserApertureCheckBox, 7, 0)
        self.controlScrollAreaLayout.addWidget(self.condenserApertureSpinBox, 7, 1)
        self.controlScrollAreaLayout.addWidget(self.condenserApertureUnitsLabel, 7, 2)

        # Convergence angle
        self.convergenceAngleCheckBox = QtWidgets.QCheckBox('Convergence Angle')
        self.convergenceAngleSpinBox = QtWidgets.QDoubleSpinBox()
        self.convergenceAngleUnitsLabel = QtWidgets.QLabel('mrad')
        self.controlScrollAreaLayout.addWidget(self.convergenceAngleCheckBox, 8, 0)
        self.controlScrollAreaLayout.addWidget(self.convergenceAngleSpinBox, 8, 1)
        self.controlScrollAreaLayout.addWidget(self.convergenceAngleUnitsLabel, 8, 2)

        # Precession frequency
        self.precessionFrequencyCheckBox = QtWidgets.QCheckBox('Rocking Frequency')
        self.precessionFrequencySpinBox = QtWidgets.QSpinBox()
        self.precessionFrequencyUnitsLabel = QtWidgets.QLabel('Hz')
        self.controlScrollAreaLayout.addWidget(self.precessionFrequencyCheckBox, 9, 0)
        self.controlScrollAreaLayout.addWidget(self.precessionFrequencySpinBox, 9, 1)
        self.controlScrollAreaLayout.addWidget(self.precessionFrequencyUnitsLabel, 9, 2)

        # Rocking angle
        self.precessionAngleCheckBox = QtWidgets.QCheckBox('Rocking Angle')
        self.precessionAngleSpinBox = QtWidgets.QDoubleSpinBox()
        self.precessionAngleUnitsLabel = QtWidgets.QLabel('deg')
        self.controlScrollAreaLayout.addWidget(self.precessionAngleCheckBox, 10, 0)
        self.controlScrollAreaLayout.addWidget(self.precessionAngleSpinBox, 10, 1)
        self.controlScrollAreaLayout.addWidget(self.precessionAngleUnitsLabel, 10, 2)

        # Acquisition date
        self.acquisitionDateCheckBox = QtWidgets.QCheckBox('Acquisition Date')
        self.acquisitionDate = QtWidgets.QDateEdit(datetime.now().date())
        self.controlScrollAreaLayout.addWidget(self.acquisitionDateCheckBox, 11, 0)
        self.controlScrollAreaLayout.addWidget(self.acquisitionDate, 11, 1)

        # Camera
        self.cameraCheckBox = QtWidgets.QCheckBox('Camera')
        self.cameraComboBox = QtWidgets.QComboBox()
        self.controlScrollAreaLayout.addWidget(self.cameraCheckBox, 12, 0)
        self.controlScrollAreaLayout.addWidget(self.cameraComboBox, 12, 1)

        # Microscope
        self.microscopeCheckBox = QtWidgets.QCheckBox('Microscope')
        self.microscopeComboBox = QtWidgets.QComboBox()
        self.controlScrollAreaLayout.addWidget(self.microscopeCheckBox, 13, 0)
        self.controlScrollAreaLayout.addWidget(self.microscopeComboBox, 13, 1)

        # Scan steps
        self.stepGroupBox = QtWidgets.QGroupBox('Scan step')
        self.stepLayout = QtWidgets.QGridLayout()
        self.stepGroupBox.setLayout(self.stepLayout)
        self.stepGroupBox.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))

        self.controlScrollAreaLayout.addWidget(self.stepGroupBox, 14, 0, 3, 3)
        self.stepXDirectionLabel = QtWidgets.QLabel('X')
        self.stepYDirectionLabel = QtWidgets.QLabel('Y')
        self.stepXSpinBox = QtWidgets.QDoubleSpinBox()
        self.stepYSpinBox = QtWidgets.QDoubleSpinBox()
        self.stepXUnitsLabel = QtWidgets.QLabel('nm')
        self.stepYUnitsLabel = QtWidgets.QLabel('nm')

        #Stretcher
        self.controlScrollAreaStretcher = QtWidgets.QVBoxLayout()
        self.controlScrollAreaStretcher.addStretch()
        self.controlScrollAreaLayout.addLayout(self.controlScrollAreaStretcher, 17, 0, 1, 3)

        #Set the control layout
        self.controlScrollArea.setLayout(self.controlScrollAreaLayout)

        self.setup_controllers()

    def setup_controllers(self):
        #HT
        self.highTensionSpinBox.setMinimum(0)
        self.highTensionSpinBox.setMaximum(200)
        self.highTensionCheckBox.stateChanged.connect(lambda x: self.highTensionSpinBox.setEnabled(bool(x)))
        self.highTensionCheckBox.setChecked(True)

        #Magnification
        self.magnificationSpinBox.setMinimum(0)
        self.magnificationSpinBox.setMaximum(2000000)
        self.magnificationSpinBox.setSingleStep(1000)
        self.magnificationSelector.addItems(['MAG1', 'SAMAG'])
        self.magnificationCheckBox.stateChanged.connect(lambda x: self.magnificationSpinBox.setEnabled(bool(x)))
        self.magnificationCheckBox.stateChanged.connect(lambda x: self.magnificationSelector.setEnabled(bool(x)))
        self.magnificationCheckBox.setChecked(False)

        #Cameralength
        self.cameraLengthSpinBox.setMinimum(8)
        self.cameraLengthSpinBox.setMaximum(200)
        self.cameraLengthSpinBox.setSingleStep(1)
        self.cameraLengthCheckBox.stateChanged.connect(lambda x: self.cameraLengthSpinBox.setEnabled(bool(x)))
        self.cameraLengthCheckBox.setChecked(False)

        #Mode
        self.modeSelector.addItems(['None', 'STEM', 'LMSTEM', 'TEM', 'NBD', 'CBD'])
        self.modeSelector.setCurrentText('NBD')
        self.modeCheckBox.stateChanged.connect(lambda x: self.modeSelector.setEnabled(bool(x)))
        self.modeCheckBox.setChecked(False)

        # Alpha
        self.alphaSpinBox.setMinimum(1)
        self.alphaSpinBox.setMaximum(5)
        self.alphaSpinBox.setSingleStep(1)
        self.alphaSpinBox.setValue(5)
        self.alphaCheckBox.stateChanged.connect(lambda x: self.alphaSpinBox.setEnabled(bool(x)))
        self.alphaCheckBox.setChecked(False)

        # Spot
        self.spotSpinBox.setMinimum(1)
        self.spotSpinBox.setMaximum(10)
        self.spotSpinBox.setValue(1)
        self.spotCheckBox.stateChanged.connect(lambda x: self.spotSpinBox.setEnabled(bool(x)))
        self.spotCheckBox.setChecked(False)

        # Spotsize
        self.spotSizeSpinBox.setMinimum(0.1)
        self.spotSizeSpinBox.setMaximum(10)
        self.spotSizeSpinBox.setDecimals(2)
        self.spotSizeSpinBox.setSingleStep(0.1)
        self.spotSizeSpinBox.setValue(0.3)
        self.spotSizeCheckBox.stateChanged.connect(lambda x: self.spotSizeSpinBox.setEnabled(bool(x)))
        self.spotSizeCheckBox.setChecked(False)

        #Condenser aperture
        self.condenserApertureSpinBox.setMinimum(1)
        self.condenserApertureSpinBox.setMaximum(500)
        self.condenserApertureSpinBox.setValue(40)
        self.condenserApertureSpinBox.setSingleStep(10)
        self.condenserApertureCheckBox.stateChanged.connect(lambda x: self.condenserApertureSpinBox.setEnabled(bool(x)))
        self.condenserApertureCheckBox.setChecked(False)

        #Convergence angle
        self.convergenceAngleSpinBox.setMinimum(0)
        self.convergenceAngleSpinBox.setMaximum(99.99)
        self.convergenceAngleSpinBox.setSingleStep(0.1)
        self.convergenceAngleSpinBox.setDecimals(2)
        self.convergenceAngleSpinBox.setValue(0)
        self.convergenceAngleCheckBox.stateChanged.connect(lambda x: self.convergenceAngleSpinBox.setEnabled(bool(x)))

        #Rocking frequency
        self.precessionFrequencySpinBox.setMinimum(0)
        self.precessionFrequencySpinBox.setMaximum(300)
        self.precessionFrequencySpinBox.setSingleStep(10)
        self.precessionFrequencySpinBox.setValue(100)
        self.precessionFrequencyCheckBox.stateChanged.connect(lambda x: self.precessionFrequencySpinBox.setEnabled(bool(x)))
        self.precessionFrequencyCheckBox.setChecked(False)

        #Rocking angle
        self.precessionAngleSpinBox.setMinimum(0)
        self.precessionAngleSpinBox.setMaximum(10)
        self.precessionAngleSpinBox.setSingleStep(0.1)
        self.precessionAngleSpinBox.setDecimals(2)
        self.precessionAngleSpinBox.setValue(1.00)
        self.precessionAngleCheckBox.stateChanged.connect(lambda x: self.precessionAngleSpinBox.setEnabled(bool(x)))
        self.precessionAngleCheckBox.setChecked(False)

        #Acquisition date
        self.acquisitionDate.setDisplayFormat('dd.MM.yyyy')
        self.acquisitionDate.setMaximumDate(datetime.now().date())
        self.acquisitionDate.setCalendarPopup(True)
        self.acquisitionDateCheckBox.stateChanged.connect(lambda x: self.acquisitionDate.setEnabled(bool(x)))
        self.acquisitionDateCheckBox.setChecked(False)

        #Camera
        self.cameraComboBox.addItems(['Merlin', 'US1000 1'])
        self.cameraComboBox.setCurrentText('Merlin')
        self.cameraCheckBox.stateChanged.connect(lambda x: self.cameraComboBox.setEnabled(bool(x)))
        self.cameraCheckBox.setChecked(True)

        #Microscope
        self.microscopeComboBox.addItems(['2100', '2100F', 'ARM200F'])
        self.microscopeComboBox.setCurrentText('2100F')
        self.microscopeCheckBox.stateChanged.connect(lambda x: self.microscopeComboBox.setEnabled(bool(x)))
        self.microscopeCheckBox.setChecked(True)

        #Scan steps
        self.stepGroupBox.setCheckable(True)
        for row, direction in enumerate(['X', 'Y']):
            if direction == 'X':
                direction_label = self.stepXDirectionLabel
                spinbox = self.stepXSpinBox
                units_label = self.stepXUnitsLabel
            else:
                direction_label = self.stepYDirectionLabel
                spinbox = self.stepYSpinBox
                units_label = self.stepYUnitsLabel
            spinbox.setMinimum(0)
            spinbox.setMaximum(1000)
            spinbox.setDecimals(2)
            spinbox.setSingleStep(0.1)

            self.stepLayout.addWidget(direction_label, row, 0)
            self.stepLayout.addWidget(spinbox, row, 1)
            self.stepLayout.addWidget(units_label, row, 2)
            self.stepGroupBox.toggled.connect(lambda x: spinbox.setEnabled(bool(x)))
        self.stepGroupBox.setChecked(False)


class QTextEditLogger(logging.Handler, QObject):
    appendPlainText = pyqtSignal(str)

    def __init__(self, widget):
        super().__init__()
        QObject.__init__(self)
        # self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget = widget
        self.widget.setReadOnly(True)
        self.appendPlainText.connect(self.widget.appendPlainText)

    def emit(self, record):
        msg = self.format(record)
        self.appendPlainText.emit(msg)


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress

    """
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal([], [int], [str], [bool], [object])
    progress = pyqtSignal(int)


class Worker(QRunnable):
    """
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    """

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.result = None

        # Add the callback to our kwargs
        # self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            self.result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            try:
                self.signals.result[type(self.result)].emit(self.result)
            except Exception:
                self.signals.result[object].emit(self.result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class DataFrameModel(QAbstractTableModel):
    DtypeRole = QtCore.Qt.UserRole + 1000
    ValueRole = QtCore.Qt.UserRole + 1001

    def __init__(self, df=pd.DataFrame(), parent=None):
        super(DataFrameModel, self).__init__(parent)
        self._dataframe = df

    def setDataFrame(self, dataframe):
        self.beginResetModel()
        self._dataframe = dataframe.copy()
        self.endResetModel()

    def dataFrame(self):
        return self._dataframe

    dataFrame = QtCore.pyqtProperty(pd.DataFrame, fget=dataFrame, fset=setDataFrame)

    @QtCore.pyqtSlot(int, QtCore.Qt.Orientation, result=str)
    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.dataFrame.columns[section]
            else:
                return str(self.dataFrame.index[section])
        return QtCore.QVariant()

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.dataFrame.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return self.dataFrame.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount() and 0 <= index.column() < self.columnCount()):
            return QtCore.QVariant()
        row = self.dataFrame.index[index.row()]
        col = self.dataFrame.columns[index.column()]
        dt = self.dataFrame[col].dtype

        val = self.dataFrame.iloc[row][col]

        if role == QtCore.Qt.DisplayRole:
            return str(val)
        elif role == DataFrameModel.ValueRole:
            return val
        if role == DataFrameModel.DtypeRole:
            return dt
        return QtCore.QVariant()

    def roleNames(self):
        roles = {
            QtCore.Qt.DisplayRole: b'display',
            DataFrameModel.DtypeRole: b'dtype',
            DataFrameModel.ValueRole: b'value'
        }
        return roles


class DictionaryTreeModel(QAbstractItemModel):
    def __init__(self, dictionary={}, parent=None):
        super(DictionaryTreeModel, self).__init__(parent=parent)
        self._dictionary = dict(dictionary)

    def set_dictionary(self, dictionary):
        self.beginResetModel()
        self._dictionary = dict(dictionary)
        self.endResetModel()

    # def


class Error(Exception):
    pass


class StatusError(Error):
    pass


# class Status(QObject):
#     """A status object for keeping track of the status of other objects"""
#     statusChanged = pyqtSignal([], [str], [int], [bool], [QObject])
#     active_labels = ['Active', 'On', 1, True]
#     busy_labels = ['Busy', 'Pending', 2]
#     inactive_labels = ['Inactive', 'Off', 0, False]
#     none_labels = ['None', -1., None]
#     accepted_statuses = active_labels + busy_labels + inactive_labels + none_labels
#
#     def __init__(self, initial_status, *args, **kwargs):
#         """
#         Initialize a status object.
#
#         A status object has three different status categories, "Inactive": 0, "Active": 1, and "Busy": 2. The different categories have additional labels and values.
#
#         :param initial_status: The initial status of the object.
#         :param args: Optional positional arguments passed to QObject()
#         :param kwargs: Optional keyword arguments passed to QObject()
#         """
#         if not initial_status in self.accepted_statuses:
#             raise StatusError(
#                 'Status "{status}" is not an accepted status. Please set status to one of the following: {self.accepted_statuses}'.format(
#                     status=initial_status, self=self))
#         super(Status, self).__init__(*args, **kwargs)
#         self._status = initial_status
#
#     @property
#     def status(self):
#         if self._status in self.inactive_labels:
#             return 0
#         elif self._status in self.active_labels:
#             return 1
#         elif self._status in self.pending_labels:
#             return 2
#         elif self._status in self.none_labels:
#             return -1
#         else:
#             raise StatusError('Status of {self} can not be categorized!'.format(self=self))
#
#     @status.setter
#     def status(self, status):
#         if status not in self.accepted_statuses:
#             raise StatusError(
#                 'Status "{status}" is not an accepted status. Please set status to one of the following: {self.accepted_statuses}'.format(
#                     status=status, self=self))
#         self._status = status
#         self.statusChanged.emit()
#         self.statusChanged[type(self.status)].emit(self.status)
#         self.statusChanged[QObject].emit(self)
#
#     def __str__(self):
#         if self.status == 0:
#             label = 'Inactive'
#         elif self.status == 1:
#             label = 'Active'
#         elif self.status == 2:
#             label = 'Busy'
#         elif self.status == -1:
#             label = 'None'
#         else:
#             label = self.status
#         return '{self.__class__.__name__}: {self._status} ({label})'.format(self=self, label=label)
#
#     @pyqtSlot()
#     def setInactive(self):
#         self.status = 0
#
#     @pyqtSlot()
#     def setActive(self):
#         self.status = 1
#
#     @pyqtSlot()
#     def setBusy(self):
#         self.status = 2
#
#     @pyqtSlot()
#     def setNone(self):
#         self.status = -1
#
#     @pyqtSlot(int)
#     @pyqtSlot(str)
#     @pyqtSlot(bool)
#     def setStatus(self, status):
#         self.status = status
#
#     def is_inactive(self):
#         return self.status in self.inactive_labels
#
#     def is_active(self):
#         return self.status in self.active_labels
#
#     def is_busy(self):
#         return self.status in self.busy_labels
#
#     def is_none(self):
#         return self.status in self.none_labels


class StatusIndicator(QtWidgets.QLabel):
    """A status indicator widget"""
    inactive_pixmap_path = Path(__file__).parent / Path('../source/icons/Off.png')
    active_pixmap_path = Path(__file__).parent / Path('../source/icons/On.png')
    busy_pixmap_path = Path(__file__).parent / Path('../source/icons/Busy.png')
    none_pixmap_path = Path(__file__).parent / Path('../source/icons/None.png')

    statusChanged = pyqtSignal([], [str], [int], [bool], [QObject])
    none_statuses = [-1, 'None', '', None]
    off_statuses = [0, False, 'Inactive', 'Off', 'Failed']
    on_statuses = [1, True, 'Active', 'On']
    busy_statuses = [2, 'Busy', 'Pending']
    status_values = {
        -1: [-1, 'None', '', None],
        0: [0, 'Inactive', 'Off', 'Failed', False],
        1: [1, 'Active', 'On', True],
        2: [2, 'Busy', 'Pending']
    }
    accepted_statuses = none_statuses + off_statuses + on_statuses + busy_statuses

    # _ = [accepted_statuses.extend(status_values[key] for key in status_values)]

    def __init__(self, *args, initial_status=None, **kwargs):
        """
        Initialize a status indicator.
        :param args: Optional positional arguments passed to QLabel()
        :param initial_status: The initial status of the indicator
        :param kwargs: Optional keyword arguments passed to QLabel()
        """
        super(StatusIndicator, self).__init__(*args, **kwargs)

        if initial_status not in self.accepted_statuses:
            raise ValueError()
        self._status = initial_status

        self.setScaledContents(True)
        self.statusChanged.connect(self.reDraw)

    def set_status(self, status):
        if status not in self.accepted_statuses:
            raise StatusError(
                'Status {status!r} not found in accepted statuses {self.accepted_statuses!r}'.format(status=status,
                                                                                                     self=self))
        self._status = status

        try:
            if self.is_inactive():
                pixmap_path = self.inactive_pixmap_path
            elif self.is_active():
                pixmap_path = self.active_pixmap_path
            elif self.is_busy():
                pixmap_path = self.busy_pixmap_path
            elif self.is_none():
                pixmap_path = self.none_pixmap_path
            else:
                raise StatusError(
                    'Cannot redraw status indicator. Status {status} is not recognized!'.format(status=self.Status()))
        except StatusError:
            raise
        else:
            pixmap = QPixmap(str(pixmap_path))
            if pixmap.isNull():
                raise ValueError(
                    'Image for status {self._status} is Null (path: "{path}"!'.format(self=self, path=pixmap_path))
            self.setPixmap(pixmap)

    def get_status(self):
        for key in self.status_values:
            if self._status in self.status_values[key]:
                return key

        raise StatusError(
            'Status "{self._status!r}" is not fould in the accepted status values {self.status_values!r}!'.format(
                self=self))

    def is_none(self):
        return self.Status() == -1

    def is_inactive(self):
        return self.Status() == 0

    def is_busy(self):
        return self.Status() == 2

    def is_active(self):
        return self.Status() == 1

    @pyqtSlot(name='Status', result=int)
    def Status(self):
        return self.get_status()

    @pyqtSlot(int, name='setStatus')
    @pyqtSlot(str, name='setStatus')
    @pyqtSlot(bool, name='setStatus')
    def setStatus(self, status):
        self.set_status(status)
        self.statusChanged.emit()
        self.statusChanged[int].emit(self.get_status())

    @pyqtSlot(name='isNone', result=bool)
    def isNone(self):
        return self.is_none()

    @pyqtSlot(name='isInactive', result=bool)
    def isInactive(self):
        return self.is_inactive()

    @pyqtSlot(name='isBusy', result=bool)
    def isBusy(self):
        return self.is_busy()

    @pyqtSlot(name='isActive', result=bool)
    def isActive(self):
        return self.is_active()

    @pyqtSlot(name='setNone')
    def setNone(self):
        self.set_status(-1)
        self.statusChanged.emit()
        self.statusChanged[int].emit(-1)
        self.statusChanged[str].emit('None')

    @pyqtSlot(name='setInactive')
    def setInactive(self):
        self.set_status(0)
        self.statusChanged.emit()
        self.statusChanged[int].emit(0)
        self.statusChanged[bool].emit(False)
        self.statusChanged[str].emit('Off')

    @pyqtSlot(name='setActive')
    def setActive(self):
        self.set_status(1)
        self.statusChanged.emit()
        self.statusChanged[int].emit(1)
        self.statusChanged[bool].emit(True)
        self.statusChanged[str].emit('On')

    @pyqtSlot(name='setBusy')
    def setBusy(self):
        self.set_status(2)
        self.statusChanged.emit()
        self.statusChanged[int].emit(2)
        self.statusChanged[str].emit('Busy')

    @pyqtSlot()
    def reDraw(self):
        if self.isInactive():
            pixmap_path = self.inactive_pixmap_path
        elif self.isActive():
            pixmap_path = self.active_pixmap_path
        elif self.isBusy():
            pixmap_path = self.busy_pixmap_path
        elif self.isNone():
            pixmap_path = self.none_pixmap_path
        else:
            raise StatusError(
                'Cannot redraw status indicator. Status {status} is not recognized!'.format(self.Status()))
        pixmap = QPixmap(str(pixmap_path))
        if pixmap.isNull():
            raise ValueError(
                'Image for status {self.status} is Null (path: "{path}"!'.format(self=self, path=pixmap_path))
        self.setPixmap(pixmap)

