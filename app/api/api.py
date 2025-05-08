from fastapi import APIRouter, Depends
from app.api.endpoints import conversion
from app.security.api_key import get_api_key
from app.core.config import settings

api_router = APIRouter()

# Include routers from endpoints with API key authentication for production use
api_router.include_router(
    conversion.router, 
    prefix="/conversion", 
    tags=["conversion"],
    dependencies=[Depends(get_api_key)] if settings.ENVIRONMENT == "production" else []
)
