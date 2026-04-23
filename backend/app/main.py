from fastapi import FastAPI

app = FastAPI(title="Face 3D Mesh App API")


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "message": "API funcionando correctamente"}