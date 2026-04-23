import imghdr
from typing import Tuple

import cv2
import numpy as np
from fastapi import UploadFile


class ImageInputService:
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    def validate_extension(self, filename: str) -> bool:
        filename_lower = filename.lower()
        return any(filename_lower.endswith(ext) for ext in self.ALLOWED_EXTENSIONS)

    async def read_image(self, file: UploadFile) -> Tuple[np.ndarray, bytes]:
        file_bytes = await file.read()

        if not file_bytes:
            raise ValueError("El archivo está vacío")

        detected_type = imghdr.what(None, h=file_bytes)
        if detected_type not in {"jpeg", "png", "bmp", "webp"}:
            raise ValueError("El archivo no es una imagen válida soportada")

        np_buffer = np.frombuffer(file_bytes, dtype=np.uint8)
        image = cv2.imdecode(np_buffer, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("No se pudo decodificar la imagen con OpenCV")

        return image, file_bytes

    def extract_image_info(self, image: np.ndarray) -> Tuple[int, int, int]:
        height, width = image.shape[:2]
        channels = image.shape[2] if len(image.shape) == 3 else 1
        return width, height, channels