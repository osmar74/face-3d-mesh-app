from typing import List

from backend.app.models.landmark_model import FaceLandmark


class LandmarkExpansionService:
    def expand(self, landmarks: List[FaceLandmark]) -> List[FaceLandmark]:
        if not landmarks:
            return []

        min_x = min(point.x for point in landmarks)
        max_x = max(point.x for point in landmarks)
        min_y = min(point.y for point in landmarks)
        max_y = max(point.y for point in landmarks)

        face_width = max_x - min_x
        face_height = max_y - min_y
        center_x = (min_x + max_x) / 2.0

        expanded_landmarks = list(landmarks)
        next_index = max(point.index for point in landmarks) + 1

        avg_z = sum(point.z for point in landmarks) / len(landmarks)

        # Frente más amplia y curva
        forehead_points = [
            (center_x - face_width * 0.34, min_y - face_height * 0.10),
            (center_x - face_width * 0.26, min_y - face_height * 0.18),
            (center_x - face_width * 0.18, min_y - face_height * 0.25),
            (center_x - face_width * 0.08, min_y - face_height * 0.31),
            (center_x,                   min_y - face_height * 0.34),
            (center_x + face_width * 0.08, min_y - face_height * 0.31),
            (center_x + face_width * 0.18, min_y - face_height * 0.25),
            (center_x + face_width * 0.26, min_y - face_height * 0.18),
            (center_x + face_width * 0.34, min_y - face_height * 0.10),
        ]

        # Laterales izquierdos: mejor aproximación a zona de oreja/costado
        left_side_points = [
            (min_x - face_width * 0.10, min_y + face_height * 0.16),
            (min_x - face_width * 0.14, min_y + face_height * 0.28),
            (min_x - face_width * 0.16, min_y + face_height * 0.40),
            (min_x - face_width * 0.15, min_y + face_height * 0.52),
            (min_x - face_width * 0.12, min_y + face_height * 0.66),
            (min_x - face_width * 0.08, min_y + face_height * 0.80),
        ]

        # Laterales derechos: simétricos
        right_side_points = [
            (max_x + face_width * 0.10, min_y + face_height * 0.16),
            (max_x + face_width * 0.14, min_y + face_height * 0.28),
            (max_x + face_width * 0.16, min_y + face_height * 0.40),
            (max_x + face_width * 0.15, min_y + face_height * 0.52),
            (max_x + face_width * 0.12, min_y + face_height * 0.66),
            (max_x + face_width * 0.08, min_y + face_height * 0.80),
        ]

        # Mejora de contorno inferior-lateral para que no se vea tan recortado
        lower_side_points = [
            (center_x - face_width * 0.26, max_y - face_height * 0.02),
            (center_x - face_width * 0.14, max_y + face_height * 0.01),
            (center_x,                     max_y + face_height * 0.02),
            (center_x + face_width * 0.14, max_y + face_height * 0.01),
            (center_x + face_width * 0.26, max_y - face_height * 0.02),
        ]

        synthetic_points = (
            forehead_points +
            left_side_points +
            right_side_points +
            lower_side_points
        )

        for x_value, y_value in synthetic_points:
            expanded_landmarks.append(
                FaceLandmark(
                    index=next_index,
                    x=float(x_value),
                    y=float(y_value),
                    z=float(avg_z),
                    source="synthetic"
                )
            )
            next_index += 1

        return expanded_landmarks