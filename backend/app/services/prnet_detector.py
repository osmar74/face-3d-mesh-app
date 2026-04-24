import numpy as np
from typing import List

from backend.app.models.landmark_model import FaceLandmark
from backend.app.services.interfaces.face_detector_interface import FaceDetectorInterface


class PRNetFaceDetector(FaceDetectorInterface):
    def __init__(self) -> None:
        pass

    def detect(self, image_bgr: np.ndarray) -> List[FaceLandmark]:
        raise NotImplementedError(
            "PRNet todavía no está integrado. Esta clase es un placeholder para la Fase 2."
        )