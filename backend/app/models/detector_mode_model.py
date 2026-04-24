from enum import Enum


class DetectorMode(str, Enum):
    MEDIAPIPE = "mediapipe"
    PRNET = "prnet"


class PRNetOutputMode(str, Enum):
    LANDMARKS = "landmarks"
    DENSE = "dense"