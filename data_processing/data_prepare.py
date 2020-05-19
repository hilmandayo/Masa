"""Prepare data"""


import argparse
from pathlib import Path
import cv2
import pandas as pd
from shutil import rmtree

import brambox as bb
from data_processing import parser


def prepare_data(dir_input):
    dir_input = Path(dir_input)
    if not dir_input.exists():
        raise ValueError(f"{dir_input} is not exists.")

    csv_files = list(dir_input.rglob("annotations.csv"))
    for csv_file in csv_files:
        data_dir = csv_file.parent.parent / "data"
        video_file = list(data_dir.rglob("*.mp4"))
        if len(video_file) != 1:
            print(f"Skipping {data_id}. Probably problematic")
            continue

        video_file = video_file[0]
        try:
            images = extract_data(video_file, csv_file)
        except pd.errors.EmptyDataError:
            continue

        extracted_dir = data_dir / ".extracted"
        if extracted_dir.exists():
            rmtree(extracted_dir)
        extracted_dir.mkdir()

        save_images(images, extracted_dir)

    annos = bb.io.load(parser.RoadSceneAnnotationParser, csv_files, lambda x:x)
    bb.io.save(annos, "pandas", dir_input.with_suffix(".h5"))

    print(f"Data {dir_input} prepared successfully!")


def extract_data(video_file, csv_file) -> dict:
    video = cv2.VideoCapture(str(video_file))
    csv = pd.read_csv(csv_file)

    images = {}
    for idx, data in csv.iterrows():
        frame_id = data["frame_id"]
        if frame_id in images:
            continue

        video.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
        frame = video.read()[1]
        images[frame_id] = frame

    return images

def save_images(images, directory):
    for frame_id, image in images.items():
        cv2.imwrite(str(directory / f"{frame_id}.jpg"), image)

if __name__ == '__main__':
    main()
