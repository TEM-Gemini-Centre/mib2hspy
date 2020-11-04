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

class NotesWindow(QtWidgets.QMainWindow):
    textChanged = pyqtSignal()
    def __init__(self, *args, **kwargs):
        super(NotesWindow, self).__init__(*args, **kwargs)

        # Load ui file
        uic.loadUi('./source/QTCmib2hspy/noteswindow.ui', self)
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


class mib2hspyModel(QObject):
    filenameChanged = pyqtSignal([], [str], name='filenameChanged')
    dataLoaded = pyqtSignal([], [int], name='dataLoaded')
    dataCleared = pyqtSignal(name='dataCleared')
    headerLoaded = pyqtSignal([], [int], name='headerLoaded')
    headerCleared = pyqtSignal(name='headerCleared')

    def __init__(self):
        super(mib2hspyModel, self).__init__()
        self.filename = None
        self.data = None
        self.hdr = MedipixHDRcontent('.')

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

    def clear_data(self):
        """
        Clears the data and header contents.
        :return:
        """
        self.data = None
        self.hdr.clear()

        self.dataCleared.emit()
        self.headerCleared.emit()

        logging.getLogger().info(
            'Cleared data:\ndata: {self.data!r}\nHeader: {self.hdr!r}'.format(self=self))


class mib2hspyController(object):
    def __init__(self, view, model=None, notes_window=None):
        """
        Create controller for the mib2hspy gui
        :param view: The main gui window.
        :type view: MainWindow
        :param model: The model to control.
        :type model: mib2hspyModel
        :param notes_window: The notes subwindow
        :type notes_window: NotesWindow
        """
        self._view = view
        self._notes_view = notes_window
        self._model = model

        self.setupLogging()
        self.setupInputFileSignals()

        self._model.headerLoaded.connect(lambda: self.set_scan_size_from_header())
        self._view.writeFileButton.clicked.connect(self.write_data)
        self._view.actionNotes.triggered.connect(lambda: self._notes_view.show())

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
        self._view.browseInputFileButton.clicked.connect(
            lambda: self._view.inputFilePathField.setText(self._view.browseInputFile()))
        self._view.loadInputFileButton.clicked.connect(self.load_data)
        self._model.dataLoaded.connect(self.update_view)
        self._model.dataLoaded.connect(self._model.load_hdr)
        self._model.headerLoaded.connect(lambda: self._view.headerStatusIndicator.setActive())
        self._model.headerLoaded.connect(lambda: self.update_view())
        self._model.dataCleared.connect(lambda: self._view.fileStatusIndicator.setInactive())
        self._model.headerCleared.connect(lambda: self._view.headerStatusIndicator.setInactive())
        self._model.dataCleared.connect(lambda: self.update_view())
        self._model.headerCleared.connect(lambda: self.update_view())


    def update_view(self):
        if self._model.data is not None:
            self._view.fileStatusIndicator.setActive()
        else:
            self._view.fileStatusIndicator.setNone()

    def set_scan_size_from_header(self):
        """
        Sets the scan size of the data based on header file.
        """
        logging.getLogger().info('Setting scan sizes based on header file. Frames per trigger is {self._model.hdr.frames_per_trigger}'.format(self=self))
        if self._model.data is None:
            raise TypeError

        N = len(self._model.data)
        nx = int(self._model.hdr.frames_per_trigger)
        ny = int(N/nx)
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

    def load_data(self):
        """Start a worker to load a signal"""
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


    def reshape_data(self, data_array, nx, ny, dx, dy):
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
        self._view.reshapedIndicator.setBusy()
        if nx > 0 and ny > 0:
            logging.getLogger().info('Treating data as image stack when reshaping')
            shape = (nx, ny, dx, dy)
        else:
            logging.getLogger().info('Treating data as single image when reshaping')
            shape = (dx, dy)
        logging.getLogger().info('Using data shape {}'.format(shape))
        data_array = data_array.reshape(shape)
        self._view.reshapedIndicator.setActive()
        logging.getLogger().info('Reshaped data')
        return data_array

    def downsample_data(self, data_array, bitdepth):
        """
        Change the data type of a data array

        :param data_array: The data array to downsample
        :type data_array: array-like
        :param bitdepth: the datatype to change the data into
        :type bitdepth: str
        :return: data_array
        :rtype: array-like
        """
        self._view.downsampledIndicator.setBusy()
        if bitdepth == 'None':
            self._view.downsampledIndicator.setInactive()
            logging.getLogger().info('Did not downsample data')
        else:
            data_array = data_array.astype(bitdepth)
            self._view.downsampledIndicator.setActive()
            logging.getLogger().info('Downsapled data to {}'.format(bitdepth))
        return data_array

    def rechunk_data(self, data_array, chunksize):
        """
        Change the chunking of a dask array
        :param data_array: The data array to rechunk
        :param chunksize: The chunksize to use
        :type data_array: array-like
        :type chunksize: int
        :return: The rechunked data array
        :rtype: array-like
        """
        self._view.rechunkedIndicator.setBusy()
        if chunksize != 'None':
            chunks = [int(chunksize)] * len(data_array.shape)
            logging.getLogger().info('Rechunking data to {} chunks'.format(chunks))
            data_array = data_array.rechunk(chunks)
            self._view.rechunkedIndicator.setActive()
            logging.getLogger().info('Rechunked data')
        else:
            logging.getLogger().info('Did not rechunk data')
            self._view.rechunkedIndicator.setInactive()
        return data_array

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
                'Operator': self._view.operatorLineEdit.text()
                'Notes': self._notes_view.get_text()
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
                    }
                }
            }
        }
        logging.getLogger().info('Generated metadata:\n{metadata}'.format(metadata=metadata))
        return  metadata

    def convert_data(self):
        """
        Convert the data, and save it as a signal.
        :return:
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

        data_array = self.reshape_data(data_array, nx, ny, dx, dy)
        data_array = self.downsample_data(data_array, self._view.bitDepthSelector.currentText())
        data_array = self.rechunk_data(data_array, self._view.rechunkComboBox.currentText())

        logging.getLogger().info('Creating signal from converted data')
        signal = pxm.LazyElectronDiffraction2D(data_array)
        logging.getLogger().info('Created signal {}'.format(signal))

        signal.original_metadata.add_dictionary(self.generate_metadata())

        logging.getLogger().info('Writing data')
        self._view.writtenIndicator.setBusy()
        signal.save(self._model.filename.with_suffix(self._view.fileFormatSelector.currentText()),
                    overwrite=self._view.overwriteCheckBox.isChecked())
        self._view.writtenIndicator.setActive()
        logging.getLogger().info('Wrote data')


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

    main_window = MainWindow()
    main_window.show()

    notes_window = NotesWindow()

    model = mib2hspyModel()
    controller = mib2hspyController(main_window, model, notes_window=notes_window)

    sys.exit(myqui.exec_())

    # app = QtWidgets.QApplication(sys.argv)
    # window = MainWindow()
    # window.show()
    # window.activateWindow()
    # window.raise_()
    # sys.exit(app.exec())


if __name__ == '__main__':
    main('debug.log')
