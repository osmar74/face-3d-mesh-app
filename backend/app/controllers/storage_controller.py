from fastapi import APIRouter

router = APIRouter(prefix="/storage", tags=["storage"])


@router.get("/ping")
def storage_ping() -> dict:
    return {
        "status": "ok",
        "message": "Módulo de almacenamiento listo para implementar guardado/carga"
    }