import argparse
import sys
from pathlib import Path

from PySide2 import QtWidgets as qtw
from Masa.gui.widgets.video_player import VideoPlayer
from Masa.apps.default import ImageExtractorApp
from data_processing.data_prepare import prepare_data


parser = argparse.ArgumentParser()
parser.add_argument("--dataid" "-d", default=None)
parser.add_argument("--prepare-data", "-p",
                    help="Prepare data for a Data ID", default=None)

args = vars(parser.parse_args())

if __name__ == "__main__":
    if args["prepare_data"]:
        prepare_data(args["prepare_data"])
        sys.exit(0)

    path = Path(args["dataid"])
    if not path.exists():
        raise ValueError(f"Cannot found {path}.")

    app = qtw.QApplication(sys.argv)
    iea = ImageExtractorApp(path)
    iea.show()

    sys.exit(app.exec_())
