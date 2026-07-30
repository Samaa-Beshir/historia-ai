from fastapi import APIRouter, Depends

from app.api.schemas.health import HealthResponse, VersionResponse
from app.config.settings import Settings
from app.core.dependencies import get_settings_dep

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/version", response_model=VersionResponse)
def get_version(settings: Settings = Depends(get_settings_dep)) -> VersionResponse:
    return VersionResponse(app_name=settings.app_name, version=settings.app_version)
