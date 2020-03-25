from PySide2 import QtCore as qtc
import cv2

try:
    from .session import Session
except:
    import sys; from pathlib import Path
    _dir = Path(__file__).parent
    sys.path.append(str(_dir))
    from session import Session
from Masa.core.utils import SignalPacket


class BBSession(Session):
    added_tobj = qtc.Signal(SignalPacket)
    added_instance = qtc.Signal(SignalPacket)
    request_tobj = qtc.Signal(SignalPacket)

    def __init__(self, data_handler=None, backward: bool = True):
        super().__init__()
        self._dh = data_handler

    def set_data_handler(self, data_handler):
        self._dh = data_handler

    def __call__(self, frame, index):
        self.run(frame, idx)

    def add_tobj_r(self, packet: SignalPacket):
        self._dh.append(packet.data)

    def add_instance_r(self, packet: SignalPacket):
        self._dh.append(packet.data)
        

    def run(self, frame, idx):
        height, width = frame.shape[:2]

    def get_tobj(self, track_id):
        return self._dh[track_id]

if __name__ == "__main__":
    vid = cv2.VideoCapture("/home/hilman_dayo/Documents/epipolar_track/video.mp4")
    algo = BBSession()

    while True:
        _, frame = vid.read()
        for tl in algo.tl_line_orig:
            tl = tuple(tl)
            cv2.circle(frame, tl, 1, (0, 0, 255), 1)
        for br in algo.br_line_orig:
            br = tuple(br)
            cv2.circle(frame, br, 1, (0, 0, 255), 1)

        cv2.imshow("vid", frame)
        key = cv2.waitKey(0)
        if key == ord("q"):
            break
