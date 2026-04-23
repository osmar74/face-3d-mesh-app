from pydantic import BaseModel
from backend.app.models.mesh_model import MeshData


class SceneConfig(BaseModel):
    rotation_a: float = 0.0
    rotation_b: float = 0.0
    distance: float = 500.0


class SceneResponse(BaseModel):
    scene: SceneConfig
    mesh: MeshData
    message: str