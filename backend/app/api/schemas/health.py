from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class VersionResponse(BaseModel):
    app_name: str
    version: str
