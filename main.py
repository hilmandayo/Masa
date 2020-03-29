import sys
from PySide2 import QtWidgets as qtw
from Masa.gui import VideoPlayer
from Masa.models.datahandler import DataHandler


if __name__ == "__main__":
    data_handler = DataHandler("/home/hilman_dayo/dummy.csv")
    app = qtw.QApplication(sys.argv)
    default = VideoPlayer("/home/hilman_dayo/Documents/youtube_videos/to_seki_with_takumi/IMG_1973.MOV",
                          data_handler,
                          width=640)
    default.show()

    sys.exit(app.exec_())
