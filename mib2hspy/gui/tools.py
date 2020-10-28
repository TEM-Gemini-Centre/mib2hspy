import sys
import pandas as pd
import traceback

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QAbstractTableModel, QRunnable
from PyQt5.QtGui import QPixmap

from pathlib import Path


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
    result = pyqtSignal(str)
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

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
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


class Error(Exception):
    pass


class StatusError(Error):
    pass


class Status(QObject):
    """A status object for keeping track of the status of other objects"""
    statusChanged = pyqtSignal([], [str], [int], [bool], [QObject])
    active_labels = ['Active', 'On', 1, True]
    busy_labels = ['Busy', 'Pending', 2]
    inactive_labels = ['Inactive', 'Off', 0, False]
    accepted_statuses = active_labels + busy_labels + inactive_labels

    def __init__(self, initial_status, *args, **kwargs):
        """
        Initialize a status object.

        A status object has three different status categories, "Inactive": 0, "Active": 1, and "Busy": 2. The different categories have additional labels and values.

        :param initial_status: The initial status of the object.
        :param args: Optional positional arguments passed to QObject()
        :param kwargs: Optional keyword arguments passed to QObject()
        """
        if not initial_status in self.accepted_statuses:
            raise StatusError(
                'Status "{status}" is not an accepted status. Please set status to one of the following: {self.accepted_statuses}'.format(
                    status=initial_status, self=self))
        super(Status, self).__init__(*args, **kwargs)

        self._status = initial_status

    def __str__(self):
        if self.status == 0:
            label = 'Inactive'
        elif self.status == 1:
            label = 'Active'
        elif self.status == 2:
            label = 'Busy'
        else:
            label = self.status
        return '{self.__class__.__name__}: {self.status} ({label})'.format(self=self, label=label)

    @property
    def status(self):
        if self._status in self.inactive_labels:
            return 0
        elif self._status in self.active_labels:
            return 1
        elif self._status in self.pending_labels:
            return 2
        else:
            raise StatusError('Status of {self} can not be categorized!'.format(self=self))

    @status.setter
    def status(self, status):
        if not status in self.accepted_statuses:
            raise StatusError(
                'Status "{status}" is not an accepted status. Please set status to one of the following: {self.accepted_statuses}'.format(
                    status=status, self=self))
        self._status = status
        self.statusChanged.emit()
        self.statusChanged[type(self.status)].emit(self.status)
        self.statusChanged[QObject].emit(self)

    @pyqtSlot()
    def setInactive(self):
        self.status = 0

    @pyqtSlot()
    def setActive(self):
        self.status = 1

    @pyqtSlot()
    def setBusy(self):
        self.status = 2

    @pyqtSlot(int)
    @pyqtSlot(str)
    @pyqtSlot(bool)
    def setStatus(self, status):
        self.status = status

    def is_inactive(self):
        return self.status in self.inactive_labels

    def is_active(self):
        return self.status in self.active_labels

    def is_busy(self):
        return self.status in self.busy_labels


class StatusIndicator(QtWidgets.QLabel):
    """A status indicator widget"""
    inactive_pixmap_path = Path('./source/icons/Off.png')
    active_pixmap_path = Path('./source/icons/On.png')
    busy_pixmap_path = Path('./source/icons/Busy.png')
    none_pixmap_path = Path('./source/icons/None.png')

    def __init__(self, *args, initial_status=None, **kwargs):
        """
        Initialize a status indicator.
        :param args: Optional positional arguments passed to QLabel()
        :param initial_status: The initial status of the indicator
        :param kwargs: Optional keyword arguments passed to QLabel()
        """
        super(StatusIndicator, self).__init__(*args, **kwargs)

        self.status = Status(initial_status)
        self.setScaledContents(True)
        self.status.statusChanged.connect(self.reDraw)

    @pyqtSlot()
    def reDraw(self):
        if self.status.is_inactive():
            pixmap_path = self.inactive_pixmap_path
        elif self.status.is_active():
            pixmap_path = self.active_pixmap_path
        elif self.status.is_busy():
            pixmap_path = self.busy_pixmap_path
        else:
            pixmap_path = self.none_pixmap_path
        pixmap = QPixmap(str(pixmap_path))
        if pixmap.isNull():
            raise ValueError(
                'Image for status {self.status} is Null (path: "{path}"!'.format(self=self, path=pixmap_path))
        self.setPixmap(pixmap)
