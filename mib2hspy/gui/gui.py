import logging
import sys
from datetime import datetime
from pathlib import Path
from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThreadPool, QObject
import pandas as pd
from math import sqrt, isclose
from mib2hspy.gui.guiTools import QTextEditLogger
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
    # logging.getLogger().addHandler((logging.StreamHandler(sys.stderr)))
    # sys.stdout = LogStream(logging.getLogger(), logging.INFO)
    # sys.stderr = LogStream(logging.getLogger(), logging.ERROR)

    myqui = QtWidgets.QApplication(sys.argv)
    window = ConverterView()
    window.show()

    model = ConverterModel()
    controller = ConverterController(window, model)

    sys.exit(myqui.exec_())

    # app = QtWidgets.QApplication(sys.argv)
    # window = MainWindow()
    # window.show()
    # window.activateWindow()
    # window.raise_()
    # sys.exit(app.exec())


if __name__ == '__main__':
    main(log_level=logging.INFO)
