import logging
import sys
from datetime import datetime
from pathlib import Path
from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThreadPool, QObject
import pyxem as pxm

import time
# from .guiTools import tools
from mib2hspy.gui.guiTools import Worker, QTextEditLogger
from mib2hspy.Tools import MedipixHDRcontent, MedipixHDRfield


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
        uic.loadUi('./source/QTCmib2hspy/mainwindow.ui', self)
        self.setWindowTitle('mib2hspy converter')
        self.threadpool = QThreadPool()

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
            "",
            "mib Files (*.mib);;hspy Files (*.hspy);;All Files (*)",
            options=options)
        return fileName

    @pyqtSlot(int, int, name='setStepSize')
    def setStepSize(self, nx, ny):
        self.stepsXSpinBox.setValue(nx)
        self.stepsYSpinBox.setValue(ny)

    @pyqtSlot(tuple, name='setStepSize')
    def setStepSize(self, steps):
        if steps[0] is None:
            steps = (0, steps[1])
        if steps[1] is None:
            steps = (steps[0], 0)
        self.stepsXSpinBox.setValue(steps[0])
        self.stepsYSpinBox.setValue(steps[1])

    # @pyqtSlot()
    # def returnPressedInputFileField(self):
    #     self.message.emit('Return pressed in input file path')
    #     self.model.setFilename(self.inputFilePathField.text())
    #     self.update.emit()


class mib2hspyModel(QObject):
    filenameChanged = pyqtSignal([], [str], name='filenameChanged')
    dataLoaded = pyqtSignal([], [int], name='dataLoaded')
    dataCleared = pyqtSignal(name='dataCleared')
    headerLoaded = pyqtSignal([], [int], name='headerLoaded')
    headerCleared = pyqtSignal(name='headerCleared')
    scanSizeChanged = pyqtSignal([], [int, int], [tuple], name='scanSizeChanged')
    dwelltimeChanged = pyqtSignal([], [float], name='dwelltimeChanged')
    scanRotationChanged = pyqtSignal([], [float], name='scanRotationChanged')
    specimenChanged = pyqtSignal([], [str], name='specimenChanged')
    operatorChanged = pyqtSignal([], [str], name='operatorChanged')
    positionXChanged = pyqtSignal([], [float], name='positionXChanged')
    positionYChanged = pyqtSignal([], [float], name='positionYChanged')
    positionZChanged = pyqtSignal([], [float], name='positionZChanged')
    tiltXChanged = pyqtSignal([], [float], name='tiltXChanged')
    tiltYChanged = pyqtSignal([], [float], name='tiltYChanged')

    def __init__(self):
        super(mib2hspyModel, self).__init__()
        self.filename = None
        self.data = None
        self.data_array = None
        self.hdr = MedipixHDRcontent('.')
        self.scan_size = (None, None)
        self.dwelltime = None
        self.scan_rotation = None
        self.specimen = None
        self.operator = None

        self.position_x = None
        self.position_y = None
        self.position_z = None
        self.tilt_x = None
        self.tilt_y = None

    def set_filename(self, filename):
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

    def clear_data(self):
        self.data = None
        self.data_array = None
        self.hdr.clear()

        self.dwelltime = None
        self.scan_rotation = None

        self.specimen = None
        self.operator = None

        self.position_x = None

        self.dataCleared.emit()
        self.headerCleared.emit()

        logging.getLogger().info(
            'Cleared data:\ndata: {self.data!r}\ndata array: {self.data_array!r}\nHeader: {self.hdr!r}'.format(
                self=self))

    def set_steps_x(self, steps):
        """
        Sets the scan size in x-direction

        :param steps: The number of steps in x-direction
        :type steps: int
        :return:
        """
        self.scan_size = (steps, self.scan_size[1])
        self.scanSizeChanged.emit()
        self.scanSizeChanged[tuple].emit(self.scan_size)
        logging.getLogger().info('Set number of steps in x axis to {steps!r}'.format(steps=steps))

    def set_steps_y(self, steps):
        """
        Sets the scan size in y-direction

        :param steps: The number of steps in y-direction
        :type steps: int
        :return:
        """
        self.scan_size = (self.scan_size[0], steps)
        self.scanSizeChanged.emit()
        self.scanSizeChanged[tuple].emit(self.scan_size)
        logging.getLogger().info('Set number of steps in y axis to {steps!r}'.format(steps=steps))

    def set_dwelltime(self, dwelltime):
        """
        Sets the dwelltime of the scan

        :param dwelltime: The dwelltime of the scan in ms
        :type dwelltime: float
        :return:
        """
        if not isinstance(dwelltime, float):
            raise TypeError()
        self.dwelltime = dwelltime
        self.dwelltimeChanged.emit()
        if isinstance(self.dwelltime, float):
            self.dwelltimeChanged[float].emit(self.dwelltime)
        logging.getLogger().info('Set dwelltime to {self.dwelltime!r} ms'.format(self=self))

    def set_scan_rotation(self, rotation):
        """
        Sets the scan rotation

        :param rotation: Scan rotation in degrees
        :type rotation: float
        :return:
        """
        if not isinstance(rotation, float):
            raise TypeError()
        self.scan_rotation = rotation
        self.scanRotationChanged.emit()
        if isinstance(self.scan_rotation, float):
            self.scanRotationChanged[float].emit(self.scan_rotation)
        logging.getLogger().info('Set scan rotation to {self.scan_rotation!r} deg'.format(self=self))

    def set_specimen(self, specimen):
        """
        Sets the specimen tag/name

        :param specimen: The name of the specimen
        :type specimen: str
        :return:
        """
        if not isinstance(specimen, str):
            raise TypeError()
        self.specimen = specimen
        self.specimenChanged.emit()
        if isinstance(self.specimen, str):
            self.specimenChanged[str].emit(self.specimen)
        logging.getLogger().info('Set specimen to {self.specimen!r}'.format(self=self))

    def set_operator(self, operator):
        """
        Sets the specimen tag/name

        :param operator: The name of the specimen
        :type operator: str
        :return:
        """
        if not isinstance(operator, str):
            raise TypeError()
        self.operator = operator
        self.operatorChanged.emit()
        if isinstance(self.operator, str):
            self.operatorChanged[str].emit(self.operator)
        logging.getLogger().info('Set operator to {self.operator!r}'.format(self=self))

    def set_position_x(self, x):
        """
        Sets the specimen x position

        :param x: Specimen x position in microns
        :type x: float
        :return:
        """
        if not isinstance(x, float):
            raise TypeError()
        self.position_x = x
        self.positionXChanged.emit()
        if isinstance(self.position_x, float):
            self.positionXChanged[float].emit(self.position_x)
        logging.getLogger().info('Set specimen x position to {self.position_x!r} deg'.format(self=self))
        
    def set_position_y(self, y):
        """
        Sets the specimen y position

        :param y: Specimen y position in microns
        :type y: float
        :return:
        """
        if not isinstance(y, float):
            raise TypeError()
        self.position_y = y
        self.positionYChanged.emit()
        if isinstance(self.position_y, float):
            self.positionYChanged[float].emit(self.position_y)
        logging.getLogger().info('Set specimen y position to {self.position_y!r} deg'.format(self=self))
    
    def set_position_z(self, z):
        """
        Sets the specimen z position

        :param z: Specimen z position in microns
        :type z: float
        :return:
        """
        if not isinstance(z, float):
            raise TypeError()
        self.position_z = z
        self.positionZChanged.emit()
        if isinstance(self.position_z, float):
            self.positionZChanged[float].emit(self.position_z)
        logging.getLogger().info('Set specimen z position to {self.position_z!r} deg'.format(self=self))
        
    def set_tilt_x(self, x):
        """
        Sets the specimen x tilt

        :param x: Specimen x tilt in degrees
        :type x: float
        :return:
        """
        if not isinstance(x, float):
            raise TypeError()
        self.tilt_x = x
        self.tiltXChanged.emit()
        if isinstance(self.tilt_x, float):
            self.tiltXChanged[float].emit(self.tilt_x)
        logging.getLogger().info('Set specimen x tilt to {self.tilt_x!r} deg'.format(self=self))
        
    def set_tilt_y(self, y):
        """
        Sets the specimen y tilt or specimen rotation.

        :param y: Specimen y tilt in degrees
        :type y: float
        :return:
        """
        if not isinstance(y, float):
            raise TypeError()
        self.tilt_y = y
        self.tiltYChanged.emit()
        if isinstance(self.tilt_y, float):
            self.tiltYChanged[float].emit(self.tilt_y)
        logging.getLogger().info('Set specimen y tilt to {self.tilt_y!r} deg'.format(self=self))


class mib2hspyController(object):
    def __init__(self, view, model=None):
        """
        Create controller for the mib2hspy gui
        :param view: The main gui window.
        :type view: MainWindow
        :param model: The model to control.
        """
        self._view = view
        self._model = model

        self.setupLogging()
        self.setupInputFileSignals()
        self.setupScanDetails()
        self.setupSessionDetails()

    def setupLogging(self):
        handler = QTextEditLogger(widget=self._view.logView)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(handler)

    def setupInputFileSignals(self):
        self._view.browseInputFileButton.clicked.connect(
            lambda: self._view.inputFilePathField.setText(self._view.browseInputFile()))
        self._view.loadInputFileButton.clicked.connect(self.load_data)
        self._model.dataLoaded.connect(self.update_view)
        self._model.dataLoaded.connect(self._model.load_hdr)
        self._model.headerLoaded.connect(lambda: self._view.headerStatusIndicator.setActive())
        self._model.dataCleared.connect(lambda: self._view.fileStatusIndicator.setInactive())
        self._model.headerCleared.connect(lambda: self._view.headerStatusIndicator.setInactive())

    def setupScanDetails(self):
        self._model.headerLoaded.connect(lambda: self.set_scan_size())
        self._view.stepsXSpinBox.valueChanged.connect(lambda nx: self._model.set_steps_x(nx))
        self._view.stepsYSpinBox.valueChanged.connect(lambda ny: self._model.set_steps_y(ny))
        self._view.dwelltimeSpinBox.valueChanged.connect(lambda dt: self._model.set_dwelltime(dt))
        self._view.rotationSpinBox.valueChanged.connect(lambda rot: self._model.set_scan_rotation(rot))

    def setupSessionDetails(self):
        # self._view.specimenLineEdit.textChanged.connect(lambda text: self._model.set_specimen(text))
        self._view.specimenLineEdit.returnPressed.connect(
            lambda: self._model.set_specimen(self._view.specimenLineEdit.text()))
        self._view.operatorLineEdit.returnPressed.connect(
            lambda: self._model.set_operator(self._view.operatorLineEdit.text()))
        self._view.xPosSpinBox.valueChanged.connect(lambda x: self._model.set_position_x(x))
        self._view.yPosSpinBox.valueChanged.connect(lambda y: self._model.set_position_y(y))
        self._view.zPosSpinBox.valueChanged.connect(lambda z: self._model.set_position_z(z))
        self._view.xTiltSpinBox.valueChanged.connect(lambda x: self._model.set_tilt_x(x))
        self._view.yTiltSpinBox.valueChanged.connect(lambda y: self._model.set_tilt_y(y))




    def update_view(self):
        if self._model.data is not None:
            self._view.fileStatusIndicator.setActive()
        else:
            self._view.fileStatusIndicator.setNone()

    def set_scan_size(self, nx=None, ny=None):
        """
        Sets the scan size of the data.

        If both `nx` and `ny` is `None`, attempts to set scan sized based on the header file content
        If only one of `nx` and `ny` is given, attempts to set the other scan size to match the total shape of the signal navigation size.
        :param nx: scan size in x-direction. Optional, default is None.
        :param ny: scan size in y-direction. Optional, default is None
        :type nx: int
        :type ny: int
        :return:
        """
        if self._model.data is None:
            logging.info('Setting scan size before loading data is not advised!')
            N = None
        else:
            N = len(self._model.data)

        if N is not None:
            if nx is not None and ny is not None:
                if (nx * ny) == N:
                    logging.info('Scan size {size} does not match data size {N}'.format(size=nx * ny, N=N))
            elif nx is None and ny is None:
                nx = int(self._model.hdr.frames_per_trigger.value)
                ny = int(N / nx)
            elif nx is None and ny is not None:
                nx = int(N / ny)
            elif nx is not None and ny is None:
                ny = int(N / nx)
        else:
            if nx is None:
                nx = self._model.scan_size[0]
            if ny is None:
                ny = self._model.scan_size[1]
        steps = (nx, ny)
        self._view.setStepSize(steps)

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

    def load_data(self):
        """Start a worker to load a signal"""
        self._view.fileStatusIndicator.setBusy()
        worker = self.worker_wrapper(self._model.load_file, filename=self._view.inputFilePathField.text())
        worker.signals.error.connect(lambda e: self._view.fileStatusIndicator.setInactive())
        worker.signals.error.connect(lambda e: self._model.clear_data())
        worker.signals.finished.connect(
            lambda: logging.getLogger().info('Data: {self._model.data!r}'.format(self=self)))
        self._view.threadpool.start(worker)


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
    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger().addHandler((logging.StreamHandler(sys.stdout)))
    # sys.stdout = LogStream(logging.getLogger(), logging.DEBUG)
    # sys.stderr = LogStream(logging.getLogger(), logging.ERROR)

    logging.debug('Hei')

    myqui = QtWidgets.QApplication(sys.argv)

    view = MainWindow()
    view.show()
    model = mib2hspyModel()
    controller = mib2hspyController(view, model)

    sys.exit(myqui.exec_())

    # app = QtWidgets.QApplication(sys.argv)
    # window = MainWindow()
    # window.show()
    # window.activateWindow()
    # window.raise_()
    # sys.exit(app.exec())


if __name__ == '__main__':
    main('debug.log')
