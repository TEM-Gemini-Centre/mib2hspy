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

from mib2hspy.Tools.hdrtools import MedipixHDRcontent


class Error(Exception):
    pass


class DirectoryError(Error):
    pass


class FileError(Error):
    pass


class MainWindow(QtWidgets.QMainWindow):
    data_root = Path(r'C:\Users\emilc\OneDrive - NTNU\NORTEM\Merlin')

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

        for i in reversed(range(self.fileListLayout.count())):
            self.fileListLayout.itemAt(i).widget().setParent(None)

        if not isinstance(files, dict):
            raise TypeError(
                'Only dict objects are accepted as "files", not {files} of type {t}'.format(files=files, t=type(files)))

        # Create headers
        for col, label in enumerate(
                ['#', 'Name', 'Dim', 'Data', 'Print', 'Plot', 'CL/Mag', 'Units', 'Exposure Time [ms]', 'Mode', 'Condenser Aperture']):
            widget = QtWidgets.QLabel(label)
            widget.adjustSize()
            self.fileListLayout.addWidget(widget, 0, col)

        for row, file_id in enumerate(files):
            file_info = files[file_id]

            # Add file info fields
            for col, label in enumerate([file_id, file_info['Name'], file_info['Dimensions'], file_info['Data']]):
                widget = QtWidgets.QLabel(str(label))
                widget.adjustSize()
                self.fileListLayout.addWidget(widget, row + 1, col)

            # Add print button
            print_btn = QtWidgets.QPushButton('Print')
            print_btn.clicked.connect(lambda: print('"{name}" ({data}):\n***Axes Manager***\n{data.axes_manager}\n\n***Metadata***\n{data.metadata}\n\n***Original Metadata***\n{data.original_metadata}\n\n'.format(name=file_info['Name'], data=file_info['Data'])))
            self.fileListLayout.addWidget(print_btn, row + 1, 4)

            # Add Plot button
            plot_btn = QtWidgets.QPushButton('Plot')
            plot_btn.clicked.connect(lambda: self.plot_image(file_info['Data']))
            self.fileListLayout.addWidget(plot_btn, row + 1, 5)

            #Attempt to extract info from filename
            split_name = file_info['Name'].split('_')
            scale = 0
            units = 'cm'
            for part in split_name:
                if 'kx' in part:
                    scale = float(part.replace('kx', ''))
                    units = 'kx'
                if 'Mx' in part:
                    scale = float(part.replace('Mx', ''))
                    units = 'Mx'
                if 'cm' in part:
                    scale = float(part.replace('cm', ''))
                    units = 'cm'

            # Add metadata fields
            # Create and add scale widget
            scale_widget = QtWidgets.QDoubleSpinBox()
            scale_widget.setMinimum(0)
            scale_widget.setMaximum(999.999)
            scale_widget.setDecimals(3)
            scale_widget.setSingleStep(0.1)
            scale_widget.setValue(scale)
            file_info['ScaleWidget'] = scale_widget
            self.fileListLayout.addWidget(scale_widget, row + 1, 6)

            # Add units selector
            units_widget = QtWidgets.QComboBox()
            units_widget.addItems(['cm', 'mm', 'kx', 'Mx'])
            units_widget.setCurrentText(units)
            file_info['UnitsWidget'] = units_widget
            self.fileListLayout.addWidget(units_widget, row + 1, 7)

            # Add exposuretime counter [WILL BE REMOVED]
            exptime_widget = QtWidgets.QSpinBox()
            exptime_widget.setMinimum(0)
            exptime_widget.setMaximum(int(1E9))
            exptime_widget.setValue(0)
            exptime_widget.setSingleStep(1)
            file_info['ExposureTimeWidget'] = exptime_widget
            self.fileListLayout.addWidget(exptime_widget, row + 1, 8)

            # Add mode selector
            mode_widget = QtWidgets.QComboBox()
            mode_widget.addItems(['None', 'TEM', 'NBD', 'CBD'])
            mode_widget.setCurrentIndex(0)
            file_info['ModeWidget'] = mode_widget
            self.fileListLayout.addWidget(mode_widget, row + 1, 9)

            # Add convergence angle spinbox
            condenser_aperture_widget = QtWidgets.QComboBox()
            condenser_aperture_widget.addItems(['None', '1', '2', '3', '4'])
            file_info['CondenserApertureWidget'] = condenser_aperture_widget
            self.fileListLayout.addWidget(condenser_aperture_widget, row + 1, 10)

    def plot_image(self, data):
        plot_window = PlotWindow(self)
        plot_window.show()
        plot_window.plot(data.inav[0].data)

class mibConverterModel(QObject):
    directoryChanged = pyqtSignal([], [str], name='directoryChanged')
    filesLoaded = pyqtSignal([], [dict], [int], name='filesLoaded')
    filesConverted = pyqtSignal([], [int], name='filesConverted')

    def __init__(self):
        super(mibConverterModel, self).__init__()
        self.directory = None
        self.files = None

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
            data = pxm.load_mib(str(filename))
            if filename.with_suffix('.hdr').exists():
                header = MedipixHDRcontent(filename.with_suffix('.hdr'))
                header.load_hdr()
            else:
                header = None
            self.files[filenumber] = {'Path': filename, 'Name': filename.stem, 'Data': data, 'Dimensions': len(data),
                                      'Header': header}
        self.filesLoaded.emit()
        self.filesLoaded[dict].emit(self.files)
        self.filesLoaded[int].emit(len(self.files))

    def convert_files(self, formats):
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
                print('Converting file {file_number}: "{name}"'.format(file_number=file_number, name=file['Name']))
                for file_format in formats:
                    new_filename = file['Path'].with_suffix(file_format)
                    if file_format in ['.jpg', '.png', '.bmp']:
                        file['Data'].plot()
                        fig = plt.gcf()
                        fig.savefig(new_filename)
                        plt.close(fig)
                    else:
                        file['Data'].save(new_filename)
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
             checkbox.isChecked()]))

    def browse_directory(self):
        directory = self._view.browseDirectory()
        self._view.pathEdit.setText(directory)
        self._model.set_directory(directory)


class PlotWindow(QtWidgets.QDialog):
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

    def plot(self, image):
        # create an axis
        ax = self.figure.add_subplot(111)

        # discards the old graph
        ax.clear()

        # plot data
        ax.imshow(image)

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

    model = mibConverterModel()
    controller = mibConverterController(main_window, model)

    sys.exit(myqui.exec_())


if __name__ == '__main__':
    main()
