import logging
import sys
from datetime import datetime
from pathlib import Path
from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThreadPool, QObject
import pandas as pd
from math import sqrt, isclose, nan, isnan
from mib2hspy.gui.guiTools import QTextEditLogger, DataFrameModel
from mib2hspy.Tools import Converter


class LogStream(object):
    """
    Class for handling logging to stream objects.
    """

    def __init__(self, logger, log_level=logging.DEBUG):
        """
        Create a log stream
        :param logger: logging.Logger object
        :param log_level: logging level
        """
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        """
        Log a message and write it to the stream
        :param buf:
        :return:
        """
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())


class ParameterController(QObject):
    accelerationVoltageChanged = pyqtSignal([], [int], [float], [str])
    modeChanged = pyqtSignal([], [int], [float], [str])
    magModeChanged = pyqtSignal([], [int], [float], [str])
    magnificationChanged = pyqtSignal([], [int], [float], [str])
    cameralengthChanged = pyqtSignal([], [int], [float], [str])
    alphaChanged = pyqtSignal([], [int], [float], [str])
    stepSizeXChanged = pyqtSignal([], [int], [float], [str])
    stepSizeYChanged = pyqtSignal([], [int], [float], [str])
    condenserApertureChanged = pyqtSignal([], [int], [float], [str])
    convergenceAngleChanged = pyqtSignal([], [int], [float], [str])
    rockingAngleChanged = pyqtSignal([], [int], [float], [str])
    rockingFrequencyChanged = pyqtSignal([], [int], [float], [str])
    spotChanged = pyqtSignal([], [int], [float], [str])
    spotSizeChanged = pyqtSignal([], [int], [float], [str])
    cameraChanged = pyqtSignal([], [str])
    microscopeNameChanged = pyqtSignal([], [str])
    acquisitionDateChanged = pyqtSignal([])

    tableChanged = pyqtSignal([])

    def __init__(self, view, model, calibrationtable=None):
        """
        Create a controller for parameter view and model
        :param view: The window to control the parameters
        :param model: The model to store the parameters in
        :param calibrationtable: Calibration table to look up calibration values in.
        :type view: ParametersWindow
        :type model: MicroscopeParameters
        :type calibrationtable: pandas.DataFrame
        """
        super(ParameterController, self).__init__()
        self._view = view
        self._model = model
        self._table = calibrationtable or pd.DataFrame()

        self._table_model = DataFrameModel(parent=self._view)
        self._view.tableView.setModel(self._table_model)

        # Setup widgets and widget signals
        self.setupMagnification()
        self.setupCameralength()
        self.setupAccelerationVoltage()
        self.setupMode()
        self.setupAlpha()
        self.setupSpot()
        self.setupSpotSize()
        self.setupConvergenceAngle()
        self.setupCondenserAperture()
        self.setupPrecessionAngle()
        self.setupPrecessionFrequency()
        self.setupAcquisitionDate()
        self.setupScanStep()
        self.setupCamera()
        self.setupMicroscopeName()
        self.update()

        # Interconnections
        self.accelerationVoltageChanged.connect(self.cameralengthChanged)
        self.accelerationVoltageChanged.connect(self.magnificationChanged)
        self.magModeChanged.connect(self.magnificationChanged)
        self.accelerationVoltageChanged.connect(self.rockingAngleChanged)
        self.alphaChanged.connect(self.rockingAngleChanged)
        self.modeChanged.connect(self.rockingAngleChanged)
        self.cameraChanged.connect(self.cameralengthChanged)
        self.cameraChanged.connect(self.magnificationChanged)
        self.microscopeNameChanged.connect(self.cameralengthChanged)
        self.microscopeNameChanged.connect(self.magnificationChanged)

        # Calibration functionality
        self.accelerationVoltageChanged.connect(lambda: self._model.calibrate(self._table))
        self.magnificationChanged.connect(lambda: self._model.calibrate_image_scale(self._table))
        self.cameralengthChanged.connect(lambda: self._model.calibrate_diffraction_scale(self._table))
        self.rockingAngleChanged.connect(lambda: self._model.calibrate_rocking_angle(self._table))
        self.stepSizeXChanged.connect(lambda: self._model.calibrate_stepsize_x(self._table))
        self.stepSizeYChanged.connect(lambda: self._model.calibrate_stepsize_y(self._table))

    def setupMagnification(self):
        if self._view.magnificationCheckBox.isChecked():
            self._model.set_nominal_magnification(self._view.magnificationSpinBox.value())
            self._model.set_mag_mode(self._view.magnificationSelector.currentText())
        self._view.magnificationSpinBox.valueChanged.connect(self._model.set_nominal_magnification)
        self._view.magnificationSelector.currentTextChanged.connect(self._model.set_mag_mode)
        self._view.magnificationCheckBox.clicked.connect(self.toggle_magnification)
        self._view.magnificationSpinBox.valueChanged.connect(self.magnificationChanged)
        self._view.magnificationSelector.currentTextChanged.connect(self.magModeChanged)
        self._view.magnificationSelector.currentTextChanged.connect(self.update)
        self._view.magnificationSpinBox.valueChanged.connect(self.update)

    def toggle_magnification(self):
        if self._view.magnificationCheckBox.isChecked():
            self._model.set_nominal_magnification(self._view.magnificationSpinBox.value())
            self._model.set_mag_mode(self._view.magnificationSelector.currentText())
            self._view.magnificationSpinBox.setEnabled(True)
            self._view.magnificationSelector.setEnabled(True)
        else:
            self._model.set_nominal_magnification(nan)
            self._model.set_mag_mode('')
            self._view.magnificationSpinBox.setEnabled(False)
            self._view.magnificationSelector.setEnabled(False)
        self.magnificationChanged.emit()
        self.magModeChanged.emit()
        self.update()

    def setupCameralength(self):
        self._view.cameraLengthSpinBox.valueChanged.connect(self._model.set_nominal_cameralength)
        self._view.cameraLengthCheckBox.clicked.connect(self.toggle_cameralength)
        self._view.cameraLengthSpinBox.valueChanged.connect(self.cameralengthChanged)
        self._view.cameraLengthSpinBox.valueChanged.connect(self.update)
        if self._view.cameraLengthCheckBox.isChecked():
            self._model.set_nominal_cameralength(self._view.cameraLengthSpinBox.value())

    def toggle_cameralength(self):
        if self._view.cameraLengthCheckBox.isChecked():
            self._model.set_nominal_cameralength(self._view.cameraLengthSpinBox.value())
            self._view.cameraLengthSpinBox.setEnabled(True)
        else:
            self._model.set_nominal_cameralength(nan)
            self._view.cameraLengthSpinBox.setEnabled(False)
        self.cameralengthChanged.emit()
        self.update()

    def setupAccelerationVoltage(self):
        self._view.highTensionSpinBox.valueChanged.connect(
            lambda x: self._model.set_acceleration_voltage(self._view.highTensionSpinBox.value()))
        self._view.highTensionCheckBox.clicked.connect(self.toggle_acceleration_voltage)
        self._view.highTensionSpinBox.valueChanged.connect(self.accelerationVoltageChanged)
        self._view.highTensionSpinBox.valueChanged.connect(self.update)
        if self._view.highTensionCheckBox.isChecked():
            self._model.set_acceleration_voltage(self._view.highTensionSpinBox.value())

    def toggle_acceleration_voltage(self):
        if self._view.highTensionCheckBox.isChecked():
            self._model.set_acceleration_voltage(self._view.highTensionSpinBox.value())
            self._view.highTensionSpinBox.setEnabled(True)
        else:
            self._model.set_acceleration_voltage(nan)
            self._view.highTensionSpinBox.setEnabled(False)
        self.accelerationVoltageChanged.emit()
        self.update()

    def setupMode(self):
        self._view.modeSelector.currentTextChanged.connect(self._model.set_mode)
        self._view.modeSelector.currentTextChanged.connect(self.update)
        self._view.modeSelector.currentIndexChanged.connect(self.modeChanged)
        #        self._view.modeSelector.currentIndexChanged.connect(self.update)
        self._view.modeCheckBox.clicked.connect(self.toggle_mode)
        if self._view.modeCheckBox.isChecked():
            self._model.set_mode(self._view.modeSelector.currentText())

    def toggle_mode(self):
        if self._view.modeCheckBox.isChecked():
            self._model.set_mode(self._view.modeSelector.currentText())
            self._view.modeSelector.setEnabled(True)
        else:
            self._model.set_mode('None')
            self._view.modeSelector.setEnabled(False)
        self.modeChanged.emit()
        self.update()

    def setupAlpha(self):
        self._view.alphaSpinBox.valueChanged.connect(self._model.set_alpha)
        self._view.alphaCheckBox.clicked.connect(self.toggle_alpha)
        self._view.alphaSpinBox.valueChanged.connect(self.alphaChanged)
        self._view.alphaSpinBox.valueChanged.connect(self.update)
        if self._view.alphaCheckBox.isChecked():
            self._model.set_alpha(self._view.alphaSpinBox.value())

    def toggle_alpha(self):
        if self._view.alphaCheckBox.isChecked():
            self._model.set_alpha(self._view.alphaSpinBox.value())
            self._view.alphaSpinBox.setEnabled(True)
        else:
            self._model.set_alpha(nan)
            self._view.alphaSpinBox.setEnabled(False)
        self.alphaChanged.emit()
        self.update()

    def setupSpot(self):
        self._view.spotSpinBox.valueChanged.connect(self._model.set_spot)
        self._view.spotSpinBox.valueChanged.connect(self.update)
        self._view.spotCheckBox.clicked.connect(self.toggle_spot)
        self._view.spotSpinBox.valueChanged.connect(self.spotChanged)
        if self._view.spotCheckBox.isChecked():
            self._model.set_spot(self._view.spotSpinBox.value())

    def toggle_spot(self):
        if self._view.spotCheckBox.isChecked():
            self._model.set_spot(self._view.spotSpinBox.value())
            self._view.spotSpinBox.setEnabled(True)
        else:
            self._model.set_spot(nan)
            self._view.spotSpinBox.setEnabled(False)
        self.spotChanged.emit()
        self.update()

    def setupSpotSize(self):
        self._view.spotSizeSpinBox.valueChanged.connect(self._model.set_nominal_spotsize)
        self._view.spotSizeSpinBox.valueChanged.connect(self.update)
        self._view.spotSizeCheckBox.clicked.connect(self.toggle_spot_size)
        self._view.spotSizeSpinBox.valueChanged.connect(self.spotSizeChanged)
        if self._view.spotSizeCheckBox.isChecked():
            self._model.set_nominal_spotsize(self._view.spotSizeSpinBox.value())

    def toggle_spot_size(self):
        if self._view.spotSizeCheckBox.isChecked():
            self._model.set_nominal_spotsize(self._view.spotSizeSpinBox.value())
            self._view.spotSizeSpinBox.setEnabled(True)
        else:
            self._model.set_nominal_spotsize(nan)
            self._view.spotSizeSpinBox.setEnabled(False)
        self.spotSizeChanged.emit()
        self.update()

    def setupCondenserAperture(self):
        self._view.condenserApertureSpinBox.valueChanged.connect(self._model.set_nominal_condenser_aperture)
        self._view.condenserApertureCheckBox.clicked.connect(self.toggle_condenser_aperture)
        self._view.condenserApertureSpinBox.valueChanged.connect(self.condenserApertureChanged)
        self._view.condenserApertureSpinBox.valueChanged.connect(self.update)
        if self._view.condenserApertureCheckBox.isChecked():
            self._model.set_nominal_condenser_aperture(self._view.condenserApertureSpinBox.value())

    def toggle_condenser_aperture(self):
        if self._view.condenserApertureCheckBox.isChecked():
            self._model.set_nominal_condenser_aperture(self._view.condenserApertureSpinBox.value())
            self._view.condenserApertureSpinBox.setEnabled(True)
        else:
            self._model.set_nominal_condenser_aperture(nan)
            self._view.condenserApertureSpinBox.setEnabled(False)
        self.condenserApertureChanged.emit()
        self.update()

    def setupConvergenceAngle(self):
        self._view.convergenceAngleSpinBox.valueChanged.connect(self._model.set_nominal_convergence_angle)
        self._view.convergenceAngleCheckBox.clicked.connect(self.toggle_convergence_angle)
        self._view.convergenceAngleSpinBox.valueChanged.connect(self.convergenceAngleChanged)
        self._view.convergenceAngleSpinBox.valueChanged.connect(self.update)
        if self._view.convergenceAngleCheckBox.isChecked():
            self._model.set_nominal_convergence_angle(self._view.convergenceAngleSpinBox.value())

    def toggle_convergence_angle(self):
        if self._view.convergenceAngleCheckBox.isChecked():
            self._model.set_nominal_convergence_angle(self._view.convergenceAngleSpinBox.value())
            self._view.convergenceAngleSpinBox.setEnabled(True)
        else:
            self._model.set_nominal_convergence_angle(nan)
            self._view.convergenceAngleSpinBox.setEnabled(False)
        self.convergenceAngleChanged.emit()
        self.update()

    def setupPrecessionAngle(self):
        self._view.precessionAngleSpinBox.valueChanged.connect(self._model.set_nominal_rocking_angle)
        self._view.precessionAngleCheckBox.clicked.connect(self.toggle_precession_angle)
        self._view.precessionAngleSpinBox.valueChanged.connect(self.rockingAngleChanged)
        self._view.precessionAngleSpinBox.valueChanged.connect(self.update)
        if self._view.precessionAngleCheckBox.isChecked():
            self._model.set_nominal_rocking_angle(self._view.precessionAngleSpinBox.value())

    def toggle_precession_angle(self):
        if self._view.precessionAngleCheckBox.isChecked():
            self._model.set_nominal_rocking_angle(self._view.precessionAngleSpinBox.value())
            self._view.precessionAngleSpinBox.setEnabled(True)
        else:
            self._model.set_nominal_rocking_angle(nan)
            self._view.precessionAngleSpinBox.setEnabled(False)
        self.rockingAngleChanged.emit()
        self.update()

    def setupPrecessionFrequency(self):
        self._view.precessionFrequencySpinBox.valueChanged.connect(self._model.set_rocking_frequency)
        self._view.precessionFrequencyCheckBox.clicked.connect(self.toggle_precession_frequency)
        self._view.precessionFrequencySpinBox.valueChanged.connect(self.rockingFrequencyChanged)
        self._view.precessionFrequencySpinBox.valueChanged.connect(self.update)
        if self._view.precessionFrequencyCheckBox.isChecked():
            self._model.set_rocking_frequency(self._view.precessionFrequencySpinBox.value())

    def toggle_precession_frequency(self):
        if self._view.precessionFrequencyCheckBox.isChecked():
            self._model.set_rocking_frequency(self._view.precessionFrequencySpinBox.value())
            self._view.precessionFrequencySpinBox.setEnabled(True)
        else:
            self._model.set_rocking_frequency(nan)
            self._view.precessionFrequencySpinBox.setEnabled(False)
        self.rockingFrequencyChanged.emit()
        self.update()

    def setupAcquisitionDate(self):
        self._view.acquisitionDate.dateChanged.connect(lambda date: self._model.set_acquisition_date(date.toPyDate()))
        self._view.acquisitionDate.dateChanged.connect(self.acquisitionDateChanged)
        self._view.acquisitionDate.dateChanged.connect(self.update)
        self._view.acquisitionDateCheckBox.clicked.connect(self.toggle_acquisition_date)
        if self._view.acquisitionDateCheckBox.isChecked():
            self._model.set_acquisition_date(self._view.acquisitionDate.date().toPyDate())

    def toggle_acquisition_date(self):
        if self._view.acquisitionDateCheckBox.isChecked():
            self._model.set_acquisition_date(self._view.acquisitionDate.date().toPyDate())
            self._view.acquisitionDate.setEnabled(True)
        else:
            self._model.set_acquisition_date('')
            self._view.acquisitionDate.setEnabled(False)
        self._view.acquisitionDate.dateChanged.connect(self.acquisitionDateChanged)
        self.update()

    def setupScanStep(self):
        self._view.stepXSpinBox.valueChanged.connect(self._model.set_nominal_scan_step_x)
        self._view.stepXSpinBox.valueChanged.connect(self._model.set_scan_step_x)
        self._view.stepYSpinBox.valueChanged.connect(self._model.set_nominal_scan_step_y)
        self._view.stepYSpinBox.valueChanged.connect(self._model.set_scan_step_y)
        self._view.stepGroupBox.clicked.connect(self.toggle_step_size)
        self._view.stepXSpinBox.valueChanged.connect(self.stepSizeXChanged)
        self._view.stepYSpinBox.valueChanged.connect(self.stepSizeYChanged)
        self._view.stepXSpinBox.valueChanged.connect(self.update)
        self._view.stepYSpinBox.valueChanged.connect(self.update)
        if self._view.stepGroupBox.isChecked():
            self._model.set_nominal_scan_step_x(self._view.stepXSpinBox.value())
            self._model.set_nominal_scan_step_y(self._view.stepYSpinBox.value())
            self._model.set_scan_step_x(self._view.stepXSpinBox.value())
            self._model.set_scan_step_y(self._view.stepYSpinBox.value())

    def toggle_step_size(self):
        if self._view.stepGroupBox.isChecked():
            self._model.set_nominal_scan_step_x(self._view.stepXSpinBox.value())
            self._model.set_nominal_scan_step_y(self._view.stepYSpinBox.value())
            self._model.set_scan_step_x(self._view.stepXSpinBox.value())
            self._model.set_scan_step_y(self._view.stepYSpinBox.value())
        else:
            self._model.set_nominal_scan_step_x(nan)
            self._model.set_nominal_scan_step_y(nan)
            self._model.set_scan_step_x(nan)
            self._model.set_scan_step_y(nan)
        self.stepSizeXChanged.emit()
        self.stepSizeYChanged.emit()
        self.update()

    def setupCamera(self):
        self._view.cameraComboBox.currentTextChanged.connect(lambda text: self._model.set_camera(str(text)))
        self._view.cameraComboBox.currentTextChanged.connect(self.cameraChanged)
        self._view.cameraComboBox.currentTextChanged.connect(self.update)
        self._view.cameraCheckBox.clicked.connect(self.toggle_camera)
        if self._view.cameraCheckBox.isChecked():
            self._model.set_camera(str(self._view.cameraComboBox.currentText()))

    def toggle_camera(self):
        if self._view.cameraCheckBox.isChecked():
            self._model.set_camera(str(self._view.cameraComboBox.currentText()))
            self._view.cameraComboBox.setEnabled(True)
        else:
            self._model.set_camera('')
            self._view.cameraComboBox.setEnabled(False)
        self.cameraChanged.emit()
        self.update()

    def setupMicroscopeName(self):
        self._view.microscopeComboBox.currentTextChanged.connect(
            lambda text: self._model.set_microscope(str(text)))
        self._view.microscopeComboBox.currentTextChanged.connect(self.microscopeNameChanged)
        self._view.microscopeComboBox.currentTextChanged.connect(self.update)
        self._view.microscopeCheckBox.clicked.connect(self.toggle_microscope)
        if self._view.microscopeCheckBox.isChecked():
            self._model.set_microscope(str(self._view.microscopeComboBox.currentText()))

    def toggle_microscope(self):
        if self._view.microscopeCheckBox.isChecked():
            self._model.set_microscope(str(self._view.microscopeComboBox.currentText()))
            self._view.microscopeComboBox.setEnabled(True)
        else:
            self._model.set_microscope('')
            self._view.microscopeComboBox.setEnabled(False)
        self.microscopeNameChanged.emit()
        self.update()

    def update(self, *args, **kwargs):
        self._table_model.setDataFrame(self._model.as_dataframe2D())

    def show(self):
        self._view.show()

    def get_view(self):
        return self._view

    def get_model(self):
        return self._model

    def get_table(self):
        return self._table

    def set_table(self, calibrationtable):
        """
        Sets the calibration table of the parameters

        :param calibrationtable: The calibration table
        :type calibrationtable: pd.DataFrame
        :return:
        """
        if not isinstance(calibrationtable, pd.DataFrame):
            raise TypeError(
                'Calibration table must be a pandas.DataFrame object, not {t}'.format(t=type(calibrationtable)))
        self._table = calibrationtable
        self.tableChanged.emit()


class ParametersWindow(QtWidgets.QMainWindow):
    parametersChanged = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(ParametersWindow, self).__init__(*args, **kwargs)

        uic.loadUi(str(Path(__file__).parent / 'source/QTCmib2hspy/parameterswindow.ui'), self)

    #     self.model = Microscope()
    #
    #     self.magnificationSpinBox.valueChanged.connect(self.set_magnification)
    #     self.magnificationSelector.currentTextChanged.connect(self.set_mag_mode)
    #     self.magnificationGroupBox.clicked.connect(self.set_magnification_active)
    #
    #     self.cameraLengthSpinBox.valueChanged.connect(self.set_cameralength)
    #     self.cameraLengthGroupBox.clicked.connect(self.set_cameralength_active)
    #
    #     self.highTensionSpinBox.valueChanged.connect(self.set_acceleration_voltage)
    #     self.highTensionGroupBox.clicked.connect(self.set_acceleration_voltage_active)
    #
    #     self.modeSelector.currentTextChanged.connect(self.set_mode)
    #
    #     self.alphaSpinBox.valueChanged.connect(self.set_alpha)
    #     self.alphaGroupBox.clicked.connect(self.set_alpha_active)
    #
    #     self.spotSpinBox.valueChanged.connect(self.set_spot)
    #     self.spotGroupBox.clicked.connect(self.set_spot_active)
    #
    #     self.condenserApertureSpinBox.valueChanged.connect(self.set_condenser_aperture)
    #     self.condenserApertureGroupBox.clicked.connect(self.set_condenser_aperture_active)
    #
    #     self.convergenceAngleSpinBox.valueChanged.connect(self.set_convergence_angle)
    #     self.convergenceAngleGroupBox.clicked.connect(self.set_convergence_angle_active)
    #
    #     self.spotSizeSpinBox.valueChanged.connect(self.set_spotsize)
    #     self.spotSizeGroupBox.clicked.connect(self.set_spotsize_active)
    #
    #     self.precessionAngleSpinBox.valueChanged.connect(self.set_rocking_angle)
    #     self.precessionAngleGroupBox.clicked.connect(self.set_rocking_angle_active)
    #
    #     self.precessionFrequencySpinBox.valueChanged.connect(self.set_rocking_frequency)
    #     self.precessionFrequencyGroupBox.clicked.connect(self.set_rocking_frequency_active)
    #
    #     self.acquisitionDate.dateChanged.connect(self.set_acquisition_date)
    #     self.acquisitionDateGroupBox.clicked.connect(self.set_acquisition_date_active)
    #
    #     self.stepXSpinBox.valueChanged.connect(self.set_step_x)
    #     self.stepYSpinBox.valueChanged.connect(self.set_step_y)
    #     self.stepGroupBox.clicked.connect(self.set_step_active)
    #
    #     self.table_model = DataFrameModel(parent=self)
    #     self.tableView.setModel(self.table_model)
    #     self.model.updated.connect(self.refresh)
    #
    #     self.refresh()
    #
    # @pyqtSlot()
    # def refresh(self):
    #     self.table_model.setDataFrame(self.model.dataframe2D)


class ConverterModel(QObject):
    dataChanged = pyqtSignal([], [str], [Converter], name="dataChanged")

    def __init__(self):
        super(ConverterModel, self).__init__()
        self.converter = Converter()

    @pyqtSlot(str, name="setDataPath")
    def setDataPath(self, data_path):
        try:
            self.converter.data_path = data_path
        except Exception as e:
            logging.getLogger().error(e)
        self.dataChanged.emit()

    @pyqtSlot(name="resetData")
    def resetData(self):
        self.converter.data_path = None
        self.dataChanged.emit()

    @pyqtSlot(bool, name="loadMIB")
    def loadMIB(self, arg):
        if arg:
            try:
                self.converter.read_mib()
            except Exception as e:
                logging.getLogger().error(e)
            self.dataChanged.emit()

    @pyqtSlot(str, name='loadMIB')
    def loadMIB(self, data_path):
        try:
            self.converter.read_mib(data_path)
        except Exception as e:
            logging.getLogger().error(e)
        self.dataChanged.emit()

    @pyqtSlot(name="loadMIB")
    def loadMIB(self):
        try:
            self.converter.read_mib()
        except Exception as e:
            logging.getLogger().error(e)
        self.dataChanged.emit()

    @pyqtSlot(name='clearData')
    def clearData(self):
        self.converter.data_path = None
        self.dataChanged.emit()

    @pyqtSlot(int, name='rechunkData')
    def rechunkData(self, chunksize):
        try:
            self.converter.rechunk(chunksize)
        except Exception as e:
            logging.getLogger().error(e)
        self.dataChanged.emit()

    @pyqtSlot(int, int, name='reshapeStack')
    def reshapeStack(self, nx, ny):
        try:
            print(nx, ny)
            self.converter.reshape(nx, ny)
        except Exception as e:
            print(e)
            logging.getLogger().error(e)

        self.dataChanged.emit()

    @pyqtSlot(int, name="reshapeStack")
    def reshapeStack(self, nx):
        try:
            self.converter.reshape(nx)
        except Exception as e:
            logging.getLogger().error(e)
        self.dataChanged.emit()


class ConverterView(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(ConverterView, self).__init__(*args, **kwargs)
        uic.loadUi(str(Path(__file__).parent / './source/mib2hspy/mainwindow.ui'), self)
        self.setWindowTitle('mib2hspy converter')
        self.threadpool = QThreadPool()
        self._settings = {}
        self.read_settings()

    def read_settings(self, settings_file_name=str(Path(__file__).parent / 'settings.txt')):
        """
        Read gui settings from a settings file.
        :param settings_file_name: Path to settings file
        :return:
        """
        with open(settings_file_name, 'r') as settings_file:
            lines = settings_file.readlines()
            for line in lines:
                try:
                    key, value = line.split(':', maxsplit=1)
                    key = key.strip()
                    value = value.strip()
                except Exception as e:
                    logging.getLogger().error(e)
                else:
                    self._settings.update({key: value})

    def write_settings(self, settings_file_name=str(Path(__file__).parent / 'settings.txt')):
        """
        Write settings to a settings file.
        :param settings_file_name: Path to settings file
        :return:
        """
        with open(settings_file_name, 'w') as settings_file:
            settings_file.write('SETTINGS\n')
            for key in self._settings:
                settings_file.write('{key}:{value}\n'.format(key=key, value=self._settings[key]))
            settings_file.write('END')

    def set_setting(self, setting, value, write_settings=True):
        """
        Sets a setting to a given value.
        :param setting: The setting to beset
        :param value: The value to set
        :param write_settings: Whether to write the settings to settings file or not
        :type setting: str
        :type value: any
        :type write_settings: bool
        :return:
        """
        self._settings.update({setting: value})
        logging.getLogger().info('Set setting "{setting}" to "{value}"'.format(setting=setting, value=value))
        if write_settings:
            self.write_settings()

    def get_setting(self, setting):
        return self._settings[setting]

    @pyqtSlot(name='browseInputFile', result=str)
    def browseInputFile(self):
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            None,
            "Select data file",
            str(self._settings['default_data_root']),
            "mib Files (*.mib);;All Files (*)",
            options=options)
        return fileName

    @pyqtSlot(name='browseCalibrationFile', result=str)
    def browseCalibrationFile(self):
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            None,
            "Select Calibration file",
            str(Path(self._settings['default_calibration_file']).parent),
            "csv Files (*.csv);;Excel Files (*xlsx);;All Files (*)",
            options=options)
        return fileName


class ConverterController(object):
    default_calibration_file = str(Path(__file__).parent.parent.parent / 'Calibrations.xlsx')

    def __init__(self, view, model):
        """

        :param view:
        :param model:
        :type view: ConverterView
        :type model: ConverterModel
        """

        self._view = view
        self._model = model
        self._parameter_controller = ParameterController(self._view, self._model.converter.microscope_parameters)

        # Setup calibration table signals
        self._view.calibrationPathLineEdit.setText(self.default_calibration_file)
        self.set_calibration_table()
        self._view.calibrationPathLineEdit.returnPressed.connect(self.set_calibration_table)
        self._view.showCalibrationsButton.clicked.connect(lambda: print(self._parameter_controller.get_table()))
        self._view.browseCalibrationFileButton.clicked.connect(
            lambda: self.set_calibration_table(self._view.browseCalibrationFile()))

        self._model.dataChanged.connect(self.update_view)
        self._view.dataPathLineEdit.returnPressed.connect(lambda: self.load_data(self._view.dataPathLineEdit.text()))
        self._view.loadButton.clicked.connect(lambda: self.load_data(self._view.dataPathLineEdit.text()))
        self._view.refreshButton.clicked.connect(self.update_view)
        self._view.printConverterButton.clicked.connect(lambda: print(self._model.converter))
        self._view.browseDataButton.clicked.connect(lambda: self.load_data(self._view.browseInputFile()))
        self._view.reshapeButton.clicked.connect(self.reshape_stack)
        self._view.nXSpinBox.valueChanged.connect(self.update_view)
        self._view.nYSpinBox.valueChanged.connect(self.update_view)
        self._view.applyCalibrationButton.clicked.connect(self.apply_calibrations)
        self._view.rechunkButton.clicked.connect(self.rechunk_data)
        self._view.readDataInfoButton.clicked.connect(self.read_dtype)
        self._view.readDataInfoButton.clicked.connect(self.read_max_value)
        self._view.changeDtypeButton.clicked.connect(self.change_dtype)

        self._view.operatorLineEdit.textChanged.connect(self.update_session_metadata)
        self._view.specimenLineEdit.textChanged.connect(self.update_session_metadata)
        self._view.notesTextEdit.textChanged.connect(self.update_session_metadata)
        self._view.xStage.valueChanged.connect(self.update_stage_metadata)
        self._view.yStage.valueChanged.connect(self.update_stage_metadata)
        self._view.zStage.valueChanged.connect(self.update_stage_metadata)
        self._view.alphaTilt.valueChanged.connect(self.update_stage_metadata)
        self._view.betaTilt.valueChanged.connect(self.update_stage_metadata)
        self._view.rotationHolderCheckBox.clicked.connect(self.update_stage_metadata)
        self._model.dataChanged.connect(self.update_stage_metadata)
        self._model.dataChanged.connect(self.update_session_metadata)

        self._view.writeButton.clicked.connect(self.write)
        for widget in self._view.fileFormatGroupBox.children():
            if isinstance(widget, QtWidgets.QCheckBox): widget.clicked.connect(self.update_write_button)

        handler = QTextEditLogger(widget=self._view.logView)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(handler)

    def load_data(self, path):
        if path is None:
            self._model.converter.data_path = path
        else:
            try:
                self._model.converter.data_path = path
            except Exception as e:
                logging.getLogger().error(e)
            else:
                self._model.loadMIB()
        self.update_reshape(squarify=True)

    def update_reshape(self, squarify=False):
        frames = self._model.converter.frames
        self._view.framesLabel.setText(str(frames))
        self._view.nXSpinBox.setMaximum(frames)
        self._view.nYSpinBox.setMaximum(frames)
        if squarify:
            square_width = sqrt(frames)
            if isclose(square_width % 1, 0):
                self._view.nXSpinBox.setValue(int(square_width))
                self._view.nYSpinBox.setValue(int(square_width))
        if self._view.nXSpinBox.value() * self._view.nYSpinBox.value() != frames:
            self._view.reshapeButton.setEnabled(False)
        else:
            self._view.reshapeButton.setEnabled(True)

    def update_write_button(self):
        if not any([checkbox.isChecked() for checkbox in self._view.fileFormatGroupBox.children() if
                    isinstance(checkbox, QtWidgets.QCheckBox)]):
            self._view.writeButton.setEnabled(False)
        else:
            self._view.writeButton.setEnabled(True)

    def update_view(self):
        self._view.dataPathLineEdit.setText(str(self._model.converter.data_path))
        self._view.signalLabel.setText(str(self._model.converter.data))
        self.update_write_button()

        self._parameter_controller.update()

        # Update metadata and axes manager views
        if self._model.converter.data is not None:
            self._view.axesManagerPlainTextEdit.setPlainText(str(self._model.converter.data.axes_manager))
            populate_1Dtree(self._view.metadataTreeWidget, self._model.converter.data.metadata.as_dictionary(),
                            exclude_patterns=['_'])
            populate_1Dtree(self._view.originalMetadataTreeWidget,
                            self._model.converter.data.original_metadata.as_dictionary(), exclude_patterns=['_'])
        else:
            self._view.axesManagerPlainTextEdit.setPlainText('')
            populate_1Dtree(self._view.metadataTreeWidget, {})
            populate_1Dtree(self._view.originalMetadataTreeWidget, {})

        # Update reshape widgets
        self.update_reshape()

        # Update chunksize label
        if self._model.converter.data is not None:
            self._view.chunksLabel.setText(str(self._model.converter.data.data.chunksize))

    def reshape_stack(self):
        try:
            self._model.converter.reshape(self._view.nXSpinBox.value(), self._view.nYSpinBox.value())
        except Exception as e:
            logging.getLogger().error(e)
        else:
            logging.info('Reshaped stack successfully')
            self._model.dataChanged.emit()

    def apply_calibrations(self):
        logging.info('Applying calibrations')
        try:
            self._model.converter.apply_calibrations()
        except Exception as e:
            logging.getLogger().error(e)
        else:
            logging.info('Applied calibrations successfully')
            self._model.dataChanged.emit()

    def rechunk_data(self):
        try:
            self._model.converter.rechunk(self._view.chunkSpinBox.value())
        except Exception as e:
            logging.getLogger().error(e)
        else:
            logging.info('Rechunked stack successfully')
            self._model.dataChanged.emit()

    def change_dtype(self):
        try:
            self._model.converter.downsample(self._view.dtypeComboBox.currentText())
        except Exception as e:
            logging.getLogger().error(e)
        else:
            logging.info('Changed data dtype successfully')
            self._model.dataChanged.emit()

    def read_max_value(self):
        try:
            self._view.maxValueLabel.setText(str(self._model.converter.get_max_value()))
        except Exception as e:
            logging.getLogger().error(e)
        else:
            logging.info('Maximum value in dataset read successfully')

    def read_dtype(self):
        try:
            self._view.dtypeLabel.setText(str(self._model.converter.data.data.dtype))
        except Exception as e:
            logging.getLogger().error(e)
        else:
            logging.info('Data dtype read successfully')

    def update_stage_metadata(self):
        if self._model.converter.data is not None:
            dictionary = {'Acquisition_instrument': {'TEM': {'Stage': {
                'X': '{x} um'.format(x=self._view.xStage.value()),
                'Y': '{y} um'.format(y=self._view.yStage.value()),
                'Z': '{z} um'.format(z=self._view.zStage.value()),
                'Alpha': '{a} deg'.format(a=self._view.alphaTilt.value()),
                'Beta': '{b} deg'.format(b=self._view.betaTilt.value()),
                'Rotation': '{r}'.format(r=self._view.rotationHolderCheckBox.isChecked())
            }}}}
            self._model.converter.data.metadata.add_dictionary(dictionary)
            self.update_view()

    def update_session_metadata(self):
        if self._model.converter.data is not None:
            dictionary = {'General': {'Session': {
                'Operator': self._view.operatorLineEdit.text(),
                'Specimen': self._view.specimenLineEdit.text(),
                'Notes': self._view.notesTextEdit.toPlainText()
            }}}
            self._model.converter.data.metadata.add_dictionary(dictionary)
            self.update_view()

    def write(self):
        file_formats = []
        for widget in self._view.fileFormatGroupBox.children():
            if isinstance(widget, QtWidgets.QCheckBox):
                if widget.isChecked():
                    file_formats.append(widget.text())

        for file_format in file_formats:
            logging.getLogger().info('Writing "{format}" data'.format(format=file_format))
            try:
                if file_format in ['.jpg', '.png', '.tif', '.tiff']:
                    inav = [0, 0]
                else:
                    inav = None
                self._model.converter.write(file_format, overwrite=self._view.overwriteCheckBox.isChecked(), inav=inav)
            except Exception as e:
                logging.getLogger().error(e, exc_info=sys.exc_info())
            else:
                logging.getLogger().info('Data written successfully!')

    def set_calibration_table(self, path=None):
        try:
            if path is None:
                path = self._view.calibrationPathLineEdit.text()
            path = Path(path)

            calibration_table = pd.read_excel(str(path), engine='openpyxl')
            # self._model.converter.calibration_table = pd.read_excel(str(Path(self._view.calibrationPathLineEdit.text())), engine='openpyxl')
            self._parameter_controller.set_table(calibration_table)
        except Exception as e:
            logging.error(e)


def populate_1Dtree(tree, dictionary, header='Value', exclude_patterns=[]):
    """
    Populate the tree in a QTreeWidget

    :param tree: The tree to populate
    :param dictionary: The dictionary to populate tree with
    :param header: The header of the tree
    :param exclude_patterns: List of key prefixes to exlude
    :type tree: QtWidgets.QTreeWidget
    :type dictionary: dict
    :type header: str
    :type exclude_patterns: list
    :return:
    """
    tree.clear()
    tree.setColumnCount(1)
    tree.setHeaderLabels([header])
    tree.setItemsExpandable(True)

    if not isinstance(dictionary, dict):
        raise TypeError('Can only use dictionaries to populate trees')
    items = dict2treeItems(tree, dictionary, exclude_patterns=exclude_patterns)
    tree.expandAll()
    # tree.resizeColumnToContents(0)


def dict2treeItems(parent, dictionary, exclude_patterns=[]):
    """

    :param parent: The parent tree to populate
    :param dictionary: The dictionary to use to populate the parent tree
    :param exclude_patterns: List of key patterns to exclude.
    :type parent: Unioun[QtWidgets.QTreeWidget, QtWidgets.QTreeWidgetItem]
    :type dictionary: dict
    :type exclude_patterns: list
    :return:
    """
    items = []
    for parameter in dictionary:
        skip = False
        if isinstance(parameter, str):
            if parameter.startswith(tuple(exclude_patterns)):
                skip = True

        if not skip:
            item = QtWidgets.QTreeWidgetItem(parent, [parameter])
            value = dictionary[parameter]
            if isinstance(value, dict):
                children = dict2treeItems(item, value)
                for child in children:
                    item.addChild(child)
            else:
                child = QtWidgets.QTreeWidgetItem(item, [str(value)])
                # item.addChild(child)
            items.append(item)
    return items


def run_gui(log_level=logging.INFO):
    main(r'./mib2hspy/gui/debug.log', log_level=log_level)


def main(logfile=None, log_level=logging.INFO):
    """
    Intialize a standard GUI with logging
    :param logfile: path to output log (debug) file. DEfault is None, in which case a new timestamped logfile will be created under ./logs/
    :return:
    """
    # Create debug file if not provided
    if logfile is None:
        now = datetime.now()
        debug_file = Path('./logs/{stamp}_debug.log'.format(stamp=now.strftime('%Y-%m-%d-%H-%M-%S')))
    else:
        debug_file = Path(logfile)
    debug_file.parent.mkdir(parents=True, exist_ok=True)
    with open(debug_file, 'w') as f:
        f.close()
    print(debug_file.absolute())

    # Setup logging
    logformat = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fileHandler = logging.FileHandler(str(debug_file))
    fileHandler.setFormatter(logformat)
    logging.getLogger().addHandler(fileHandler)
    logging.getLogger().setLevel(log_level)
    logging.getLogger().addHandler((logging.StreamHandler(sys.stdout)))

    myqui = QtWidgets.QApplication(sys.argv)
    window = ConverterView()
    window.show()

    model = ConverterModel()
    controller = ConverterController(window, model)

    sys.exit(myqui.exec_())


if __name__ == '__main__':
    main(log_level=logging.INFO)
