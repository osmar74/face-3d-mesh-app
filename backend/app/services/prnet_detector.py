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

        image_resized = cv2.resize(image_bgr, (256, 256))

        image_tensor = torch.as_tensor(self.transform(image_resized), dtype=torch.float32)
        image_tensor = image_tensor.unsqueeze(0)

        with torch.no_grad():
            pos = self.prn.net_forward(image_tensor)

        vertices = self.prn.get_vertices(pos)

        output: List[FaceLandmark] = []

        for index, vertex in enumerate(vertices):
            x, y, z = vertex

            output.append(
                FaceLandmark(
                    index=index,
                    x=float(x),
                    y=float(y),
                    z=float(z),
                    source="prnet"
                )
            )

        return output