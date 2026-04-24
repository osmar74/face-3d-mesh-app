import numpy as np
from typing import List

from backend.app.models.landmark_model import FaceLandmark
from backend.app.services.interfaces.face_detector_interface import FaceDetectorInterface


class PRNetFaceDetector(FaceDetectorInterface):
    def __init__(self) -> None:
        self.model = None
        self.is_ready = False

    def detect(self, image_bgr: np.ndarray) -> List[FaceLandmark]:
        raise NotImplementedError(
            "PRNet real todavía requiere adaptar el modelo clonado y sus pesos. "
            "PyTorch ya está instalado correctamente."
        )