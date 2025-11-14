"""
Rotas da API
"""
from src.backend.routes.health import router as health_router
from src.backend.routes.query import router as query_router
from src.backend.routes.structure import router as structure_router
from src.backend.routes.docker import router as docker_router

__all__ = ["health_router", "query_router", "structure_router", "docker_router"]

