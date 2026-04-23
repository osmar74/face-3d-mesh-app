from fastapi import APIRouter

from backend.app.config import settings
from backend.app.models.mesh_model import MeshData, Triangle, Vertex3D
from backend.app.models.scene_model import SceneConfig, SceneResponse
from backend.app.services.projection_service import ProjectionService

router = APIRouter(prefix="/face", tags=["face"])


@router.get("/demo-scene", response_model=SceneResponse)
def get_demo_scene() -> SceneResponse:
    vertices = [
        Vertex3D(x=-100.0, y=-100.0, z=0.0),
        Vertex3D(x=100.0, y=-100.0, z=0.0),
        Vertex3D(x=0.0, y=100.0, z=50.0),
        Vertex3D(x=0.0, y=0.0, z=120.0),
    ]

    triangles = [
        Triangle(a=0, b=1, c=2),
        Triangle(a=0, b=2, c=3),
        Triangle(a=1, b=2, c=3),
    ]

    scene = SceneConfig(
        rotation_a=settings.DEFAULT_ROTATION_A,
        rotation_b=settings.DEFAULT_ROTATION_B,
        distance=settings.DEFAULT_DISTANCE,
    )

    projection_service = ProjectionService(distance=scene.distance)
    projected_vertices = projection_service.rotate_and_project(
        vertices=vertices,
        rotation_a=scene.rotation_a,
        rotation_b=scene.rotation_b,
    )

    mesh = MeshData(
        vertices=vertices,
        projected_vertices=projected_vertices,
        triangles=triangles,
    )

    return SceneResponse(
        scene=scene,
        mesh=mesh,
        message="Escena de prueba generada correctamente",
    )