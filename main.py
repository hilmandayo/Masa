import sys
from PySide2 import QtWidgets as qtw
from Masa.gui.widgets import VideoPlayer


if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    default = VideoPlayer("/dayo/sompo/nikaime/douga_raw/NEW_mp4/0000000001_20130101_210023_001.mp4",
                          width=640)
    default.show()

    sys.exit(app.exec_())
