import math
from typing import List, Tuple

import numpy as np
from scipy.spatial import Delaunay

from backend.app.models.landmark_model import FaceLandmark
from backend.app.models.mesh_model import Triangle, Vertex3D


class MeshBuilder:
    def build(self, landmarks: List[FaceLandmark]) -> Tuple[np.ndarray, np.ndarray]:
        if not landmarks:
            raise ValueError("No hay landmarks para construir la malla")

        points_2d = np.array([[p.x, p.y] for p in landmarks], dtype=float)

        delaunay = Delaunay(points_2d)
        raw_triangles = delaunay.simplices

        filtered_triangles = self.filter_triangles(
            points=points_2d,
            triangles=raw_triangles,
            max_length_factor=0.12
        )

        return points_2d, np.array(filtered_triangles, dtype=int)

    def build_3d_mesh(self, landmarks: List[FaceLandmark]):
        points_2d, raw_triangles = self.build(landmarks)

        vertices = []
        triangles = []

        for point in landmarks:
            vertices.append(
                Vertex3D(
                    index=point.index,
                    x=float(point.x),
                    y=float(point.y),
                    z=float(point.z),
                )
            )

        for triangle in raw_triangles:
            triangles.append(
                Triangle(
                    a=int(triangle[0]),
                    b=int(triangle[1]),
                    c=int(triangle[2]),
                )
            )

        return vertices, triangles

    def filter_triangles(
        self,
        points: np.ndarray,
        triangles: np.ndarray,
        max_length_factor: float = 0.12
    ) -> List[np.ndarray]:
        if points.size == 0 or len(triangles) == 0:
            return []

        min_x = np.min(points[:, 0])
        max_x = np.max(points[:, 0])
        min_y = np.min(points[:, 1])
        max_y = np.max(points[:, 1])

        face_width = max_x - min_x
        face_height = max_y - min_y
        face_size = max(face_width, face_height)

        max_edge_length = face_size * max_length_factor

        filtered = []

        for tri in triangles:
            p1 = points[tri[0]]
            p2 = points[tri[1]]
            p3 = points[tri[2]]

            d12 = self.distance(p1, p2)
            d23 = self.distance(p2, p3)
            d31 = self.distance(p3, p1)

            if (
                d12 <= max_edge_length and
                d23 <= max_edge_length and
                d31 <= max_edge_length
            ):
                filtered.append(tri)

        return filtered

    def distance(self, p1: np.ndarray, p2: np.ndarray) -> float:
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)