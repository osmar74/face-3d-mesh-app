from typing import List

from backend.app.models.landmark_model import FaceLandmark


class LandmarkExpansionService:
    def expand(self, landmarks: List[FaceLandmark]) -> List[FaceLandmark]:
        return list(landmarks)