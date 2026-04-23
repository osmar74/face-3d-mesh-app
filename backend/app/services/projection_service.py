import math
from typing import List

from backend.app.models.mesh_model import Vertex3D, Vertex2D


class ProjectionService:
    def __init__(self, distance: float = 500.0) -> None:
        self.distance = distance

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