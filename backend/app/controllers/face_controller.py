from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.app.config import settings
from backend.app.models.image_model import ImageInfoResponse
from backend.app.models.landmark_model import FaceLandmarksResponse
from backend.app.models.mesh_model import MeshData, Triangle, Vertex3D
from backend.app.models.scene_model import SceneConfig, SceneResponse
from backend.app.services.face_mesh_detector import FaceMeshDetector
from backend.app.services.image_input_service import ImageInputService
from backend.app.services.landmark_expansion_service import LandmarkExpansionService
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


@router.post("/upload-image", response_model=ImageInfoResponse)
async def upload_image(file: UploadFile = File(...)) -> ImageInfoResponse:
    image_service = ImageInputService()

    if not file.filename:
        raise HTTPException(status_code=400, detail="El archivo no tiene nombre")

    if not image_service.validate_extension(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Extensión no permitida. Usa JPG, JPEG, PNG, BMP o WEBP."
        )

    try:
        image, _ = await image_service.read_image(file)
        width, height, channels = image_service.extract_image_info(image)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno procesando la imagen: {str(error)}"
        ) from error

    return ImageInfoResponse(
        filename=file.filename,
        width=width,
        height=height,
        channels=channels,
        message="Imagen cargada y validada correctamente"
    )


@router.post("/detect-landmarks", response_model=FaceLandmarksResponse)
async def detect_landmarks(file: UploadFile = File(...)) -> FaceLandmarksResponse:
    image_service = ImageInputService()
    detector = FaceMeshDetector()
    expansion_service = LandmarkExpansionService()

    if not file.filename:
        raise HTTPException(status_code=400, detail="El archivo no tiene nombre")

    if not image_service.validate_extension(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Extensión no permitida. Usa JPG, JPEG, PNG, BMP o WEBP."
        )

    try:
        image, _ = await image_service.read_image(file)
        width, height, _ = image_service.extract_image_info(image)
        landmarks = detector.detect(image)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno detectando landmarks: {str(error)}"
        ) from error

    if not landmarks:
        raise HTTPException(
            status_code=404,
            detail="No se detectó ningún rostro en la imagen"
        )

    expanded_landmarks = expansion_service.expand(landmarks)

    return FaceLandmarksResponse(
        filename=file.filename,
        image_width=width,
        image_height=height,
        landmark_count=len(expanded_landmarks),
        landmarks=expanded_landmarks,
        message="Landmarks faciales detectados y expandidos correctamente"
    )