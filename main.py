import sys
from PySide2 import QtWidgets as qtw
from Masa.gui import VideoPlayer


if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    default = VideoPlayer("/home/hilman_dayo/Documents/youtube_videos/to_seki_with_takumi/IMG_1973.MOV",
                          width=640)
    default.show()

    sys.exit(app.exec_())
