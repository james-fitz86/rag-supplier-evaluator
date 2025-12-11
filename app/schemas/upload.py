from pydantic import BaseModel

class UploadRequest(BaseModel):
    text: str

class UploadResponse(BaseModel):
    id: int
    message: str
