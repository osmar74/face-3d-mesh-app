from fastapi import Form
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from backend.app.services.mesh_refinement_service import MeshRefinementService
from backend.app.services.obj_export_service import ObjExportService
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

from backend.app.services.image_input_service import ImageInputService
from backend.app.services.landmark_expansion_service import LandmarkExpansionService
from backend.app.services.mesh_builder import MeshBuilder
from backend.app.services.projection_service import ProjectionService

from backend.app.models.detector_mode_model import DetectorMode
from backend.app.services.detector_factory import DetectorFactory
from backend.app.models.detector_mode_model import DetectorMode, PRNetOutputMode

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
async def detect_landmarks(
    file: UploadFile = File(...),
    detector_mode: DetectorMode = Form(DetectorMode.MEDIAPIPE),
    prnet_output_mode: PRNetOutputMode = Form(PRNetOutputMode.LANDMARKS),
) -> FaceLandmarksResponse:
    image_service = ImageInputService()
    detector = DetectorFactory.create(
    detector_mode,
    prnet_output_mode=prnet_output_mode
)
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
async def triangulate(
    file: UploadFile = File(...),
    detector_mode: DetectorMode = Form(DetectorMode.MEDIAPIPE),
    prnet_output_mode: PRNetOutputMode = Form(PRNetOutputMode.LANDMARKS),
) -> MeshResponse:
    image_service = ImageInputService()
    detector = DetectorFactory.create(
    detector_mode,
    prnet_output_mode=prnet_output_mode
)
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
    
@router.post("/project-mesh")
async def project_mesh(
    file: UploadFile = File(...),
    detector_mode: DetectorMode = Form(DetectorMode.MEDIAPIPE),
    prnet_output_mode: PRNetOutputMode = Form(PRNetOutputMode.LANDMARKS),
):
    image_service = ImageInputService()
    mesh_builder = MeshBuilder()
    refinement_service = MeshRefinementService()

    try:
        # Leer imagen
        image, _ = await image_service.read_image(file)

        # Crear detector
        detector = DetectorFactory.create(
            detector_mode,
            prnet_output_mode=prnet_output_mode
        )

        # Detectar landmarks
        landmarks = detector.detect(image)

        if not landmarks:
            raise HTTPException(
                status_code=400,
                detail="No se detectaron landmarks"
            )

        # -------------------------
        # 1. Construcción inicial
        # -------------------------
        points_2d, triangle_array = mesh_builder.build(landmarks)

        triangles = [
            Triangle(
                a=int(tri[0]),
                b=int(tri[1]),
                c=int(tri[2])
            )
            for tri in triangle_array
        ]

        # -------------------------
        # 2. Suavizado de malla
        # -------------------------
        landmarks_smoothed = refinement_service.smooth_landmarks(
            landmarks=landmarks,
            triangles=triangles,
            iterations=2,
            strength=0.35
        )

        # -------------------------
        # 3. Reconstruir con suavizado
        # -------------------------
        points_2d, triangle_array = mesh_builder.build(landmarks_smoothed)

        triangles = [
            Triangle(
                a=int(tri[0]),
                b=int(tri[1]),
                c=int(tri[2])
            )
            for tri in triangle_array
        ]

        # -------------------------
        # 4. Construir malla 3D
        # -------------------------
        vertices_3d = [
            Vertex3D(
                index=p.index,
                x=p.x,
                y=p.y,
                z=p.z
            )
            for p in landmarks_smoothed
        ]

        # -------------------------
        # 5. Proyección (rotación simple)
        # -------------------------
        projected_vertices = []

        for v in vertices_3d:
            projected_vertices.append({
                "x": v.x,
                "y": v.y,
                "z": v.z
            })

        # -------------------------
        # 6. Respuesta
        # -------------------------
        return {
            "vertex_count": len(vertices_3d),
            "triangle_count": len(triangles),
            "vertices": [
                {"x": v.x, "y": v.y, "z": v.z}
                for v in vertices_3d
            ],
            "triangles": [
                {"a": t.a, "b": t.b, "c": t.c}
                for t in triangles
            ],
            "projected_vertices": projected_vertices,
            "message": "Proyección 3D generada con suavizado"
        }

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error en proyección 3D: {str(error)}"
        ) from error


@router.post("/export-obj")
async def export_obj(
    file: UploadFile = File(...),
    detector_mode: DetectorMode = Form(DetectorMode.MEDIAPIPE),
    prnet_output_mode: PRNetOutputMode = Form(PRNetOutputMode.LANDMARKS),
) -> FileResponse:
    image_service = ImageInputService()
    mesh_builder = MeshBuilder()
    export_service = ObjExportService()

    try:
        image, _ = await image_service.read_image(file)

        detector = DetectorFactory.create(
            detector_mode,
            prnet_output_mode=prnet_output_mode
        )

        landmarks = detector.detect(image)

        if not landmarks:
            raise HTTPException(
                status_code=400,
                detail="No se detectaron puntos faciales para exportar OBJ"
            )

        vertices, triangles = mesh_builder.build_3d_mesh(landmarks)

        obj_path = export_service.export(
            vertices=vertices,
            triangles=triangles,
            filename_prefix=f"face_model_{detector_mode.value}"
        )

        return FileResponse(
            path=obj_path,
            filename=obj_path.split("\\")[-1],
            media_type="text/plain"
        )

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Error exportando OBJ: {str(error)}"
        ) from error