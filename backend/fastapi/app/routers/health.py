from fastapi import APIRouter, Request
from ..models.schemas import HealthResponse
from ..services.example_service import get_welcome

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> dict:
    return {"status": "ok"}


@router.get("/welcome")
async def welcome(request: Request) -> dict:
    settings = getattr(request.app.state, "settings", None)
    return {"message": get_welcome(settings)}
