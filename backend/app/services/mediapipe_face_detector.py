import cv2
import mediapipe as mp
import numpy as np
from typing import List

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from backend.app.config import settings
from backend.app.models.landmark_model import FaceLandmark
from backend.app.services.interfaces.face_detector_interface import FaceDetectorInterface


class MediaPipeFaceDetector(FaceDetectorInterface):
    def __init__(self) -> None:
        base_options = python.BaseOptions(
            model_asset_path=settings.FACE_LANDMARKER_MODEL_PATH
        )

        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
            num_faces=1
        )

        self.detector = vision.FaceLandmarker.create_from_options(options)

    def detect(self, image_bgr: np.ndarray) -> List[FaceLandmark]:
        if image_bgr is None or image_bgr.size == 0:
            raise ValueError("La imagen de entrada está vacía")

        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        height, width = image_rgb.shape[:2]

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=image_rgb
        )

        result = self.detector.detect(mp_image)

        if not result.face_landmarks:
            return []

        face_landmarks = result.face_landmarks[0]
        output_landmarks: List[FaceLandmark] = []

        for index, landmark in enumerate(face_landmarks):
            x_px = landmark.x * width
            y_px = landmark.y * height
            z_rel = landmark.z * width

            output_landmarks.append(
                FaceLandmark(
                    index=index,
                    x=float(x_px),
                    y=float(y_px),
                    z=float(z_rel),
                    source="detected"
                )
            )

        return output_landmarks