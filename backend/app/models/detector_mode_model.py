from enum import Enum


class DetectorMode(str, Enum):
    MEDIAPIPE = "mediapipe"
    PRNET = "prnet"