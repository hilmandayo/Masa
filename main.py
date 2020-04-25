import argparse
import sys
from pathlib import Path

from PySide2 import QtWidgets as qtw
from Masa.gui.widgets.video_player import VideoPlayer
from Masa.apps.default import ImageExtractorApp


parser = argparse.ArgumentParser()
parser.add_argument("dataid")
args = vars(parser.parse_args())

if __name__ == "__main__":
    path = Path(args["dataid"])
    if not path.exists():
        raise ValueError(f"Cannot found {path}.")

    app = qtw.QApplication(sys.argv)
    iea = ImageExtractorApp(path)
    iea.show()

    sys.exit(app.exec_())
