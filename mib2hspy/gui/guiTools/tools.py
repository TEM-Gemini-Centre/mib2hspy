import sys
import pandas as pd
import traceback

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QAbstractTableModel, QRunnable, QAbstractItemModel
from PyQt5.QtGui import QPixmap

from pathlib import Path

import logging

class QTextEditLogger(logging.Handler, QObject):
    appendPlainText = pyqtSignal(str)

    def __init__(self, widget):
        super().__init__()
        QObject.__init__(self)
        #self.widget = QtWidgets.QPlainTextEdit(parent)
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
        #self.kwargs['progress_callback'] = self.signals.progress

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
    def __init__(self, dictionary = {}, parent=None):
        super(DictionaryTreeModel, self).__init__(parent=parent)
        self._dictionary = dict(dictionary)

    def set_dictionary(self, dictionary):
        self.beginResetModel()
        self._dictionary = dict(dictionary)
        self.endResetModel()

    #def

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
    accepted_statuses = none_statuses+off_statuses+on_statuses+busy_statuses
    #_ = [accepted_statuses.extend(status_values[key] for key in status_values)]

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
            raise StatusError('Status {status!r} not found in accepted statuses {self.accepted_statuses!r}'.format(status=status, self=self))
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
                raise StatusError('Cannot redraw status indicator. Status {status} is not recognized!'.format(status=self.Status()))
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

    @pyqtSlot(int, name = 'setStatus')
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
            raise StatusError('Cannot redraw status indicator. Status {status} is not recognized!'.format(self.Status()))
        pixmap = QPixmap(str(pixmap_path))
        if pixmap.isNull():
            raise ValueError(
                'Image for status {self.status} is Null (path: "{path}"!'.format(self=self, path=pixmap_path))
        self.setPixmap(pixmap)
