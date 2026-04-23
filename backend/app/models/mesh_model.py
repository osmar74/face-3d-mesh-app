from pydantic import BaseModel, Field
from typing import List


class Vertex3D(BaseModel):
    x: float
    y: float
    z: float


class Vertex2D(BaseModel):
    x: float
    y: float


class Triangle(BaseModel):
    a: int
    b: int
    c: int


class MeshData(BaseModel):
    vertices: List[Vertex3D] = Field(default_factory=list)
    projected_vertices: List[Vertex2D] = Field(default_factory=list)
    triangles: List[Triangle] = Field(default_factory=list)