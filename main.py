import sys
from PySide2 import QtWidgets as qtw
from Masa.gui.widgets.video_player import VideoPlayer
from Masa.models.datahandler import DataHandler
from Masa.apps.default import ImageExtractorApp


if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    data_handler = DataHandler("/home/hilman_dayo/dummy.csv")
    iea = ImageExtractorApp(data_handler)
    # default = VideoPlayer("/home/hilman_dayo/Documents/youtube_videos/to_seki_with_takumi/IMG_1973.MOV",
    #                       data_handler,
    #                       width=640)
    # default.show()
    iea.show()

    sys.exit(app.exec_())
