from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.controllers.face_controller import router as face_router
from backend.app.controllers.storage_controller import router as storage_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict:
    return {
        "status": "ok",
        "message": "API funcionando correctamente"
    }


app.include_router(face_router, prefix=settings.API_PREFIX)
app.include_router(storage_router, prefix=settings.API_PREFIX)