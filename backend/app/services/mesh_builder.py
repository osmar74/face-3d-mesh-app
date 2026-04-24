import math
from typing import List, Tuple

import numpy as np
from scipy.spatial import Delaunay

from backend.app.models.landmark_model import FaceLandmark


class MeshBuilder:
    def build(self, landmarks: List[FaceLandmark]) -> Tuple[np.ndarray, np.ndarray]:
        if not landmarks:
            raise ValueError("No hay landmarks para construir la malla")

        points_2d = np.array([[p.x, p.y] for p in landmarks], dtype=float)

        delaunay = Delaunay(points_2d)
        raw_triangles = delaunay.simplices

        min_x = np.min(points_2d[:, 0])
        max_x = np.max(points_2d[:, 0])
        min_y = np.min(points_2d[:, 1])
        max_y = np.max(points_2d[:, 1])

        center_x = (min_x + max_x) / 2.0
        center_y = (min_y + max_y) / 2.0

        face_width = max_x - min_x
        face_height = max_y - min_y

        # Elipse de contorno permitida
        ellipse_rx = face_width * 0.46
        ellipse_ry = face_height * 0.58

        # Límite de arista para evitar triángulos demasiado largos
        max_edge_length = max(face_width, face_height) * 0.11

        filtered_triangles = []

        for tri in raw_triangles:
            p1 = points_2d[tri[0]]
            p2 = points_2d[tri[1]]
            p3 = points_2d[tri[2]]

            d12 = self.distance(p1, p2)
            d23 = self.distance(p2, p3)
            d31 = self.distance(p3, p1)

            if d12 > max_edge_length or d23 > max_edge_length or d31 > max_edge_length:
                continue

            centroid = (p1 + p2 + p3) / 3.0

            if not self.is_inside_ellipse(
                centroid_x=centroid[0],
                centroid_y=centroid[1],
                center_x=center_x,
                center_y=center_y,
                radius_x=ellipse_rx,
                radius_y=ellipse_ry,
            ):
                continue

            filtered_triangles.append(tri)

        return points_2d, np.array(filtered_triangles, dtype=int)

    def distance(self, p1: np.ndarray, p2: np.ndarray) -> float:
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def is_inside_ellipse(
        self,
        centroid_x: float,
        centroid_y: float,
        center_x: float,
        center_y: float,
        radius_x: float,
        radius_y: float,
    ) -> bool:
        if radius_x <= 0 or radius_y <= 0:
            return False

        value = (
            ((centroid_x - center_x) ** 2) / (radius_x ** 2) +
            ((centroid_y - center_y) ** 2) / (radius_y ** 2)
        )
        return value <= 1.0