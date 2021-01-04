import logging
import sys
from datetime import datetime
from pathlib import Path
from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThreadPool, QObject
import pyxem as pxm
import pandas as pd
from numpy import nan

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import time
# from .guiTools import tools
from mib2hspy.gui.guiTools import Worker, QTextEditLogger, DataFrameModel
from mib2hspy.Tools import MedipixHDRcontent, MedipixHDRfield, Microscope


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


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi(str(Path(__file__).parent / './source/QTCmib2hspy/mainwindow.ui'), self)
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
        # options |= QtWidgets.QFileDialog.DontUseNativeDialog
        # fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
        #     None,
        #     "Select file",
        #     str(self.settings['default_root_folder']),
        #     "mib Files (*.mib);;hspy Files (*.hspy);;All Files (*)",
        #     options=options)
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            None,
            "Select file",
            str(self._settings['default_data_root']),
            "mib Files (*.mib);;hspy Files (*.hspy);;All Files (*)",
            options=options)
        return fileName

    @pyqtSlot(str, name='browseInputFile', result=str)
    def browseInputFile(self, root=None):
        options = QtWidgets.QFileDialog.Options()
        if root is None:
            fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
                None,
                "Select file",
                str(self._settings['default_data_root']),
                "mib Files (*.mib);;hspy Files (*.hspy);;All Files (*)",
                options=options)
        else:
            fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
                None,
                "Select file",
                str(root),
                "mib Files (*.mib);;hspy Files (*.hspy);;All Files (*)",
                options=options)
        return fileName

    @pyqtSlot(name='browseCalibrationFile', result=str)
    def browseCalibrationFile(self):
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            None,
            "Select file",
            str(Path(self._settings['default_calibration_file']).parent),
            "csv Files (*.csv);;Excel Files (*xlsx);;All Files (*)",
            options=options)
        return fileName


class NotesWindow(QtWidgets.QMainWindow):
    textChanged = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(NotesWindow, self).__init__(*args, **kwargs)

        # Load ui file
        uic.loadUi(str(Path(__file__).parent / 'source/QTCmib2hspy/noteswindow.ui'), self)
        self.setWindowTitle('Notes')
        self.storeButton.clicked.connect(self.setNotes)
        self.textEdit.textChanged.connect(self.refresh)
        self.textChanged.connect(self.refresh)
        self._text = ''

    @pyqtSlot()
    def refresh(self):
        if self._text != self.textEdit.toPlainText():
            self.statusIndicator.setInactive()
        else:
            self.statusIndicator.setActive()

    @pyqtSlot()
    def setNotes(self):
        self._text = self.textEdit.toPlainText()
        self.textChanged.emit()

    def get_text(self):
        return self._text


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

    def __init__(self, view, model):
        """
        Create a controller for parameter view and model
        :param view: The window to control the parameters
        :param model: The model to store the parameters in
        :type view: ParametersWindow
        :type model: Microscope
        """
        super(ParameterController, self).__init__()
        self._view = view
        self._model = model

        self._table_model = DataFrameModel(parent=self._view)
        self._view.tableView.setModel(self._table_model)

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

    def setupMagnification(self):
        if self._view.magnificationCheckBox.isChecked():
            self._model.set_nominal_magnification(self._view.magnificationSpinBox.value())
            self._model.set_mag_mode(self._view.magnificationSelector.currentText())
        self._view.magnificationSpinBox.valueChanged.connect(self._model.set_nominal_magnification)
        self._view.magnificationSpinBox.valueChanged.connect(lambda v: self.update())
        self._view.magnificationSelector.currentTextChanged.connect(self._model.set_mag_mode)
        self._view.magnificationSelector.currentTextChanged.connect(lambda v: self.update())
        self._view.magnificationCheckBox.clicked.connect(self.toggle_magnification)
        self._view.magnificationSpinBox.valueChanged.connect(self.magnificationChanged)
        self._view.magnificationSelector.currentTextChanged.connect(self.magModeChanged)

    def toggle_magnification(self):
        if self._view.magnificationCheckBox.isChecked():
            self._model.set_nominal_magnification(self._view.magnificationSpinBox.value())
            self._model.set_mag_mode(self._view.magnificationSelector.currentText())
        else:
            self._model.set_nominal_magnification(nan)
            self._model.set_mag_mode('')
        self.magnificationChanged.emit()
        self.magModeChanged.emit()
        self.update()

    def setupCameralength(self):
        self._view.cameraLengthSpinBox.valueChanged.connect(self._model.set_nominal_cameralength)
        self._view.cameraLengthSpinBox.valueChanged.connect(lambda v: self.update())
        self._view.cameraLengthCheckBox.clicked.connect(self.toggle_cameralength)
        self._view.cameraLengthSpinBox.valueChanged.connect(self.cameralengthChanged)
        if self._view.cameraLengthCheckBox.isChecked():
            self._model.set_nominal_cameralength(self._view.cameraLengthSpinBox.value())

    def toggle_cameralength(self):
        if self._view.cameraLengthCheckBox.isChecked():
            self._model.set_nominal_cameralength(self._view.cameraLengthSpinBox.value())
        else:
            self._model.set_nominal_cameralength(nan)
        self.cameralengthChanged.emit()
        self.update()

    def setupAccelerationVoltage(self):
        self._view.highTensionSpinBox.valueChanged.connect(
            lambda x: self._model.set_acceleration_voltage(self._view.highTensionSpinBox.value()))
        self._view.highTensionSpinBox.valueChanged.connect(self.update)
        self._view.highTensionCheckBox.clicked.connect(self.toggle_acceleration_voltage)
        self._view.highTensionSpinBox.valueChanged.connect(self.accelerationVoltageChanged)
        if self._view.highTensionCheckBox.isChecked():
            self._model.set_acceleration_voltage(self._view.highTensionSpinBox.value())

    def toggle_acceleration_voltage(self):
        if self._view.highTensionCheckBox.isChecked():
            self._model.set_acceleration_voltage(self._view.highTensionSpinBox.value())
        else:
            self._model.set_acceleration_voltage(nan)
        self.accelerationVoltageChanged.emit()
        self.update()

    def setupMode(self):
        self._view.modeSelector.currentTextChanged.connect(self._model.set_mode)
        self._view.modeSelector.currentTextChanged.connect(self.update)
        self._view.modeSelector.currentIndexChanged.connect(self.modeChanged)
        self._view.modeCheckBox.clicked.connect(self.toggle_mode)
        if self._view.modeCheckBox.isChecked():
            self._model.set_mode(self._view.modeSelector.currentText())

    def toggle_mode(self):
        if self._view.modeCheckBox.isChecked():
            self._model.set_mode(self._view.modeSelector.currentText())
        else:
            self._model.set_mode('None')
        self.modeChanged.emit()
        self.update()

    def setupAlpha(self):
        self._view.alphaSpinBox.valueChanged.connect(self._model.set_alpha)
        self._view.alphaSpinBox.valueChanged.connect(self.update)
        self._view.alphaCheckBox.clicked.connect(self.toggle_alpha)
        self._view.alphaSpinBox.valueChanged.connect(self.alphaChanged)
        if self._view.alphaCheckBox.isChecked():
            self._model.set_alpha(self._view.alphaSpinBox.value())

    def toggle_alpha(self):
        if self._view.alphaCheckBox.isChecked():
            self._model.set_alpha(self._view.alphaSpinBox.value())
        else:
            self._model.set_alpha(nan)
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
        else:
            self._model.set_spot(nan)
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
        else:
            self._model.set_nominal_spotsize(nan)
        self.spotSizeChanged.emit()
        self.update()

    def setupCondenserAperture(self):
        self._view.condenserApertureSpinBox.valueChanged.connect(self._model.set_nominal_condenser_aperture)
        self._view.condenserApertureSpinBox.valueChanged.connect(self.update)
        self._view.condenserApertureCheckBox.clicked.connect(self.toggle_condenser_aperture)
        self._view.condenserApertureSpinBox.valueChanged.connect(self.condenserApertureChanged)
        if self._view.condenserApertureCheckBox.isChecked():
            self._model.set_nominal_condenser_aperture(self._view.condenserApertureSpinBox.value())

    def toggle_condenser_aperture(self):
        if self._view.condenserApertureCheckBox.isChecked():
            self._model.set_nominal_condenser_aperture(self._view.condenserApertureSpinBox.value())
        else:
            self._model.set_nominal_condenser_aperture(nan)
        self.condenserApertureChanged.emit()
        self.update()

    def setupConvergenceAngle(self):
        self._view.convergenceAngleSpinBox.valueChanged.connect(self._model.set_nominal_convergence_angle)
        self._view.convergenceAngleSpinBox.valueChanged.connect(self.update)
        self._view.convergenceAngleCheckBox.clicked.connect(self.toggle_convergence_angle)
        self._view.convergenceAngleSpinBox.valueChanged.connect(self.convergenceAngleChanged)
        if self._view.convergenceAngleCheckBox.isChecked():
            self._model.set_nominal_convergence_angle(self._view.convergenceAngleSpinBox.value())

    def toggle_convergence_angle(self):
        if self._view.convergenceAngleCheckBox.isChecked():
            self._model.set_nominal_convergence_angle(self._view.convergenceAngleSpinBox.value())
        else:
            self._model.set_nominal_convergence_angle(nan)
        self.convergenceAngleChanged.emit()
        self.update()

    def setupPrecessionAngle(self):
        self._view.precessionAngleSpinBox.valueChanged.connect(self._model.set_nominal_rocking_angle)
        self._view.precessionAngleSpinBox.valueChanged.connect(self.update)
        self._view.precessionAngleCheckBox.clicked.connect(self.toggle_precession_angle)
        self._view.precessionAngleSpinBox.valueChanged.connect(self.rockingAngleChanged)
        if self._view.precessionAngleCheckBox.isChecked():
            self._model.set_nominal_rocking_angle(self._view.precessionAngleSpinBox.value())

    def toggle_precession_angle(self):
        if self._view.precessionAngleCheckBox.isChecked():
            self._model.set_nominal_rocking_angle(self._view.precessionAngleSpinBox.value())
        else:
            self._model.set_nominal_rocking_angle(nan)
        self.rockingAngleChanged.emit()
        self.update()

    def setupPrecessionFrequency(self):
        self._view.precessionFrequencySpinBox.valueChanged.connect(self._model.set_rocking_frequency)
        self._view.precessionFrequencySpinBox.valueChanged.connect(self.update)
        self._view.precessionFrequencyCheckBox.clicked.connect(self.toggle_precession_frequency)
        self._view.precessionFrequencySpinBox.valueChanged.connect(self.rockingFrequencyChanged)
        if self._view.precessionFrequencyCheckBox.isChecked():
            self._model.set_rocking_frequency(self._view.precessionFrequencySpinBox.value())

    def toggle_precession_frequency(self):
        if self._view.precessionFrequencyCheckBox.isChecked():
            self._model.set_rocking_frequency(self._view.precessionFrequencySpinBox.value())
        else:
            self._model.set_rocking_frequency(nan)
        self.rockingFrequencyChanged.emit()
        self.update()

    def setupAcquisitionDate(self):
        self._view.acquisitionDate.dateChanged.connect(lambda date: self._model.set_acquisition_date(date.toPyDate()))
        self._view.acquisitionDate.dateChanged.connect(self.update)
        self._view.acquisitionDateCheckBox.clicked.connect(self.toggle_acquisition_date)
        if self._view.acquisitionDateCheckBox.isChecked():
            self._model.set_acquisition_date(self._view.acquisitionDate.date().toPyDate())

    def toggle_acquisition_date(self):
        if self._view.acquisitionDateCheckBox.isChecked():
            self._model.set_acquisition_date(self._view.acquisitionDate.date().toPyDate())
        else:
            self._model.set_acquisition_date('')
        self.update()

    def setupScanStep(self):
        self._view.stepXSpinBox.valueChanged.connect(self._model.set_nominal_scan_step_x)
        self._view.stepXSpinBox.valueChanged.connect(self.update)
        self._view.stepYSpinBox.valueChanged.connect(self._model.set_nominal_scan_step_y)
        self._view.stepYSpinBox.valueChanged.connect(self.update)
        self._view.stepGroupBox.clicked.connect(self.toggle_step_size)
        self._view.stepXSpinBox.valueChanged.connect(self.stepSizeXChanged)
        self._view.stepYSpinBox.valueChanged.connect(self.stepSizeYChanged)
        if self._view.stepGroupBox.isChecked():
            self._model.set_nominal_scan_step_x(self._view.stepXSpinBox.value())
            self._model.set_nominal_scan_step_y(self._view.stepYSpinBox.value())

    def toggle_step_size(self):
        if self._view.stepGroupBox.isChecked():
            self._model.set_nominal_scan_step_x(self._view.stepXSpinBox.value())
            self._model.set_nominal_scan_step_y(self._view.stepYSpinBox.value())
        else:
            self._model.set_nominal_scan_step_x(nan)
            self._model.set_nominal_scan_step_y(nan)
        self.stepSizeXChanged.emit()
        self.stepSizeYChanged.emit()
        self.update()

    def setupCamera(self):
        self._view.cameraComboBox.currentTextChanged.connect(lambda text: self._model.set_camera(str(text)))
        self._view.cameraComboBox.currentTextChanged.connect(self.update)
        self._view.cameraComboBox.currentTextChanged.connect(self.cameraChanged)
        self._view.cameraCheckBox.clicked.connect(self.toggle_camera)
        if self._view.cameraCheckBox.isChecked():
            self._model.set_camera(str(self._view.cameraComboBox.currentText()))

    def toggle_camera(self):
        if self._view.cameraCheckBox.isChecked():
            self._model.set_camera(str(self._view.cameraComboBox.currentText()))
        else:
            self._model.set_camera('')
        self.cameraChanged.emit()
        self.update()

    def setupMicroscopeName(self):
        self._view.microscopeComboBox.currentTextChanged.connect(
            lambda text: self._model.set_microscope_name(str(text)))
        self._view.microscopeComboBox.currentTextChanged.connect(self.update)
        self._view.microscopeComboBox.currentTextChanged.connect(self.microscopeNameChanged)
        self._view.microscopeCheckBox.clicked.connect(self.toggle_microscope)
        if self._view.microscopeCheckBox.isChecked():
            self._model.set_microscope_name(str(self._view.microscopeComboBox.currentText()))

    def toggle_microscope(self):
        if self._view.microscopeCheckBox.isChecked():
            self._model.set_microscope_name(str(self._view.microscopeComboBox.currentText()))
        else:
            self._model.set_microscope_name('')
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


class mib2hspyModel(QObject):
    filenameChanged = pyqtSignal([], [str], name='filenameChanged')
    dataLoaded = pyqtSignal([], [int], name='dataLoaded')
    dataCleared = pyqtSignal(name='dataCleared')
    headerLoaded = pyqtSignal([], [int], name='headerLoaded')
    headerCleared = pyqtSignal(name='headerCleared')
    calibrationLoaded = pyqtSignal([], [int], name='calibrationLoaded')
    calibrationCleared = pyqtSignal([], [int], name='calibrationCleared')

    def __init__(self):
        super(mib2hspyModel, self).__init__()
        self.filename = None
        self.data = None
        self.hdr = MedipixHDRcontent('.')
        self.calibrationfile = None

    def set_filename(self, filename):
        """
        Sets the filename of the model
        :param filename: The path to the data file to use
        :type filename: str
        :type filename: Path
        :return:
        """
        if not isinstance(filename, (str, Path)):
            raise TypeError()
        filename = Path(filename)
        if not filename.exists():
            raise FileExistsError()
        if not filename.suffix == '.mib':
            raise ValueError()
        self.filename = filename
        self.filenameChanged.emit()
        self.filenameChanged[str].emit(str(self.filename))

    def load_file(self, filename=None):
        """
        Loads a datafile.
        :param filename: The path to the data file to be used. Optional. Default is `None`, and then the preset filename will be used.
        :type filename: str
        :type filename: Path
        :type filename: NoneType
        :return:
        """
        if filename is not None:
            self.set_filename(filename)

        try:
            if self.filename is not None:
                self.data = pxm.load_mib(str(self.filename))
                self.data_array = self.data.data
                self.dataLoaded.emit()
                print(self.data)
            else:
                logging.getLogger().info('No filename set!')
        except Exception as e:
            logging.getLogger().error(e)

    def load_hdr(self):
        """
        Load a .hdr file. Can only be used if the filename of the .mib file is already set.
        :return:
        """
        if self.filename is None:
            raise ValueError()
        else:
            filename = Path(self.filename).with_suffix('.hdr')
            self.hdr.set_filename(filename)
        try:
            self.hdr.load_hdr()
            logging.info('Loaded HDR file:\n{self.hdr}'.format(self=self))
        except FileNotFoundError as e:
            self.hdr.clear()
            logging.error(e)
        else:
            self.headerLoaded.emit()

    def load_calibrationfile(self, filename):
        filename = Path(filename)
        if not filename.exists():
            raise FileExistsError
        if filename.suffix == '.csv':
            self.calibrationfile = pd.read_csv(filename)
            self.calibrationLoaded.emit()
        elif filename.suffix == '.xlsx':
            self.calibrationfile = pd.read_excel(filename, engine='openpyxl')
            self.calibrationLoaded.emit()
        else:
            self.calibrationfile = None
            self.calibrationCleared.emit()
            raise ValueError('Can only use ".csv" files as calibration files')

    def clear_data(self):
        """
        Clears the data and header contents.
        :return:
        """
        self.data = None
        self.hdr.clear()
        self.calibrationfile = None

        self.dataCleared.emit()
        self.headerCleared.emit()
        self.calibrationCleared.emit()

        logging.getLogger().info(
            'Cleared data:\ndata: {self.data!r}\nHeader: {self.hdr!r}\nCalibration: {self.calibrationfile!r}'.format(
                self=self))


class mib2hspyController(object):

    def __init__(self, view, model=None, notes_window=None, parameters_controller=None):
        """
        Create controller for the mib2hspy gui
        :param view: The main gui window.
        :type view: MainWindow
        :param model: The model to control.
        :type model: mib2hspyModel
        :param notes_window: The notes subwindow
        :type notes_window: NotesWindow
        :param parameters_controller: The controller for parameters
        :type parameters_window: ParameterController
        """
        self._view = view
        # self._notes_view = notes_window
        self._parameter_controller = parameters_controller
        self._model = model

        self.setupLogging()
        self.setupInputFileSignals()
        self.setupCalibrationFileSignals()
        self.setupSettingsSignals()

        self._model.headerLoaded.connect(lambda: self.set_scan_size_from_header())
        self._model.calibrationLoaded.connect(lambda: self.calibrate())
        self._view.writeFileButton.clicked.connect(self.write_data)
        # self._view.actionNotes.triggered.connect(lambda: self._notes_view.show())
        self._view.actionAcquisition_parameters.triggered.connect(lambda: self._parameter_controller.show())

        self._view.vbfPushButton.clicked.connect(self.show_vbf)

    def setupLogging(self):
        """
        Sets up logging for the GUI
        :return:
        """
        handler = QTextEditLogger(widget=self._view.logView)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(handler)

    def setupInputFileSignals(self):
        """
        Setup the input file signals of the GUI
        :return:
        """
        # self._view.browseInputFileButton.clicked.connect(
        #    lambda: self._view.inputFilePathField.setText(self._view.browseInputFile()))
        self._view.browseInputFileButton.clicked.connect(lambda: self.browse_input_file())
        self._view.loadInputFileButton.clicked.connect(self.load_data)
        self._model.dataLoaded.connect(self.update_view)
        self._model.dataLoaded.connect(self._model.load_hdr)
        self._model.headerLoaded.connect(lambda: self._view.headerStatusIndicator.setActive())
        self._model.headerLoaded.connect(lambda: self.update_view())
        self._model.dataCleared.connect(lambda: self._view.fileStatusIndicator.setInactive())
        self._model.headerCleared.connect(lambda: self._view.headerStatusIndicator.setInactive())
        self._model.dataCleared.connect(lambda: self.update_view())
        self._model.headerCleared.connect(lambda: self.update_view())
        self._view.clearPushButton.clicked.connect(self.clear)
        self._view.readFileInfoButton.clicked.connect(self.show_file_info)

    def browse_input_file(self):
        if self._model.filename is None:
            filename = self._view.browseInputFile()
        else:
            filename = self._view.browseInputFile(str(Path(self._model.filename).parent))
        self._view.inputFilePathField.setText(filename)

    def setupCalibrationFileSignals(self):
        self._view.browseCalibrationButton.clicked.connect(
            lambda: self._view.calibrationFilePathField.setText(self._view.browseCalibrationFile()))
        self._view.loadCalibrationButton.clicked.connect(
            lambda: self._model.load_calibrationfile(self._view.calibrationFilePathField.text()))
        self._model.calibrationLoaded.connect(self.update_view)
        self._model.calibrationCleared.connect(self.update_view)
        self._model.calibrationLoaded.connect(lambda: self._view.calibrationStatusIndicator.setActive())
        self._model.calibrationCleared.connect(lambda: self._view.calibrationStatusIndicator.setInactive())

        # self._parameter_controller.magModeChanged.connect(self.calibrate)
        self._parameter_controller.modeChanged.connect(self.calibrate)
        self._parameter_controller.alphaChanged.connect(self.calibrate)
        self._parameter_controller.accelerationVoltageChanged.connect(self.calibrate)
        self._parameter_controller.magnificationChanged.connect(self.calibrate_magnification)
        self._parameter_controller.magModeChanged.connect(self.calibrate_magnification)
        self._parameter_controller.cameralengthChanged.connect(self.calibrate_cameralength)
        # self._parameter_controller.spotChanged.connect(self.calibrate_spotsize)
        self._parameter_controller.spotSizeChanged.connect(self.calibrate_spotsize)
        self._parameter_controller.condenserApertureChanged.connect(self.calibrate_condenser_aperture)
        self._parameter_controller.convergenceAngleChanged.connect(self.calibrate_convergence_angle)
        self._parameter_controller.rockingAngleChanged.connect(self.calibrate_rocking_angle)
        # self._parameter_controller.rockingFrequencyChanged.connect(self.calibrate)
        self._parameter_controller.stepSizeXChanged.connect(self.calibrate_scan_step_x)
        self._parameter_controller.stepSizeYChanged.connect(self.calibrate_scan_step_y)
        self._parameter_controller.cameraChanged.connect(self.calibrate)
        self._parameter_controller.microscopeNameChanged.connect(self.calibrate)

        self._view.useCalibrationFileRadioButton.clicked.connect(self.calibrate)
        self._view.useManualCalibrationRadioButton.clicked.connect(self.calibrate)
        self._view.stepSizeXSpinBox.valueChanged.connect(self.calibrate_scan_step_x)
        self._view.stepSizeYSpinBox.valueChanged.connect(self.calibrate_scan_step_y)
        # self._view.scaleSpinBox.valueChanged.connect(self.calibrate_)
        # self._view.scaleSelector.currentIndexChanged.connect(self.calibrate_)
        self._view.rockingAngleSpinBox.valueChanged.connect(self.calibrate_rocking_angle)
        self._view.spotSizeSpinBox.valueChanged.connect(self.calibrate_spotsize)
        self._view.cameraLengthSpinBox.valueChanged.connect(self.calibrate_cameralength)
        self._view.magnificationSpinBox.valueChanged.connect(self.calibrate_magnification)

        self._view.printCalibrationFileButton.clicked.connect(lambda: print(self._model.calibrationfile))

    def setupSettingsSignals(self):
        self._view.actionSettings.triggered.connect(self.open_settings_dialog)
        try:
            self._view.calibrationFilePathField.setText(self._view.get_setting('default_calibration_file'))
            self._model.load_calibrationfile(self._view.get_setting('default_calibration_file'))
        except Exception as e:
            logging.getLogger().error(e)
            logging.getLogger().info('Could not load default calibration file. No calibration file loaded.')

    def open_settings_dialog(self):
        logging.getLogger().info('Opening settings dialog')
        dialog = SettingsDialog(self._view)
        dialog.dataPathField.setText(self._view.get_setting('default_data_root'))
        dialog.calibrationPathField.setText(self._view.get_setting('default_calibration_file'))
        if dialog.exec_():
            data_path = Path(dialog.dataPathField.text())
            calibration_path = Path(dialog.calibrationPathField.text())

            if data_path.is_dir():
                self._view.set_setting('default_data_root', str(data_path))
            else:
                logging.getLogger().info(
                    'Default data root {data_path!r} is invalid, will continue to use {setting!r}'.format(
                        data_path=data_path, setting=self._view.get_setting('default_data_root')))
            if calibration_path.suffix in ['.csv', '.xlsx'] and calibration_path.exists():
                self._view.set_setting('default_calibration_file', str(calibration_path))
                self._view.calibrationFilePathField.setText(str(calibration_path))
                self._model.load_calibrationfile(self._view.calibrationFilePathField.text())
            else:
                logging.getLogger().info(
                    'Calibration file path {calibration_path!r} is invalid, will continue to use {setting!r}'.format(
                        calibration_path=calibration_path, setting=self._view.get_setting('default_calibration_file')))
        else:
            logging.getLogger().info('Did not change settings')

    def show_file_info(self):
        if self._model.data is not None:
            self._view.bitModeIndicator.setText(str(self._model.data.data.dtype))
            self._view.maxValueIndicator.setText(str(self.get_max_value()))

    def get_max_value(self):
        if self._model.data is not None:
            # self._model.data.compute()
            max_value = self._model.data.max(axis=[0, 1, 2])
            return int(max_value.data[0])
        else:
            return nan

    def show_vbf(self):
        signal, chunks = self.prepare_data(update_indicators=False)
        self.generate_vbf(signal, save=False)
        del signal

    def calibrate(self):
        """
        Sets the calibrated values of the acquisition parameters
        :return:
        """
        self.calibrate_spotsize()
        self.calibrate_cameralength()
        self.calibrate_magnification()
        self.calibrate_scan_step_x()
        self.calibrate_scan_step_x()
        self.calibrate_condenser_aperture()
        self.calibrate_convergence_angle()
        self.calibrate_rocking_angle()

    def calibrate_cameralength(self):
        """
        Set the calibrated value of the cameralength
        :return:
        """
        self._parameter_controller.get_model().cameralength.set_value(self.get_cameralength_calibration())
        self._parameter_controller.update()

    def calibrate_magnification(self):
        """
        Set the calibrated value of the magnification
        :return:
        """
        self._parameter_controller.get_model().magnification.set_value(self.get_magnification_calibration())
        self._parameter_controller.update()

    def calibrate_rocking_angle(self):
        """
        Set the calibrated value of the rocking(precession) angle.
        :return:
        """
        self._parameter_controller.get_model().rocking_angle.set_value(self.get_rocking_angle_calibration())
        self._parameter_controller.update()

    def calibrate_scan_step_x(self):
        """
        Set the calibrated value of the scan step in x-direction
        :return:
        """
        self._parameter_controller.get_model().scan_step_x.set_value(self.get_x_scan_calibration())
        self._parameter_controller.update()

    def calibrate_scan_step_y(self):
        """
        Set the calibrated value of the scan step in y-direction
        :return:
        """
        self._parameter_controller.get_model().scan_step_y.set_value(self.get_y_scan_calibration())
        self._parameter_controller.update()

    def calibrate_condenser_aperture(self):
        """
        Set the calibrated value of the condenser aperture size
        :return:
        """
        self._parameter_controller.get_model().condenser_aperture.set_value(self.get_condenser_aperture_calibration())
        self._parameter_controller.update()

    def calibrate_convergence_angle(self):
        """
        Set the calibrated value of the convergence angle.
        :return:
        """
        self._parameter_controller.get_model().convergence_angle.set_value(self.get_convergence_angle_calibration())
        self._parameter_controller.update()

    def calibrate_spotsize(self):
        """
        Set the calibrated value of the spotsize. NB! This will not be a good(exact) calibration for individual experiments!!
        :return:
        """
        self._parameter_controller.get_model().spotsize.set_value(self.get_spotsize_calibration())
        self._parameter_controller.update()

    def get_calibration(self, name, query, base_query=None):
        """
        Find a calibration of `name` in the calibration file matching a query.

        The query is passed to pandas.DataFrame.query(), and should be on the form "`<column_name> == <search_value> & ...", for instance "`Nominal Camera Length (cm)` == <search_value> & ...".

        :param name: The name of the calibration value to extract
        :type name: str
        :param query: The query to perform to filter the dataframe
        :type query: str
        :param base_query: The base query to add to the specified query. Default is None, in which case a query for "`Acceleration Voltage (V)` == {} & `Camera`== {} & `Microscope`=={}" will be added.
        :type base_query: Union[NoneType, str]
        :return: Returns nan if no calibration is found and the content of the last entry in the requested column otherwise.
        """
        if base_query is None:
            parameters = self._parameter_controller.get_model()
            base_query = "`Acceleration Voltage (V)` == {parameters.acceleration_voltage.value} & `Camera`== '{parameters.camera.value}' & `Microscope`== '{parameters.microscope_name.value}'".format(
                parameters=parameters)
        query = '{base} & {query}'.format(base=base_query, query=query)

        if self._model.calibrationfile is None:
            return nan
        try:
            valid_calibration = self._model.calibrationfile.query(query)
        except Exception as e:
            logging.getLogger().error(e)
            valid_calibration = nan
        else:
            valid_calibration = valid_calibration[name].values
            if len(valid_calibration) > 0:
                valid_calibration = valid_calibration[-1]
            else:
                valid_calibration = nan
        finally:
            logging.getLogger().info(
                'Result from calibration query "{query}"\n\t{name}={result}'.format(query=query, name=name,
                                                                                    result=valid_calibration))
            # logging.getLogger().info(
            #    'Got "{name}" calibration {calibration}'.format(name=name, calibration=valid_calibration))
            return valid_calibration

    def get_cameralength_calibration(self):
        """Get the calibration value from a file or from input in the GUI"""
        if self._view.useCalibrationFileRadioButton.isChecked():
            parameters = self._parameter_controller.get_model()
            query = "`Nominal Cameralength (cm)` == {parameters.cameralength.nominal_value}".format(
                parameters=parameters)
            return self.get_calibration('Cameralength (cm)', query)
        else:
            return self._view.cameraLengthSpinBox.value()

    def get_magnification_calibration(self):
        if self._view.useCalibrationFileRadioButton.isChecked():
            parameters = self._parameter_controller.get_model()
            query = "`Nominal Magnification ()` == {parameters.magnification.nominal_value} & `Mag mode` == '{parameters.mag_mode.value}'".format(
                parameters=parameters)
            return self.get_calibration('Magnification ()', query)
        else:
            return self._view.magnificationSpinBox.value()

    def get_image_scale_calibration(self):
        if self._view.useCalibrationFileRadioButton.isChecked():
            parameters = self._parameter_controller.get_model()
            query = "`Nominal Magnification ()` == {parameters.magnification.nominal_value} & `Mag mode` == '{parameters.mag_mode.value}'".format(
                parameters=parameters)
            return self.get_calibration('Scale (nm)', query)
        else:
            if self._view.scaleSelector.currentText() == 'Å':
                return self._view.scaleSpinBox.value()
            else:
                return nan

    def get_diffraction_scale_calibration(self):
        if self._view.useCalibrationFileRadioButton.isChecked():
            parameters = self._parameter_controller.get_model()
            query = "`Nominal Cameralength (cm)` == {parameters.cameralength.nominal_value}".format(
                parameters=parameters)
            return self.get_calibration('Scale (1/Å)', query)
        else:
            if self._view.scaleSelector.currentText() == '1/Å':
                return self._view.scaleSpinBox.value()
            else:
                return nan

    def get_x_scan_calibration(self):
        if self._view.useCalibrationFileRadioButton.isChecked():
            parameters = self._parameter_controller.get_model()
            if parameters.mode.value == 'STEM':
                query = "`Mode` == '{parameters.mode.value}' & `Nominal Step Size X (nm)` == {parameters.scan_step_x.nominal_value}".format(
                    parameters=parameters)
            else:
                query = "`Mode` == '{parameters.mode.value}' & `Alpha` == '{parameters.alpha.value}' & `Nominal Step Size X (nm)` == {parameters.scan_step_x.nominal_value}".format(
                    parameters=parameters)
            return self.get_calibration('Step Size X (nm)', query)
        else:
            return self._view.stepSizeXSpinBox.value()

    def get_y_scan_calibration(self):
        if self._view.useCalibrationFileRadioButton.isChecked():
            parameters = self._parameter_controller.get_model()
            if parameters.mode.value == 'STEM':
                query = "`Mode` == '{parameters.mode.value}' & `Nominal Step Size Y (nm)` == {parameters.scan_step_x.nominal_value}".format(
                    parameters=parameters)
            else:
                query = "`Mode` == '{parameters.mode.value}' & `Alpha` == '{parameters.alpha.value}' & `Nominal Step Size Y (nm)` == {parameters.scan_step_x.nominal_value}".format(
                    parameters=parameters)
            return self.get_calibration('Step Size Y (nm)', query)
        else:
            return self._view.stepSizeYSpinBox.value()

    def get_image_rotation_calibration(self):
        parameters = self._parameter_controller.get_model()
        query = "`Mag Mode` == '{parameters.mag_mode.value}' & `Nominal Mag` == {parameters.magnification.nominal_value}".format(
            parameters=parameters)
        return self.get_calibration('Image Rotation (deg)', query)

    def get_scan_rotation_calibration(self):
        parameters = self._parameter_controller.get_model()
        if parameters.mode.value == 'STEM':
            query = "`Mode` == '{parameters.mode.value}'".format(
                parameters=parameters)
        else:
            query = "`Mode` == '{parameters.mode.value}' & `Alpha` == {parameters.alpha.value}".format(
                parameters=parameters)
        return self.get_calibration('Scan Rotation (deg)', query)

    def get_precession_calibration(self):
        return self.get_rocking_angle_calibration()

    def get_rocking_angle_calibration(self):
        if self._view.useCalibrationFileRadioButton.isChecked():
            parameters = self._parameter_controller.get_model()
            if parameters.mode.value == 'STEM':
                return nan
            else:
                query = "`Mode` == '{parameters.mode.value}' & `Alpha` == {parameters.alpha.value} & `Nominal Precession Angle (deg)` == {parameters.rocking_angle.nominal_value}".format(
                    parameters=parameters)
                return self.get_calibration('Precession Angle (deg)', query)
        else:
            return self._view.rockingAngleSpinBox.value()

    def get_rocking_angle_eccentricity_calibration(self):
        parameters = self._parameter_controller.get_model()
        if parameters.mode.value == 'STEM':
            return nan
        else:
            query = "`Mode` == '{parameters.mode.value}' & `Alpha` == {parameters.alpha.value} & `Nominal Precession Angle (deg)` == {parameters.rocking_angle.nominal_value}".format(
                parameters=parameters)
            return self.get_calibration('Precession Eccentricity', query)

    def get_condenser_aperture_calibration(self):
        parameters = self._parameter_controller.get_model()
        query = "`Nominal Condenser Aperture (um)` == {parameters.condenser_aperture.value}".format(
            parameters=parameters)
        return self.get_calibration('Condenser Aperture (um)', query)

    def get_convergence_angle_calibration(self):
        parameters = self._parameter_controller.get_model()
        if parameters.mode == 'STEM':
            query = "`Mode` == '{parameters.mode.value}' & `Nominal Condenser Aperture (um)` == {parameters.condenser_aperture.value}".format(
                parameters=parameters)
        else:
            query = "`Mode` == '{parameters.mode.value}' & `Alpha` == {parameters.alpha.value} & `Nominal Condenser Aperture (um)` == {parameters.condenser_aperture.value}".format(
                parameters=parameters)
        return self.get_calibration('Convergence Angle (mrad)', query)

    def get_spotsize_calibration(self):
        if self._view.useCalibrationFileRadioButton.isChecked():
            parameters = self._parameter_controller.get_model()
            if parameters.mode == 'TEM':
                query = "`Spot` == {parameters.spot.value}".format(
                    parameters=parameters)
            else:
                query = "`Nominal Spotsize (nm)` == {parameters.spotsize.nominal_value}".format(
                    parameters=parameters)
            return self.get_calibration('Spotsize (nm)', query)
        else:
            return self._view.spotSizeSpinBox.value()

    def update_view(self):
        self.calibrate()
        if self._model.data is not None:
            self._view.fileStatusIndicator.setActive()
            self._view.readFileInfoButton.setEnabled(True)
        else:
            self._view.fileStatusIndicator.setNone()
            self._view.readFileInfoButton.setEnabled(False)

    def clear(self):
        logging.getLogger().info('Clearing data and metadata')
        self._model.clear_data()
        self.reset_indicators()
        self._view.dwelltimeSpinBox.setValue(0.0)
        self._view.rotationSpinBox.setValue(0.0)
        self._view.stepsXSpinBox.setValue(0)
        self._view.stepsYSpinBox.setValue(0)
        self._view.specimenLineEdit.clear()
        self._view.operatorLineEdit.clear()
        self._view.notesTextEdit.clear()
        self._view.bitDepthSelector.setCurrentIndex(0)
        self._view.rechunkComboBox.setCurrentIndex(0)
        self._view.overwriteCheckBox.setChecked(False)
        self._view.fileFormatSelector.setCurrentIndex(0)
        self._view.xPosSpinBox.setValue(0.0)
        self._view.yPosSpinBox.setValue(0.0)
        self._view.zPosSpinBox.setValue(0.0)
        self._view.xTiltSpinBox.setValue(0.0)
        self._view.yTiltSpinBox.setValue(0.0)
        self._view.detectorXSpinBox.setValue(256)
        self._view.detectorYSpinBox.setValue(256)
        self._view.stepSizeXSpinBox.setValue(0.0)
        self._view.stepSizeYSpinBox.setValue(0.0)
        self._view.scaleXSpinBox.setValue(0.0)
        self._view.scaleYSpinBox.setValue(0.0)
        self._view.scaleXSelector.setCurrentIndex(0)
        self._view.scaleYSelector.setCurrentIndex(0)
        self._view.rockingAngleSpinBox.setValue(0.0)
        self._view.spotSizeSpinBox.setValue(0.0)
        self._view.cameralengthSpinBox.setValue(0.0)
        self._view.magnificationSpinBox.setValue(0.0)
        self._parameter_controller.get_view().magnificationGroupBox.setChecked(False)
        self._parameter_controller.get_view().cameraLengthGroupBox.setChecked(False)
        self._parameter_controller.get_view().modeSelector.setCurrentIndex(0)
        self._parameter_controller.get_view().alphaGroupBox.setChecked(False)
        self._parameter_controller.get_view().spotGroupBox.setChecked(False)
        self._parameter_controller.get_view().condenserApertureGroupBox.setChecked(False)
        self._parameter_controller.get_view().convergenceAngleGroupBox.setChecked(False)
        self._parameter_controller.get_view().spotSizeGroupBox.setChecked(False)
        self._parameter_controller.get_view().precessionAngleGroupBox.setChecked(False)
        self._parameter_controller.get_view().precessionFrequencyGroupBox.setChecked(False)
        self._parameter_controller.get_view().acquisitionDateGroupBox.setChecked(False)
        self._parameter_controller.get_view().stepGroupBox.setChecked(False)
        self._parameter_controller.update()
        logging.getLogger().info('Cleared data and metadata!')

    def set_scan_size_from_header(self):
        """
        Sets the scan size of the data based on header file.
        """
        logging.getLogger().info(
            'Setting scan sizes based on header file. Frames per trigger is {self._model.hdr.frames_per_trigger}'.format(
                self=self))
        if self._model.data is None:
            raise TypeError

        N = len(self._model.data)
        nx = int(self._model.hdr.frames_per_trigger)
        ny = int(N / nx)
        self._view.stepsXSpinBox.setValue(nx)
        self._view.stepsYSpinBox.setValue(ny)
        logging.getLogger().info('Set scan sizes based on header file successfully')

    def worker_progress(self, progress):
        logging.getLogger().info('Progress: {progress}'.format(progress=progress))

    def worker_finished(self):
        logging.getLogger().info('Worker finished')

    def worker_error(self, error):  # *args, **kwargs):
        # logging.getLogger().error(*args, **kwargs)
        exctype, value, format_exc = error
        logging.getLogger().error(format_exc)

    def worker_result(self, result):
        logging.getLogger().info('Result from worker: {result!r}'.format(result=result))
        return result

    def worker_wrapper(self, fn, *args, **kwargs):
        worker = Worker(fn, *args, **kwargs)
        worker.signals.error.connect(self.worker_error)
        worker.signals.finished.connect(self.worker_finished)
        worker.signals.progress.connect(self.worker_progress)
        worker.signals.result.connect(self.worker_result)
        return worker

    def reset_indicators(self):
        self._view.fileStatusIndicator.setNone()
        self._view.headerStatusIndicator.setNone()
        self._view.reshapedIndicator.setNone()
        self._view.downsampledIndicator.setNone()
        self._view.rechunkedIndicator.setNone()
        self._view.writtenIndicator.setNone()

    def load_data(self):
        """Start a worker to load a signal"""
        self.reset_indicators()
        self._view.fileStatusIndicator.setBusy()
        worker = self.worker_wrapper(self._model.load_file, filename=self._view.inputFilePathField.text())
        worker.signals.error.connect(lambda e: self._view.fileStatusIndicator.setInactive())
        worker.signals.error.connect(lambda e: self._model.clear_data())
        worker.signals.finished.connect(
            lambda: logging.getLogger().info('Data: {self._model.data!r}'.format(self=self)))
        self._view.threadpool.start(worker)

    def write_data(self):
        """Start a worker to write a signal"""
        worker = self.worker_wrapper(self.convert_data)
        self._view.threadpool.start(worker)

    def reshape_data(self, data_array, nx, ny, dx, dy, update_indicator=True):
        """
        Return a reshaped data array

        :param data_array: The data to be reshaped
        :param nx: size in x-direction (scan)
        :param ny: size in y-direction (scan)
        :param dx: detector size in x-direction
        :param dy: detector size in y-direction
        :type data_array: array-like
        :type nx: int
        :type ny: int
        :type dx: int
        :type dy: int
        :return: The reshaped data array
        :rtype: array-like
        """
        logging.getLogger().info('Reshaping data to shape ({nx}, {ny} | {dx}, {dy})'.format(nx=nx, ny=ny, dx=dx, dy=dy))
        if update_indicator:
            self._view.reshapedIndicator.setBusy()
        if nx > 0 and ny > 0:
            logging.getLogger().info('Treating data as image stack when reshaping')
            shape = (nx, ny, dx, dy)
        else:
            logging.getLogger().info('Treating data as single image when reshaping')
            shape = (dx, dy)
            if update_indicator:
                self._view.reshapedIndicator.setInactive()
        logging.getLogger().info('Using data shape {}'.format(shape))
        data_array = data_array.reshape(shape)
        if update_indicator:
            self._view.reshapedIndicator.setActive()
        logging.getLogger().info('Reshaped data')
        return data_array

    def downsample_data(self, data_array, bitdepth, update_indicator=True):
        """
        Change the data type of a data array

        :param data_array: The data array to downsample
        :type data_array: array-like
        :param bitdepth: the datatype to change the data into
        :type bitdepth: str
        :return: data_array
        :rtype: array-like
        """
        if update_indicator:
            self._view.downsampledIndicator.setBusy()
        if bitdepth == 'None':
            if update_indicator:
                self._view.downsampledIndicator.setInactive()
            logging.getLogger().info('Did not downsample data')
        else:
            data_array = data_array.astype(bitdepth)
            if update_indicator:
                self._view.downsampledIndicator.setActive()
            logging.getLogger().info('Downsapled data to {}'.format(bitdepth))
        return data_array

    def rechunk_data(self, data_array, chunksize, update_indicator=True):
        """
        Change the chunking of a dask array
        :param data_array: The data array to rechunk
        :param chunksize: The chunksize to use
        :type data_array: array-like
        :type chunksize: int
        :return: data_array, chunks. The rechunked data array and the chunks used
        :rtype: array-like
        """
        if update_indicator:
            self._view.rechunkedIndicator.setBusy()
        if chunksize != 'None':
            chunks = tuple([int(chunksize)] * len(data_array.shape))
            logging.getLogger().info('Rechunking data to {} chunks'.format(chunks))
            data_array = data_array.rechunk(chunks)
            if update_indicator:
                self._view.rechunkedIndicator.setActive()
            logging.getLogger().info('Rechunked data')
        else:
            logging.getLogger().info('Did not rechunk data')
            chunks = None
            if update_indicator:
                self._view.rechunkedIndicator.setInactive()
        return data_array, chunks

    def generate_metadata(self):
        """
        Create a metadata dictionary based on the GUI input
        :return: metadata
        :rtype: dict
        """
        logging.getLogger().info('Generating metadata')
        metadata = {
            'General': {
                'Specimen': self._view.specimenLineEdit.text(),
                'Operator': self._view.operatorLineEdit.text(),
                'Notes': self._view.notesTextEdit.toPlainText()
            },
            'Acquisition_instrument': {
                'TEM': {
                    'Stage': {
                        'X': self._view.xPosSpinBox.value(),
                        'Y': self._view.yPosSpinBox.value(),
                        'Z': self._view.zPosSpinBox.value(),
                        'Xtilt': self._view.xTiltSpinBox.value(),
                        'YTilt': self._view.yTiltSpinBox.value()
                    },
                    'Scan': {
                        'Dwelltime': self._view.dwelltimeSpinBox.value(),
                        'Rotation': self._view.rotationSpinBox.value()
                    },
                    'Parameters': self._parameter_controller.get_model().get_parameters_as_dict()
                }
            }
        }
        logging.getLogger().info('Generated metadata:\n{metadata}'.format(metadata=metadata))
        return metadata

    def generate_vbf(self, signal, figsize=(6, 6), x_offset=0.01, y_offset=0.01, fraction=1 / 5, color='w',
                     scalebarwidth=0.01, save=True):
        """
        Generate a VBF image

        :param signal: The signal to use
        :param figsize: The size of the resulting figure in inches
        :param x_offset: Offset of scalebar in x-direction in fraction of axis size
        :param y_offset: Offset of scalebar in y-direction in fraction of axis size
        :param fraction: Length of scalebar in fraction of axis size.
        :param color: Color of scalebar
        :param scalebarwidth: Width of scalebar in fraction of axis size
        :type signal: hyperspy.signals.BaseSignal
        :type figsize: tuple
        :type x_offset: float
        :type y_offset: float
        :type fraction: float
        :type color: str
        :type scalebarwidth: float
        :return:
        """
        logging.getLogger().info('Generating VBF image')
        cx = self._view.vbfCxSpinBox.value()
        cy = self._view.vbfCySpinBox.value()
        width = self._view.vbfWidthSpinBox.value()
        logging.getLogger().info('VBF center: ({cx}, {cy}), width: {width}'.format(cx=cx, cy=cy, width=width))
        # roi = pxm.roi.CircleROI(cx=cx, cy=cy, r=r)
        # vbf = signal.get_integrated_intensity(roi)

        logging.getLogger().info('Generated VBF image')
        vbf = signal.isig[cx - width:cx + width + 1, cy - width:cy + width + 1].sum(axis=[2, 3])
        fig = plt.figure(figsize=figsize)
        ax = fig.add_axes([0, 0, 1, 1], xticks=[], yticks=[])
        ax.imshow(vbf.data)
        image_width = vbf.axes_manager[0].size * vbf.axes_manager[0].scale
        units = vbf.axes_manager[0].units
        d = round(image_width * fraction, ndigits=-1)
        width = d / image_width

        scalebar = Rectangle(xy=(x_offset, y_offset), facecolor=color, width=width, height=scalebarwidth,
                             transform=ax.transAxes)
        ax.add_patch(scalebar)
        ax.annotate('{d:.0f} {u}'.format(d=d, u=units), xy=(x_offset + width / 2, y_offset + scalebarwidth),
                    color=color,
                    ha='center', va='bottom', xycoords='axes fraction')

        if save:
            path = Path(self._view.inputFilePathField.text()).with_suffix('.png')
            plt.savefig(str(path))
            logging.getLogger().info('Saved VBF image to {}'.format(path))
            plt.close('all')
        else:
            plt.show()

    def set_signal_calibration(self, signal, nx, ny):
        """
        Sets the calibration scale of the signal based on calibration values in the GUI
        :param signal: The signal to set the calibration for
        :type signal: hyperspy.signals.Signal2D
        :param nx: The size of the navigation dimension in x
        :type nx: int
        :param ny: The size of the navigation dimension in y
        :type ny: int
        :return:
        """
        if nx <= 1 and ny <= 1:
            nav_axes = [None, None]
            sig_axes = [0, 1]
        elif nx > 1 and ny <= 1:
            nav_axes = [0, None]
            sig_axes = [1, 2]
        elif nx <= 1 and ny > 1:
            nav_axes = [None, 0]
            sig_axes = [1, 2]
        elif nx > 1 and ny > 1:
            nav_axes = [0, 1]
            sig_axes = [2, 3]
        else:
            nav_axes = [None, None]
            sig_axes = [None, None]

        if self._view.dataSelector.currentText() == 'Imaging':
            units = 'nm'
            scale = self.get_image_scale_calibration()
        elif self._view.dataSelector.currentText() == 'Diffraction':
            units = '$A^{-1}$'
            scale = self.get_diffraction_scale_calibration()
        else:
            units = ''
            scale = 1
        for ax, name in zip(sig_axes, ('kx', 'ky')):
            if ax is not None:
                signal.axes_manager[ax].scale = scale
                signal.axes_manager[ax].units = units
                signal.axes_manager[ax].name = name

        if nav_axes[0] is not None:
            signal.axes_manager[nav_axes[0]].scale = self.get_x_scan_calibration()
            signal.axes_manager[nav_axes[0]].units = 'nm'
            signal.axes_manager[nav_axes[0]].name = 'x'
        if nav_axes[1] is not None:
            signal.axes_manager[nav_axes[1]].scale = self.get_y_scan_calibration()
            signal.axes_manager[nav_axes[1]].units = 'nm'
            signal.axes_manager[nav_axes[1]].name = 'y'

    def prepare_data(self, update_indicators=True):
        """
        Prepare the data
        :return: signal, chunks. The prepared signal and the chunks used to rechunk it.

        """
        if self._model.data is None:
            raise TypeError()

        nx = self._view.stepsXSpinBox.value()
        ny = self._view.stepsYSpinBox.value()
        dx = self._view.detectorXSpinBox.value()
        dy = self._view.detectorYSpinBox.value()
        if nx == ny == 0:
            logging.getLogger().info('Treating {self._model.data} as single image'.format(self=self))
            data_array = self._model.data.inav[0].data
        else:
            logging.getLogger().info('Treating {self._model.data} as image stack'.format(self=self))
            data_array = self._model.data.data

        data_array = self.reshape_data(data_array, nx, ny, dx, dy, update_indicator=update_indicators)
        data_array = self.downsample_data(data_array, self._view.bitDepthSelector.currentText(),
                                          update_indicator=update_indicators)
        data_array, chunks = self.rechunk_data(data_array, self._view.rechunkComboBox.currentText(),
                                               update_indicator=update_indicators)

        logging.getLogger().info('Creating signal from converted data')
        signal = pxm.LazyElectronDiffraction2D(data_array)
        logging.getLogger().info('Created signal {}'.format(signal))
        self.set_signal_calibration(signal, nx, ny)
        signal.original_metadata.add_dictionary(self.generate_metadata())

        return signal, chunks

    def convert_data(self):
        """
        Convert the data, and save it as a signal.
        :return:
        """
        signal, chunks = self.prepare_data()

        logging.getLogger().info('Writing data')
        self._view.writtenIndicator.setBusy()
        if chunks is not None:
            signal.save(self._model.filename.with_suffix(self._view.fileFormatSelector.currentText()), chunks=chunks,
                        overwrite=self._view.overwriteCheckBox.isChecked())
        else:
            signal.save(self._model.filename.with_suffix(self._view.fileFormatSelector.currentText()),
                        overwrite=self._view.overwriteCheckBox.isChecked())
        self._view.writtenIndicator.setActive()
        logging.getLogger().info('Wrote data')

        if self._view.vbfGroupBox.isChecked():
            self.generate_vbf(signal)
        del signal


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super(SettingsDialog, self).__init__(parent)
        uic.loadUi(str(Path(__file__).parent / './source/QTCmib2hspy/settingsdialog.ui'), self)


def run_gui():
    main('debug.log')


def main(logfile=None):
    """
    Intialize a standard GUI with logging
    :param logfile: path to output log (debug) file. DEfault is None, in which case a new timestamped logfile will be created under ./logs/
    :return:
    """
    # Create debug file if not provided
    if logfile is None:
        now = datetime.now()
        debug_file = Path('./logs/{stamp}_debug.log'.format(stamp=now.strftime('%Y-%m-%d_%H:%M:%S')))
    else:
        debug_file = Path(logfile)
    debug_file.parent.mkdir(parents=True, exist_ok=True)
    with debug_file.open('w') as f:
        f.close()

    # Setup logging
    logformat = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fileHandler = logging.FileHandler(str(debug_file))
    fileHandler.setFormatter(logformat)
    logging.getLogger().addHandler(fileHandler)
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().addHandler((logging.StreamHandler(sys.stdout)))
    # sys.stdout = LogStream(logging.getLogger(), logging.DEBUG)
    # sys.stderr = LogStream(logging.getLogger(), logging.ERROR)

    logging.debug('Hei')

    myqui = QtWidgets.QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    notes_window = NotesWindow()

    parameters_window = ParametersWindow()
    parameters_model = Microscope()
    parameters_controller = ParameterController(view=parameters_window, model=parameters_model)

    model = mib2hspyModel()
    controller = mib2hspyController(main_window, model, notes_window=notes_window,
                                    parameters_controller=parameters_controller)

    sys.exit(myqui.exec_())

    # app = QtWidgets.QApplication(sys.argv)
    # window = MainWindow()
    # window.show()
    # window.activateWindow()
    # window.raise_()
    # sys.exit(app.exec())


if __name__ == '__main__':
    main('debug.log')
