from typing import List, Dict

from backend.app.models.landmark_model import FaceLandmark
from backend.app.models.mesh_model import Triangle


class MeshRefinementService:
    def smooth_landmarks(
        self,
        landmarks: List[FaceLandmark],
        triangles: List[Triangle],
        iterations: int = 2,
        strength: float = 0.45
    ) -> List[FaceLandmark]:
        if not landmarks or not triangles:
            return landmarks

        smoothed = [
            FaceLandmark(
                index=p.index,
                x=p.x,
                y=p.y,
                z=p.z,
                source=p.source
            )
            for p in landmarks
        ]

        neighbors = self.build_neighbors(triangles)

        for _ in range(iterations):
            next_points = []

            for point in smoothed:
                point_neighbors = neighbors.get(point.index, [])

                if not point_neighbors:
                    next_points.append(point)
                    continue

                avg_x = sum(smoothed[i].x for i in point_neighbors) / len(point_neighbors)
                avg_y = sum(smoothed[i].y for i in point_neighbors) / len(point_neighbors)
                avg_z = sum(smoothed[i].z for i in point_neighbors) / len(point_neighbors)

                next_points.append(
                    FaceLandmark(
                        index=point.index,
                        x=point.x * (1 - strength) + avg_x * strength,
                        y=point.y * (1 - strength) + avg_y * strength,
                        z=point.z * (1 - strength) + avg_z * strength,
                        source=point.source
                    )
                )

            smoothed = next_points

        return smoothed

    def build_neighbors(self, triangles: List[Triangle]) -> Dict[int, List[int]]:
        neighbors = {}

        for tri in triangles:
            faces = [(tri.a, tri.b), (tri.b, tri.c), (tri.c, tri.a)]

            for a, b in faces:
                neighbors.setdefault(a, set()).add(b)
                neighbors.setdefault(b, set()).add(a)

        return {key: list(value) for key, value in neighbors.items()}