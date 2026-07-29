from pathlib import Path

from django.conf import settings
from ninja import Router, Schema


router = Router(tags=["draft"])


class HealthResponse(Schema):
    status: str
    service: str


class FrontendIntegrationResponse(Schema):
    configured_path: str
    exists: bool
    package_json_exists: bool


@router.get("/health", response=HealthResponse)
def health(request):
    return {"status": "ok", "service": "fantasy-football-api"}


@router.get("/integration/frontend", response=FrontendIntegrationResponse)
def frontend_integration(request):
    frontend_root = Path(settings.FANTASY_FRONTEND_ROOT)

    return {
        "configured_path": str(frontend_root),
        "exists": frontend_root.exists(),
        "package_json_exists": (frontend_root / "package.json").exists(),
    }
