import os
import sys
from typing import List, Tuple

import cv2
import numpy as np
import torch
from torchvision import transforms

from backend.app.models.landmark_model import FaceLandmark
from backend.app.services.interfaces.face_detector_interface import FaceDetectorInterface
from backend.app.services.mediapipe_face_detector import MediaPipeFaceDetector


class PRNetFaceDetector(FaceDetectorInterface):
    def __init__(self, output_mode: str = "landmarks") -> None:
        self.output_mode = output_mode

        self.prnet_path = os.path.join(os.getcwd(), "external", "prnet")
        self.model_path = os.path.join(self.prnet_path, "results", "latest.pth")

        if self.prnet_path not in sys.path:
            sys.path.append(self.prnet_path)

        from api import PRN  # type: ignore

        current_dir = os.getcwd()

        try:
            os.chdir(self.prnet_path)
            self.prn = PRN(self.model_path)
        finally:
            os.chdir(current_dir)

        self.transform = transforms.Compose([
            transforms.ToTensor()
        ])

        # MediaPipe se usa solo como apoyo para ubicar el rostro y recortarlo
        self.crop_detector = MediaPipeFaceDetector()

    def detect(self, image_bgr: np.ndarray) -> List[FaceLandmark]:
        if image_bgr is None or image_bgr.size == 0:
            raise ValueError("Imagen vacía")

        original_h, original_w = image_bgr.shape[:2]

        crop_box = self.get_face_crop_box(image_bgr)

        if crop_box is None:
            return []

        x1, y1, x2, y2 = crop_box

        face_crop = image_bgr[y1:y2, x1:x2]

        if face_crop.size == 0:
            return []

        crop_h, crop_w = face_crop.shape[:2]

        image_resized = cv2.resize(face_crop, (256, 256))

        transformed_image = self.transform(image_resized)
        image_tensor = torch.as_tensor(transformed_image, dtype=torch.float32)
        image_tensor = image_tensor.unsqueeze(0)

        with torch.no_grad():
            pos = self.prn.net_forward(image_tensor)

        pos = pos.squeeze(0)
        pos = pos.permute(1, 2, 0)

        if self.output_mode == "dense":
            vertices = self.prn.get_vertices(pos)
            return self.convert_dense_vertices(
                vertices=vertices,
                crop_x=x1,
                crop_y=y1,
                crop_w=crop_w,
                crop_h=crop_h,
                original_w=original_w,
                original_h=original_h
            )

        landmarks = self.prn.get_landmarks(pos)
        return self.convert_landmarks(
            landmarks=landmarks,
            crop_x=x1,
            crop_y=y1,
            crop_w=crop_w,
            crop_h=crop_h,
            original_w=original_w,
            original_h=original_h
        )

    def get_face_crop_box(self, image_bgr: np.ndarray) -> Tuple[int, int, int, int] | None:
        image_h, image_w = image_bgr.shape[:2]

        landmarks = self.crop_detector.detect(image_bgr)

        if not landmarks:
            return None

        min_x = min(point.x for point in landmarks)
        max_x = max(point.x for point in landmarks)
        min_y = min(point.y for point in landmarks)
        max_y = max(point.y for point in landmarks)

        face_w = max_x - min_x
        face_h = max_y - min_y

        margin_x = face_w * 0.25
        margin_y_top = face_h * 0.35
        margin_y_bottom = face_h * 0.18

        x1 = int(max(0, min_x - margin_x))
        y1 = int(max(0, min_y - margin_y_top))
        x2 = int(min(image_w, max_x + margin_x))
        y2 = int(min(image_h, max_y + margin_y_bottom))

        return x1, y1, x2, y2

    def convert_landmarks(
        self,
        landmarks: np.ndarray,
        crop_x: int,
        crop_y: int,
        crop_w: int,
        crop_h: int,
        original_w: int,
        original_h: int
    ) -> List[FaceLandmark]:
        output: List[FaceLandmark] = []

        for index, point in enumerate(landmarks):
            x, y, z = point

            if x < 0 or x > 256 or y < 0 or y > 256:
                continue

            x_img = crop_x + (float(x) / 256.0) * crop_w
            y_img = crop_y + (float(y) / 256.0) * crop_h

            if x_img < 0 or x_img > original_w or y_img < 0 or y_img > original_h:
                continue

            output.append(
                FaceLandmark(
                    index=len(output),
                    x=float(x_img),
                    y=float(y_img),
                    z=float(z),
                    source="prnet"
                )
            )

        return output

    def convert_dense_vertices(
        self,
        vertices: np.ndarray,
        crop_x: int,
        crop_y: int,
        crop_w: int,
        crop_h: int,
        original_w: int,
        original_h: int
    ) -> List[FaceLandmark]:
        output: List[FaceLandmark] = []

        max_points = 800
        step = max(1, len(vertices) // max_points)
        sampled_vertices = vertices[::step]

        z_values = [float(v[2]) for v in sampled_vertices]
        z_min = min(z_values)
        z_max = max(z_values)
        z_range = max(z_max - z_min, 1.0)

        for vertex in sampled_vertices:
            x, y, z = vertex

            if x < 0 or x > 256 or y < 0 or y > 256:
                continue

            # Filtro suave de ruido por profundidad
            if float(z) < z_min + 0.05 * z_range:
                continue

            x_img = crop_x + (float(x) / 256.0) * crop_w
            y_img = crop_y + (float(y) / 256.0) * crop_h

            if x_img < 0 or x_img > original_w or y_img < 0 or y_img > original_h:
                continue

            output.append(
                FaceLandmark(
                    index=len(output),
                    x=float(x_img),
                    y=float(y_img),
                    z=float(z),
                    source="prnet_dense"
                )
            )

        return output