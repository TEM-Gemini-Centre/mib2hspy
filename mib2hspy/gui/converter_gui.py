import sys
from datetime import datetime
from pathlib import Path
from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThreadPool, QObject
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import pyxem as pxm
import pandas as pd
from numpy import nan
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd

from mib2hspy.Tools.hdrtools import MedipixHDRcontent


class Error(Exception):
    pass


class DirectoryError(Error):
    pass


class FileError(Error):
    pass


class MIBDataFile(QObject):
    plot_extensions = ['.jpg', '.png']

    def __init__(self, path='', parent=None):
        super(MIBDataFile, self).__init__(parent=parent)
        path = Path(path)
        if not path.suffix == '.mib':
            raise FileError('File "{path}" is not a mib file'.format(path=path))
        self.path = Path(path)
        self.name = self.path.stem
        self.data = None
        self.header = None
        self.dimensions = None
        self.signal_type = None

        self.load()

        # Widgets
        self.print_button = QtWidgets.QPushButton('Print', parent=self.parent())
        self.print_button.clicked.connect(lambda: print(self))

        self.plot_button = QtWidgets.QPushButton('Plot', parent=self.parent())
        self.plot_button.clicked.connect(self.plot)

        # Attempt to extract info from filename
        split_name = self.name.split('_')
        scale = 0
        units = 'cm'
        try:
            for part in split_name:
                if 'kx' in part or 'Mx' in part:
                    if 'kx' in part:
                        units = 'kx'
                    elif 'Mx' in part:
                        units = 'Mx'
                    else:
                        units = 'x'
                    part = part.replace('Mx', '')
                    part = part.replace('kx', '')
                    part = part.replace('x', '')
                    part = part.replace('MAG1', '')
                    part = part.replace('MAG', '')
                    part = part.replace('SAMAG', '')
                    scale = float(part)
                else:
                    if 'cm' in part or 'mm' in part:
                        if 'cm' in part:
                            units = 'cm'
                        elif 'mm' in part:
                            units = 'mm'
                        part = part.replace('cm', '')
                        part = part.replace('mm', '')
                        part = part.replace('CL', '')
                        part = part.replace('cl', '')
                        scale = float(part)
        except ValueError as e:
            scale = 0
            units = 'cm'

        # Create scale widget
        self.scale_widget = QtWidgets.QDoubleSpinBox(parent=self.parent())
        self.scale_widget.setMinimum(0)
        self.scale_widget.setMaximum(999.999)
        self.scale_widget.setDecimals(3)
        self.scale_widget.setSingleStep(0.1)
        self.scale_widget.setValue(scale)

        # Add units selector
        self.units_widget = QtWidgets.QComboBox(parent=self.parent())
        self.units_widget.addItems(['cm', 'mm', 'kx', 'Mx'])
        self.units_widget.setCurrentText(units)

        # Add exposuretime counter [WILL BE REMOVED]
        self.exposure_widget = QtWidgets.QSpinBox()
        self.exposure_widget.setMinimum(0)
        self.exposure_widget.setMaximum(int(1E9))
        self.exposure_widget.setValue(0)
        self.exposure_widget.setSingleStep(1)

        # Add mode selector
        self.mode_widget = QtWidgets.QComboBox()
        self.mode_widget.addItems(['None', 'TEM', 'NBD', 'CBD'])
        self.mode_widget.setCurrentIndex(0)

        # Add convergence angle spinbox
        self.condenser_widget = QtWidgets.QComboBox()
        self.condenser_widget.addItems(['None', '1', '2', '3', '4'])
        self.condenser_widget.setCurrentIndex(0)

    def __repr__(self):
        return '{self.__class__.__name__}(path={self.path!r})'.format(self=self)

    def __str__(self):
        return 'MIB file at "{self.path}":\n\tName: {self.name}\n\tData: {self.data}\n\tDimensions: {self.dimensions}\n\tAxes Manager:\n{self.data.axes_manager}\n\tMetadata:\n{self.data.metadata}\n\tOriginal Metadata:\n{self.data.original_metadata}\n\tPlot Button: {self.plot_button}\n\tPrint Button: {self.print_button}\n\tHeader: {self.header}'.format(
            self=self)

    def __hash__(self):
        return hash(self.path)

    def load(self):
        self.data = pxm.load_mib(str(self.path))
        if len(self.data) == 1:
            self.data = pxm.ElectronDiffraction2D(self.data.inav[0])  # extract single frame if only one dimension!
        if self.path.with_suffix('.hdr').exists():
            self.header = MedipixHDRcontent(self.path.with_suffix('.hdr'))
        else:
            self.header = None
        self.dimensions = len(self.data)

    def save(self, extensions, overwrite=True):
        if not isinstance(extensions, (list, tuple)):
            extensions = list(extensions)

        for extension in extensions:
            if extension in self.plot_extensions:
                if self.signal_type == 'DIFF':
                    self.data.plot(norm='log')
                else:
                    self.data.plot()
                fig = plt.gcf()
                fig.savefig(self.path.with_suffix(extension))
                plt.close(fig)
            else:
                self.data.save(str(self.path.with_suffix(extension)), overwrite=overwrite)

    def plot(self):
        plot_window = PlotWindow(self.parent())
        plot_window.show()

        scale_x = self.data.axes_manager[0].scale
        scale_y = self.data.axes_manager[1].scale
        size_x = self.data.axes_manager[0].size
        size_y = self.data.axes_manager[1].size
        extent = [-scale_x / 2, size_x * scale_x - scale_x / 2, -scale_y / 2, size_y * scale_y - scale_y / 2]

        if 'x' not in self.units_widget.currentText():
            plot_window.plot(self.data, log_scale=True, extent=extent)
        else:
            plot_window.plot(self.data, extent=extent)

    def calibrate(self, calibration_table, signal_type=None):
        """
        Calibrate the signal using the provided calibration table
        :param calibration_table: The calibration table to use
        :type calibration_table: pandas.DataFrame
        :param signal_type: How to interpret the signal. Should be either None, 'DIFF', or 'IMG'. Default is None, and the value of the units widget will be used to determine the type.
        :type signal_type: Union[NoneType, str]
        :return:
        """
        if not isinstance(calibration_table, pd.DataFrame):
            raise TypeError('{calibration_table!r} is an invalid calibration table. Only pandas.DataFrame objects are accepted.')

        if signal_type not in [None, 'DIFF', 'IMG']:
            raise ValueError('`signal_type={signal_type}` is invalid, only `None`, `"DIFF"`, and `"IMG"` are accepted values'.format(signal_type=signal_type))
        if signal_type is None:
            if self.units_widget.currentText() in ['cm', 'mm']:
                self.signal_type = 'DIFF'
                if self.units_widget.currentText() == 'cm':
                    mag = self.scale_widget.value()
                elif self.units_widget.currentText() == 'mm':
                    mag = self.scale_widget.value() / 10
                else:
                    raise ValueError('Units widget value {units} is not recognized as a cameralength unit'.format(units=self.units_widget.currentText()))
            else:
                self.signal_type = 'IMG'
                if self.units_widget.currentText() == 'x':
                    mag = self.scale_widget.value()
                elif self.units_widget.currentText() == 'kx':
                    mag = self.scale_widget.value() * 1E3
                elif self.units_widget.currentText() == 'Mx':
                    mag = self.scale_widget.value() * 1E6
                else:
                    raise ValueError('Units widget value {units} is not recognized as a magnification unit'.format(units=self.units_widget.currentText()))
        else:
            self.signal_type = signal_type

        #Change to get acceleration voltage from spinboxes in future.
        if self.signal_type == 'DIFF':
            query = '`Acceleration Voltage (V)`==200000 & `Camera` == "Merlin" & `Nominal Cameralength (cm)` == @mag'
            calibration_matches = calibration_table.query(query)['Scale (1/nm)']
            scale_units = '1/nm'
            offset = 0.5
            name_prefix = 'k'
        elif self.signal_type == 'IMG':
            query = '`Acceleration Voltage (V)`==200000 & `Camera` == "Merlin" & `Nominal Magnification ()` == @mag'
            calibration_matches = calibration_table.query(query)['Scale (nm)']
            scale_units = 'nm'
            offset = 0.0
            name_prefix = ''
        else:
            raise ValueError('Could not determine signal type {signal_type} for {self!r}'.format(signal_type=signal_type, self=self))

        if len(calibration_matches) > 1:
            print('More than one calibration match was found ({n}). Using first match'.format(n=len(calibration_matches)))#Change to use most recent match
        elif len(calibration_matches) <= 0:
            print('No calibration match was found ({n})'.format(n=len(calibration_matches)))  # Change to use most recent match
            return False
        print(calibration_matches)
        scale = calibration_matches.iloc[0]
        print(scale)
        self.data.axes_manager[0].scale = float(scale)
        self.data.axes_manager[1].scale = float(scale)
        self.data.axes_manager[0].units = scale_units
        self.data.axes_manager[1].units = scale_units
        self.data.axes_manager[0].offset = offset*self.data.axes_manager[0].size*self.data.axes_manager[0].scale
        self.data.axes_manager[1].offset = offset * self.data.axes_manager[1].size * self.data.axes_manager[1].scale
        self.data.axes_manager[0].name = '{prefix}x'.format(prefix=name_prefix)
        self.data.axes_manager[1].name = '{prefix}y'.format(prefix=name_prefix)
        return True

class MainWindow(QtWidgets.QMainWindow):
    data_root = Path(r'C:\Users\emilc\OneDrive - NTNU\NORTEM\Merlin')
    fileListRefreshed = pyqtSignal([], [dict], name='fileListRefreshed')

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi(str(Path(__file__).parent / './source/QTCmibConverter/mibConverter/mainwindow.ui'), self)
        self.setWindowTitle('mib batch converter')

    @pyqtSlot(str, name='browseInputFile', result=str)
    def browseDirectory(self):
        options = QtWidgets.QFileDialog.Options()
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            None,
            "Select directory",
            str(self.data_root),
            options=options)
        return directory

    @pyqtSlot(dict, name='refreshFileList')
    def refreshFileList(self, files):

        # for i in reversed(range(self.fileListLayout.count())):
        #    self.fileListLayout.itemAt(i).widget().setParent(None)
        while self.fileListLayout.count():
            child = self.fileListLayout.takeAt(0)
            if child.widget():
                self.fileListLayout.removeWidget(child)
                child.hide()
                # child.widget().deleteLater()

        if not isinstance(files, dict):
            raise TypeError(
                'Only dict objects are accepted as "files", not {files} of type {t}'.format(files=files, t=type(files)))

        # Create headers
        for col, label in enumerate(
                ['#', 'Name', 'Dim', 'Data', 'Print', 'Plot', 'CL/Mag', 'Units', 'Exposure Time [ms]', 'Mode',
                 'Condenser Aperture']):
            widget = QtWidgets.QLabel(label)
            widget.adjustSize()
            self.fileListLayout.addWidget(widget, 0, col)

        for row, file_id in enumerate(files):
            file = files[file_id]
            if not isinstance(file, MIBDataFile):
                raise TypeError('file {file!r} is not MIBDataFile'.format(file=file))
            # Add file widgets into layout
            for col, label in enumerate(
                    [file_id, file.name, file.dimensions, file.data]):
                widget = QtWidgets.QLabel(str(label))
                widget.adjustSize()
                self.fileListLayout.addWidget(widget, row + 1, col)

            # Add widgets
            self.fileListLayout.addWidget(file.print_button, row + 1, 4)
            self.fileListLayout.addWidget(file.plot_button, row + 1, 5)
            self.fileListLayout.addWidget(file.scale_widget, row + 1, 6)
            self.fileListLayout.addWidget(file.units_widget, row + 1, 7)
            self.fileListLayout.addWidget(file.exposure_widget, row + 1, 8)
            self.fileListLayout.addWidget(file.mode_widget, row + 1, 9)
            self.fileListRefreshed.emit()
            self.fileListRefreshed[dict].emit(files)

    def plot_image(self, data):
        plot_window = PlotWindow(self)
        plot_window.show()
        plot_window.plot(data.inav[0].data)


class mibConverterModel(QObject):
    directoryChanged = pyqtSignal([], [str], name='directoryChanged')
    filesLoaded = pyqtSignal([], [dict], [int], name='filesLoaded')
    filesConverted = pyqtSignal([], [int], name='filesConverted')

    def __init__(self, *args, **kwargs):
        super(mibConverterModel, self).__init__(*args, **kwargs)
        self.directory = None
        self.files = None
        self.calibration_table = pd.read_excel(str(Path(__file__).parent / '../../Calibrations.xlsx'), engine='openpyxl')

    def set_directory(self, directory):
        """
        Sets the directory of the model
        :param directory: The path to the data files to convert
        :type directory: Union[str, Path]
        :return:
        """
        if not isinstance(directory, (str, Path)):
            raise TypeError()
        directory = Path(directory)
        if not directory.exists():
            raise DirectoryError('Path "{p}" does not exist.'.format(p=directory))
        if not directory.is_dir():
            raise DirectoryError('Path "{p}" is not a directory.'.format(p=directory))
        self.directory = directory
        self.directoryChanged.emit()
        self.directoryChanged[str].emit(str(self.directory))

    def get_filenames(self, directory=None):
        """
        Get the files in the directory.
        :param directory: The path to the directory to get files from. Optional. Default is `None`, in which case the preset directory will be used.
        :type directory: Union[str, Path]
        :return: A list of files with the .mib extension in the directory.
        :rtype: list
        """
        if directory is not None:
            self.set_directory(directory)
        if self.directory is not None:
            if not isinstance(self.directory, Path):
                raise DirectoryError('Directory must be type Path, not {t}'.format(t=type(self.directory)))
            filenames = list(self.directory.rglob('*.mib'))
            if len(filenames) <= 0:
                raise DirectoryError('No valid files in directory "{p}"'.format(p=self.directory))
            else:
                return filenames
        else:
            raise DirectoryError('No directory selected.')

    def load_files(self, directory=None):
        """
        Loads a datafile.
        :param directory: The path to the data file to be used. Optional. Default is `None`, and then the preset filename will be used.
        :type directory: str
        :type filename: Path
        :type filename: NoneType
        :return:
        """
        filenames = self.get_filenames(directory)
        self.files = {}
        for filenumber, filename in enumerate(filenames):
            self.files.update({filenumber: MIBDataFile(filename, parent=self.parent())})
            self.files[filenumber].calibrate(self.calibration_table)
        self.filesLoaded.emit()
        self.filesLoaded[dict].emit(self.files)
        self.filesLoaded[int].emit(len(self.files))

    def convert_files(self, formats, overwrite=True):
        """
        Converts the files into the given file formats
        :param formats: The file formats to convert the files into
        :type formats: Union[str, list]
        :return:
        """
        if isinstance(formats, str):
            formats = [formats]
        if not isinstance(formats, list):
            TypeError('File formats must be given as a list, not {formats} of type {t}'.format(formats=formats,
                                                                                               t=type(formats)))

        converted_files = 0
        if self.files is not None:
            for file_number in self.files:
                file = self.files[file_number]
                print('Converting file {file_number}: "{name}"'.format(file_number=file_number, name=file.name))
                file.save(formats, overwrite=overwrite)
                converted_files += 1
        else:
            raise FileError('{self!r} has no files to convert'.format(self=self))
        self.filesConverted.emit()
        self.filesConverted[int].emit(converted_files)


class mibConverterController(object):

    def __init__(self, view, model=None):
        """
        Create controller for the mibconverter gui
        :param view: The main gui window.
        :type view: MainWindow
        :param model: The model to control.
        :type model: mibConverterModel
        """
        self._view = view
        self._model = model

        self._view.browseButton.clicked.connect(lambda: self.browse_directory())
        self._view.pathEdit.returnPressed.connect(lambda: self._model.set_directory(self._view.pathEdit.text()))
        self._model.directoryChanged.connect(lambda: self._model.load_files())
        self._model.filesLoaded[dict].connect(self._view.refreshFileList)
        self._view.convertButton.clicked.connect(lambda: self._model.convert_files(
            [checkbox.text() for checkbox in self._view.conversionFormats.findChildren(QtWidgets.QCheckBox) if
             checkbox.isChecked()], overwrite=self._view.overwriteCheckBox.isChecked()))

    def browse_directory(self):
        directory = self._view.browseDirectory()
        self._view.pathEdit.setText(directory)
        self._model.set_directory(directory)


class PlotWindow(QtWidgets.QDialog):
    scale_bar_sizes = np.array(
        [0.01, 0.02, 0.05, 0.07, 0.1, 0.2, 0.5, 0.7, 1, 2, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 150, 200,
         250, 300, 350, 400, 450, 500])
    scale_bar_fraction = 1 / 5

    def __init__(self, parent=None):
        super(PlotWindow, self).__init__(parent)

        # a figure instance to plot on
        self.figure = plt.Figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # set the layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

        self.ax = self.figure.add_subplot(111)

    def plot(self, image, *args, log_scale=False, **kwargs):
        # create an axis

        # discards the old graph
        self.ax.clear()

        # plot data
        if log_scale:
            self.ax.imshow(np.log(image), *args, **kwargs)
        else:
            self.ax.imshow(image, *args, **kwargs)

        # Add Scalebar
        scale_x = image.axes_manager[0].scale
        scale_y = image.axes_manager[1].scale
        size_x = image.axes_manager[0].size
        size_y = image.axes_manager[1].size
        units = image.axes_manager[0].units
        scale_bar_length = self.scale_bar_sizes[
            np.argmin(np.abs(self.scale_bar_sizes - self.scale_bar_fraction * size_x * scale_x))]
        if scale_bar_length < 1:
            if scale_bar_length < 0.1:
                if scale_bar_length < 0.01:
                    if scale_bar_length < 0.001:
                        scalebar_label = '{scale_bar_length} {units}'.format(scale_bar_length=scale_bar_length, units=units)
                    else:
                        scalebar_label = '{scale_bar_length:.3f} {units}'.format(scale_bar_length=scale_bar_length, units=units)
                else:
                    scalebar_label = '{scale_bar_length:.2f} {units}'.format(scale_bar_length=scale_bar_length, units=units)
            else:
                scalebar_label = '{scale_bar_length:.1f} {units}'.format(scale_bar_length=scale_bar_length, units=units)
        else:
            scalebar_label = '{scale_bar_length:.0f} {units}'.format(scale_bar_length=scale_bar_length, units=units)

        xy = (0.01 * scale_x * size_x, 0.01 * scale_y * size_y)
        width = scale_bar_length
        height = 0.01 * scale_y * size_y
        patch = Rectangle(xy=xy, width=width, height=height, color='w')
        self.ax.add_patch(patch)
        self.ax.annotate(scalebar_label, xy=(xy[0] + width / 2, xy[1] + height), ha='center', va='bottom', color='w')

        # refresh canvas
        self.canvas.draw()


def run_converter_gui():
    main()


def main():
    """
    Intialize a standard GUI
    :return:
    """

    myqui = QtWidgets.QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    model = mibConverterModel(parent=main_window)
    controller = mibConverterController(main_window, model)

    sys.exit(myqui.exec_())


if __name__ == '__main__':
    main()
