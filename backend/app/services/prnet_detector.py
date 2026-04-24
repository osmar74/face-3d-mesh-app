import os
import sys
from typing import List

import cv2
import numpy as np
import torch
from torchvision import transforms

from backend.app.models.landmark_model import FaceLandmark
from backend.app.services.interfaces.face_detector_interface import FaceDetectorInterface


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

    def detect(self, image_bgr: np.ndarray) -> List[FaceLandmark]:
        if image_bgr is None or image_bgr.size == 0:
            raise ValueError("Imagen vacía")

        original_h, original_w = image_bgr.shape[:2]

        image_resized = cv2.resize(image_bgr, (256, 256))

        transformed_image = self.transform(image_resized)
        image_tensor = torch.as_tensor(transformed_image, dtype=torch.float32)
        image_tensor = image_tensor.unsqueeze(0)

        with torch.no_grad():
            pos = self.prn.net_forward(image_tensor)

        pos = pos.squeeze(0)
        pos = pos.permute(1, 2, 0)

        if self.output_mode == "dense":
            vertices = self.prn.get_vertices(pos)
            return self.convert_dense_vertices(vertices, original_w, original_h)

        landmarks = self.prn.get_landmarks(pos)
        return self.convert_landmarks(landmarks, original_w, original_h)

    def convert_landmarks(
        self,
        landmarks: np.ndarray,
        original_w: int,
        original_h: int
    ) -> List[FaceLandmark]:
        output: List[FaceLandmark] = []

        for index, point in enumerate(landmarks):
            x, y, z = point

            x_img = (float(x) / 256.0) * original_w
            y_img = (float(y) / 256.0) * original_h

            output.append(
                FaceLandmark(
                    index=index,
                    x=x_img,
                    y=y_img,
                    z=float(z),
                    source="prnet"
                )
            )

        return output

    def convert_dense_vertices(
        self,
        vertices: np.ndarray,
        original_w: int,
        original_h: int
    ) -> List[FaceLandmark]:
        output: List[FaceLandmark] = []

        max_points = 800
        step = max(1, len(vertices) // max_points)
        sampled_vertices = vertices[::step]
        z_values = [v[2] for v in sampled_vertices]
        z_min = min(z_values)
        z_max = max(z_values)

        for index, vertex in enumerate(sampled_vertices):
            x, y, z = vertex
            
            # Filtrar ruido por profundidad
            if z < z_min + 0.05 * (z_max - z_min):
                continue

            # Filtrar puntos fuera del rango válido
            if x < 0 or x > 256 or y < 0 or y > 256:
                continue

            x_img = (float(x) / 256.0) * original_w
            y_img = (float(y) / 256.0) * original_h

            output.append(
                FaceLandmark(
                    index=len(output),
                    x=x_img,
                    y=y_img,
                    z=float(z),
                    source="prnet_dense"
                )
            )

        return output