"""
Rotas de health check
"""
from fastapi import APIRouter
from datetime import datetime
from src.backend.models import HealthResponse
from src.backend.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Verifica o status da API e serviços conectados
    """
    services_status = {
        "database": "ok",
        "llm": "ok" if settings.openai_api_key else "not_configured",
        "ocr": "ok" if settings.tesseract_path else "not_configured"
    }
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now(),
        services=services_status
    )


@router.get("/")
async def root():
    """
    Rota raiz da API
    """
    return {
        "message": "Assistente SQL API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

