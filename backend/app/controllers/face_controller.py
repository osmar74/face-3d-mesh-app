from fastapi import Form
from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.app.config import settings
from backend.app.models.image_model import ImageInfoResponse
from backend.app.models.landmark_model import FaceLandmarksResponse
from backend.app.models.mesh_model import (
    MeshData,
    MeshResponse,
    Triangle,
    Vertex,
    Vertex3D,
)
from backend.app.models.scene_model import SceneConfig, SceneResponse
from backend.app.models.detector_mode_model import DetectorMode
from backend.app.services.detector_factory import DetectorFactory
from backend.app.services.image_input_service import ImageInputService
from backend.app.services.landmark_expansion_service import LandmarkExpansionService
from backend.app.services.mesh_builder import MeshBuilder
from backend.app.services.projection_service import ProjectionService

from backend.app.models.mesh_model import (
    MeshData,
    MeshResponse,
    Triangle,
    Vertex,
    Vertex3D,
)

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
    detector = DetectorFactory.create(DetectorMode.MEDIAPIPE)
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

@router.post("/triangulate", response_model=MeshResponse)
async def triangulate(file: UploadFile = File(...)) -> MeshResponse:
    image_service = ImageInputService()
    detector = DetectorFactory.create(DetectorMode.MEDIAPIPE)
    expansion_service = LandmarkExpansionService()
    mesh_builder = MeshBuilder()

    try:
        image, _ = await image_service.read_image(file)
        landmarks = detector.detect(image)

        if not landmarks:
            raise HTTPException(status_code=404, detail="No se detectó rostro")

        expanded_landmarks = expansion_service.expand(landmarks)

        points_2d, triangles = mesh_builder.build(expanded_landmarks)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    vertices = [
        Vertex(x=p.x, y=p.y, z=p.z)
        for p in expanded_landmarks
    ]

    triangle_list = [
        Triangle(a=int(t[0]), b=int(t[1]), c=int(t[2]))
        for t in triangles
    ]

    return MeshResponse(
        vertices=vertices,
        triangles=triangle_list,
        message="Triangulación generada correctamente"
    )
    
@router.post("/project-mesh", response_model=MeshResponse)
async def project_mesh(
    file: UploadFile = File(...),
    rotation_a: float = Form(0.0),
    rotation_b: float = Form(0.0),
    distance: float = Form(500.0),
) -> MeshResponse:
    image_service = ImageInputService()
    detector = FaceMeshDetector()
    expansion_service = LandmarkExpansionService()
    mesh_builder = MeshBuilder()
    projection_service = ProjectionService(distance=distance)

    try:
        image, _ = await image_service.read_image(file)
        landmarks = detector.detect(image)

        if not landmarks:
            raise HTTPException(status_code=404, detail="No se detectó rostro")

        expanded_landmarks = expansion_service.expand(landmarks)

        vertices = [
            Vertex3D(x=point.x, y=point.y, z=point.z)
            for point in expanded_landmarks
        ]

        normalized_vertices = projection_service.normalize_vertices(vertices)
        projected_vertices = projection_service.rotate_and_project(
            normalized_vertices,
            rotation_a=rotation_a,
            rotation_b=rotation_b,
        )

        _, triangles_np = mesh_builder.build(expanded_landmarks)

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

    response_vertices = [
        Vertex(x=v.x, y=v.y, z=v.z)
        for v in normalized_vertices
    ]

    response_triangles = [
        Triangle(a=int(t[0]), b=int(t[1]), c=int(t[2]))
        for t in triangles_np
    ]

    return MeshResponse(
        vertices=response_vertices,
        projected_vertices=projected_vertices,
        triangles=response_triangles,
        rotation_a=rotation_a,
        rotation_b=rotation_b,
        distance=distance,
        message="Proyección 3D generada correctamente"
    )