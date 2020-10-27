import logging
import sys
from datetime import datetime
from pathlib import Path


class LogStream(object):
    def __init__(self, logger, log_level=logging.DEBUG):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())


def main():
    now = datetime.now()
    # Create debug file
    debug_file = Path('./logs/{stamp}_debug.log'.format(stamp=now.strftime('%Y-%m-%d_%H:%M:%S')))
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
    sys.stdout = LogStream(logging.getLogger(), logging.DEBUG)
    sys.stderr = LogStream(logging.getLogger(), logging.ERROR)

    # app = QtWidgets.QApplication(sys.argv)
    # window = MainWindow()
    # window.show()
    # window.activateWindow()
    # window.raise_()
    # sys.exit(app.exec())


if __name__ == '__main__':
    main()
