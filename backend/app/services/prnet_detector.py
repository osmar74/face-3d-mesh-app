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
    def __init__(self) -> None:
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

        landmarks = self.prn.get_landmarks(pos)

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