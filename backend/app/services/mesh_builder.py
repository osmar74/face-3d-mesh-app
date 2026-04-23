import numpy as np
from scipy.spatial import Delaunay
from typing import List, Tuple

from backend.app.models.landmark_model import FaceLandmark


class MeshBuilder:
    def build(self, landmarks: List[FaceLandmark]) -> Tuple[np.ndarray, np.ndarray]:
        if not landmarks:
            raise ValueError("No hay landmarks para construir la malla")

        points_2d = np.array([[p.x, p.y] for p in landmarks])

        delaunay = Delaunay(points_2d)

        triangles = delaunay.simplices  # índices de triángulos

        return points_2d, triangles