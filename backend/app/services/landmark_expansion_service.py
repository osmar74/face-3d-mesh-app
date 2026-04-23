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

        forehead_y_1 = min_y - face_height * 0.12
        forehead_y_2 = min_y - face_height * 0.22

        forehead_points = [
            (center_x - face_width * 0.30, forehead_y_1),
            (center_x - face_width * 0.15, forehead_y_2),
            (center_x, forehead_y_2 - face_height * 0.03),
            (center_x + face_width * 0.15, forehead_y_2),
            (center_x + face_width * 0.30, forehead_y_1),
        ]

        left_side_points = [
            (min_x - face_width * 0.06, min_y + face_height * 0.25),
            (min_x - face_width * 0.08, min_y + face_height * 0.45),
            (min_x - face_width * 0.06, min_y + face_height * 0.65),
        ]

        right_side_points = [
            (max_x + face_width * 0.06, min_y + face_height * 0.25),
            (max_x + face_width * 0.08, min_y + face_height * 0.45),
            (max_x + face_width * 0.06, min_y + face_height * 0.65),
        ]

        synthetic_points = forehead_points + left_side_points + right_side_points

        avg_z = sum(point.z for point in landmarks) / len(landmarks)

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