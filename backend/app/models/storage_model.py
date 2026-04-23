from pydantic import BaseModel, Field
from typing import Any, Dict, List


class SaveMeshResponse(BaseModel):
    filename: str
    message: str


class SavedFilesResponse(BaseModel):
    files: List[str] = Field(default_factory=list)
    message: str


class LoadedMeshResponse(BaseModel):
    data: Dict[str, Any]
    message: str