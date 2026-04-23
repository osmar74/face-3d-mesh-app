from pydantic import BaseModel, Field
from typing import List


class FaceLandmark(BaseModel):
    index: int
    x: float
    y: float
    z: float
    source: str = "detected"


class FaceLandmarksResponse(BaseModel):
    filename: str
    image_width: int
    image_height: int
    landmark_count: int
    landmarks: List[FaceLandmark] = Field(default_factory=list)
    message: str