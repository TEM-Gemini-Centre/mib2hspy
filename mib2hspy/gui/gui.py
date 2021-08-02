from .stack_converter import ConverterView, ConverterModel, ConverterController
from .frame_converter import FrameConverterWindow, mibConverterModel, mibConverterController
from pathlib import Path
from PyQt5 import uic, QtWidgets
from mib2hspy.gui.guiTools import QTextEditLogger
import sys
from datetime import datetime
import logging


class ConverterMainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(ConverterMainWindow, self).__init__(*args, **kwargs)
        uic.loadUi(str(Path(__file__).parent / './source/mib2hspy/mainwindow.ui'), self)
        self.setWindowTitle('mib2hspy converter')

        # Create debug file if not provided
        now = datetime.now()
        debug_file = Path('./logs/{stamp}_debug.log'.format(stamp=now.strftime('%Y-%m-%d-%H-%M-%S')))
        debug_file.parent.mkdir(parents=True, exist_ok=True)
        with open(debug_file, 'w') as f:
            f.close()
        print(debug_file.absolute())

        # Setup logging
        logformat = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fileHandler = logging.FileHandler(str(debug_file))
        fileHandler.setFormatter(logformat)
        logging.getLogger().addHandler(fileHandler)
        logging.getLogger().setLevel(logging.INFO)
        logging.getLogger().addHandler((logging.StreamHandler(sys.stdout)))

        handler = QTextEditLogger(widget=self.logView)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(handler)

        self.frame_converter_window = FrameConverterWindow()
        self.frame_model = mibConverterModel(parent=self.frame_converter_window)
        self.frame_controller = mibConverterController(self.frame_converter_window, self.frame_model)

        self.stack_converter_window = ConverterView()
        self.stack_model = ConverterModel()
        self.stack_controller = ConverterController(self.stack_converter_window, self.stack_model)

        self.frameConverterButton.clicked.connect(self.frame_converter_window.show)
        self.stackConverterButton.clicked.connect(self.stack_converter_window.show)
        self.quitButton.clicked.connect(self.close())

def gui():
    main()


def main():
    myqui = QtWidgets.QApplication(sys.argv)
    window = ConverterMainWindow()
    window.show()

    sys.exit(myqui.exec_())


if __name__ == '__main__':
    main()
