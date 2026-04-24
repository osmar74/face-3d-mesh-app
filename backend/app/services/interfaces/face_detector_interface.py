from abc import ABC, abstractmethod
from typing import List
import numpy as np

from backend.app.models.landmark_model import FaceLandmark


class FaceDetectorInterface(ABC):
    @abstractmethod
    def detect(self, image_bgr: np.ndarray) -> List[FaceLandmark]:
        pass