from pydantic import BaseModel


class ImageInfoResponse(BaseModel):
    filename: str
    width: int
    height: int
    channels: int
    message: str