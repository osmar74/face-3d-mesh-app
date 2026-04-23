import math
from typing import List

from backend.app.models.mesh_model import Vertex2D, Vertex3D


class ProjectionService:
    def __init__(self, distance: float = 500.0) -> None:
        self.distance = distance

    def normalize_vertices(self, vertices: List[Vertex3D]) -> List[Vertex3D]:
        if not vertices:
            return []

        min_x = min(v.x for v in vertices)
        max_x = max(v.x for v in vertices)
        min_y = min(v.y for v in vertices)
        max_y = max(v.y for v in vertices)
        min_z = min(v.z for v in vertices)
        max_z = max(v.z for v in vertices)

        center_x = (min_x + max_x) / 2.0
        center_y = (min_y + max_y) / 2.0
        center_z = (min_z + max_z) / 2.0

        scale = max(max_x - min_x, max_y - min_y, max_z - min_z, 1.0)

        normalized = []
        for vertex in vertices:
            normalized.append(
                Vertex3D(
                    x=(vertex.x - center_x) / scale * 300.0,
                    y=(vertex.y - center_y) / scale * 300.0,
                    z=(vertex.z - center_z) / scale * 300.0,
                )
            )

        return normalized

    def rotate_and_project(
        self,
        vertices: List[Vertex3D],
        rotation_a: float,
        rotation_b: float
    ) -> List[Vertex2D]:
        projected_vertices: List[Vertex2D] = []

        cos_a = math.cos(rotation_a)
        sin_a = math.sin(rotation_a)
        cos_b = math.cos(rotation_b)
        sin_b = math.sin(rotation_b)

        for vertex in vertices:
            x = vertex.x
            y = vertex.y
            z = vertex.z

            xt = x * cos_a - z * sin_a
            yt = y * cos_b - z * cos_a * sin_b - x * sin_a * sin_b
            zt = z * cos_a * cos_b + x * sin_a * cos_b + y * sin_b

            denominator = self.distance - zt
            if abs(denominator) < 1e-6:
                denominator = 1e-6

            xp = self.distance * xt / denominator
            yp = self.distance * yt / denominator

            projected_vertices.append(Vertex2D(x=xp, y=yp))

        return projected_vertices