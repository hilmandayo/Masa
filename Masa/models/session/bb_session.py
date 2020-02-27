import cv2

try:
    from .session import Session
except:
    import sys; from pathlib import Path
    _dir = Path(__file__).parent
    sys.path.append(str(_dir))
    from session import Session

class BBSession(Session):
    def __init__(self, data_handler, backward: bool = True):
        super().__init__()
        self.backward = backward
        self.data_handler = data_handler

    def __call__(self, frame, index):
        self.run()

    def run(self, frame, idx):
        height, width = frame.shape[:2]


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
