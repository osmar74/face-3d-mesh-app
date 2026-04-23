from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict

from backend.app.models.storage_model import (
    LoadedMeshResponse,
    SavedFilesResponse,
    SaveMeshResponse,
)
from backend.app.services.mesh_storage_service import MeshStorageService

router = APIRouter(prefix="/storage", tags=["storage"])


class SaveMeshRequest(BaseModel):
    data: Dict[str, Any]
    filename_prefix: str = "mesh_result"


@router.get("/ping")
def storage_ping() -> dict:
    return {
        "status": "ok",
        "message": "Módulo de almacenamiento listo para implementar guardado/carga"
    }


@router.post("/save", response_model=SaveMeshResponse)
def save_mesh(request: SaveMeshRequest) -> SaveMeshResponse:
    storage_service = MeshStorageService()

    try:
        filename = storage_service.save(
            data=request.data,
            filename_prefix=request.filename_prefix
        )
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error

    return SaveMeshResponse(
        filename=filename,
        message="Resultado guardado correctamente"
    )


@router.get("/list", response_model=SavedFilesResponse)
def list_saved_meshes() -> SavedFilesResponse:
    storage_service = MeshStorageService()

    try:
        files = storage_service.list_files()
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error

    return SavedFilesResponse(
        files=files,
        message="Lista de archivos obtenida correctamente"
    )


@router.get("/load/{filename}", response_model=LoadedMeshResponse)
def load_saved_mesh(filename: str) -> LoadedMeshResponse:
    storage_service = MeshStorageService()

    try:
        data = storage_service.load(filename)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error

    return LoadedMeshResponse(
        data=data,
        message="Archivo cargado correctamente"
    )