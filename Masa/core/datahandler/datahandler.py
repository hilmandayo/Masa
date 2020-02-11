from pathlib import Path
from typing import Union
import csv


class DataHandler:
    """Represent the saved data.

    Data from buffer extraction process will be saved in some format (csv, xml,
    etc.). This class will (eventually) abstract and handle all of the data
    format. An instance of this class will represent one file/directory group
    of a particular data.
    """
    def __init__(self, input_file: Union[str, Path]):
        self.input_file = Path(input_file)


    @staticmethod
    def _read_csv(input_file: str):
        retval = {}

        with open(input_file, mode="r") as f_csv:
            csv_reader = csv.DictReader(f_csv)
            line_count = 0
            for row in csv_reader:
                retval[int(row["track_id"])]
