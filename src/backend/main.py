"""
Ponto de entrada da API FastAPI
"""
import sys
from pathlib import Path

# Adiciona o diretório raiz do projeto ao sys.path
# Isso permite que os imports absolutos funcionem independente de como o script é executado
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from loguru import logger

from src.backend.config import settings
from src.backend.routes import query_router, structure_router, health_router, docker_router

# Configuração de logs
logger.add(
    settings.log_file,
    rotation="500 MB",
    retention="10 days",
    level=settings.log_level
)

# Criação da aplicação FastAPI
app = FastAPI(
    title="Assistente SQL - API",
    description="API para geração de queries SQL a partir de linguagem natural",
    version="1.0.0",
    debug=settings.api_debug
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de rotas
app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(structure_router, prefix="/api/structure", tags=["structure"])
app.include_router(query_router, prefix="/api/query", tags=["query"])
app.include_router(docker_router, prefix="/api/docker", tags=["docker"])


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global para exceções"""
    logger.error(f"Erro não tratado: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erro interno do servidor",
            "message": str(exc) if settings.api_debug else "Erro interno"
        }
    )


@app.on_event("startup")
async def startup_event():
    """Evento executado no startup da aplicação"""
    logger.info("🚀 Iniciando Assistente SQL API...")
    logger.info(f"📝 Modo debug: {settings.api_debug}")
    logger.info(f"🤖 Modelo LLM: {settings.openai_model}")


@app.on_event("shutdown")
async def shutdown_event():
    """Evento executado no shutdown da aplicação"""
    logger.info("🛑 Encerrando Assistente SQL API...")


def main():
    """Função principal para executar a aplicação"""
    logger.info(f"🌐 Servidor rodando em http://{settings.api_host}:{settings.api_port}")
    uvicorn.run(
        "src.backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug
    )


if __name__ == "__main__":
    main()

