"""
Rotas para gerenciamento de conexão com Docker PostgreSQL
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from loguru import logger

from src.backend.services.docker_postgres_connection import DockerPostgresConnection
from src.backend.services.structure_manager import structure_manager

router = APIRouter()


class DatabaseSelection(BaseModel):
    """Modelo para seleção de database"""
    database: str


@router.get("/test-connection")
async def test_docker_connection() -> Dict[str, Any]:
    """
    Testa conexão com PostgreSQL do Docker
    
    Returns:
        Status da conexão
    """
    try:
        docker_conn = DockerPostgresConnection()
        result = docker_conn.test_connection()
        
        if not result["connected"]:
            logger.warning("Falha ao conectar ao Docker PostgreSQL")
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao testar conexão Docker: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao testar conexão: {str(e)}"
        )


@router.get("/list-databases")
async def list_docker_databases() -> Dict[str, Any]:
    """
    Lista databases disponíveis no PostgreSQL do Docker
    
    Returns:
        Lista de databases
    """
    try:
        # Primeiro testa se está conectado
        docker_conn = DockerPostgresConnection()
        conn_test = docker_conn.test_connection()
        
        if not conn_test["connected"]:
            return {
                "success": False,
                "error": conn_test["error"],
                "databases": [],
                "total": 0
            }
        
        # Lista databases
        result = docker_conn.list_databases()
        return result
        
    except Exception as e:
        logger.error(f"Erro ao listar databases: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar databases: {str(e)}"
        )


@router.post("/connect-and-extract")
async def connect_and_extract_structure(selection: DatabaseSelection) -> Dict[str, Any]:
    """
    Conecta a um database específico e extrai sua estrutura
    
    Args:
        selection: DatabaseSelection com nome do database
        
    Returns:
        Estrutura do database
    """
    try:
        logger.info(f"📥 Solicitação para extrair estrutura do database: {selection.database}")
        
        docker_conn = DockerPostgresConnection()
        
        # Conecta e extrai estrutura
        result = docker_conn.connect_and_extract_structure(selection.database)
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Erro ao extrair estrutura")
            )
        
        # Salva estrutura no gerenciador (para uso posterior)
        from src.backend.models import DatabaseStructure
        structure = DatabaseStructure(**result["structure"])
        structure_manager.set_structure(structure)
        
        logger.success(
            f"✅ Estrutura do database '{selection.database}' carregada: "
            f"{result['summary']['total_tables']} tabelas"
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao conectar e extrair estrutura: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar estrutura: {str(e)}"
        )


@router.get("/database-info/{database_name}")
async def get_database_info(database_name: str) -> Dict[str, Any]:
    """
    Obtém informações detalhadas sobre um database específico
    
    Args:
        database_name: Nome do database
        
    Returns:
        Informações do database
    """
    try:
        docker_conn = DockerPostgresConnection()
        result = docker_conn.get_database_info(database_name)
        
        if not result["success"]:
            raise HTTPException(
                status_code=404,
                detail=f"Database '{database_name}' não encontrado"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar informações do database: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar informações: {str(e)}"
        )


@router.get("/connection-status")
async def get_connection_status() -> Dict[str, Any]:
    """
    Retorna status completo da conexão Docker + databases disponíveis
    
    Returns:
        Status completo
    """
    try:
        docker_conn = DockerPostgresConnection()
        
        # Testa conexão
        conn_result = docker_conn.test_connection()
        
        if not conn_result["connected"]:
            return {
                "connected": False,
                "message": conn_result["message"],
                "error": conn_result.get("error"),
                "databases": []
            }
        
        # Lista databases
        db_result = docker_conn.list_databases()
        
        return {
            "connected": True,
            "message": "Conectado ao Docker PostgreSQL",
            "version": conn_result["version"],
            "host": conn_result["host"],
            "port": conn_result["port"],
            "databases": db_result.get("databases", []),
            "total_databases": db_result.get("total", 0)
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar status: {str(e)}"
        )

