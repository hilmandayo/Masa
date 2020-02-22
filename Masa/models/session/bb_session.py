from .session import Session

class BBSession(Session):
    def __init__(self, backward: bool = True):
        super().__init__()
        self.backward = backward

    def __call__(self, frame, index):
        self.run()

    def run(self, frame, idx):
        height, width = frame.shape[:2]


if __name__ == "__main__":
    vid = cv2.VideoCapture("/home/hilman_dayo/Documents/epipolar_track/video.mp4")
    algo = Algorithm("epipolar_data.txt")

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
