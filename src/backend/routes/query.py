"""
Rotas para geração de queries SQL
"""
from fastapi import APIRouter, HTTPException
from typing import List
from loguru import logger

from ..models import NaturalLanguageQuery, SQLQueryResponse, QueryHistory
from ..services.query_generator import QueryGenerator

router = APIRouter()
query_generator = QueryGenerator()


@router.post("/generate", response_model=SQLQueryResponse)
async def generate_query(query_request: NaturalLanguageQuery):
    """
    Gera uma query SQL a partir de linguagem natural
    """
    try:
        logger.info(f"Gerando query para: {query_request.question}")
        
        result = await query_generator.generate(
            question=query_request.question,
            structure_id=query_request.structure_id,
            context=query_request.context
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao gerar query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar query: {str(e)}"
        )


@router.post("/optimize")
async def optimize_query(sql: str):
    """
    Otimiza uma query SQL existente
    """
    try:
        logger.info("Otimizando query SQL")
        
        result = await query_generator.optimize(sql)
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao otimizar query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao otimizar query: {str(e)}"
        )


@router.get("/history", response_model=List[QueryHistory])
async def get_query_history(limit: int = 10):
    """
    Retorna o histórico de queries geradas
    """
    try:
        # TODO: Implementar busca no banco de dados
        return []
        
    except Exception as e:
        logger.error(f"Erro ao buscar histórico: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar histórico: {str(e)}"
        )


@router.post("/validate")
async def validate_query(sql: str):
    """
    Valida uma query SQL
    """
    try:
        logger.info("Validando query SQL")
        
        result = await query_generator.validate(sql)
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao validar query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao validar query: {str(e)}"
        )

