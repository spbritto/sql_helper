"""
Rotas para gerenciamento de estruturas de banco de dados
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Optional
from loguru import logger

from src.backend.models import DatabaseStructure, DatabaseConnection, DatabaseConnectionTest
from src.backend.services.structure_extractor import StructureExtractor
from src.backend.services.structure_manager import StructureManager
from src.backend.services.database_inspector import DatabaseInspector

router = APIRouter()
structure_extractor = StructureExtractor()
database_inspector = DatabaseInspector()


@router.post("/upload-text")
async def upload_text_structure(file: UploadFile = File(...)):
    """
    Faz upload de arquivo texto com estrutura do banco de dados
    """
    try:
        logger.info(f"Processando arquivo texto: {file.filename}")
        
        # Lê o conteúdo do arquivo
        content = await file.read()
        text_content = content.decode("utf-8")
        
        # Extrai a estrutura
        structure = await structure_extractor.extract_from_text(text_content)
        
        # Armazena estrutura atual usando StructureManager
        StructureManager.set_structure(structure)
        
        logger.success(f"Estrutura armazenada: {len(structure.tables)} tabelas")
        
        return {
            "message": "Estrutura extraída com sucesso",
            "structure": structure,
            "summary": {
                "total_tables": len(structure.tables),
                "total_relationships": len(structure.relationships),
                "format": structure.metadata.get("detected_format", "unknown")
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar arquivo texto: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar arquivo: {str(e)}"
        )


@router.post("/upload-image")
async def upload_image_structure(file: UploadFile = File(...)):
    """
    Faz upload de imagem com estrutura do banco de dados (usa OCR)
    """
    try:
        logger.info(f"Processando imagem: {file.filename}")
        
        # Lê o conteúdo do arquivo
        content = await file.read()
        
        # Extrai a estrutura via OCR
        structure = await structure_extractor.extract_from_image(content)
        
        # Armazena estrutura atual usando StructureManager
        StructureManager.set_structure(structure)
        
        logger.success(f"Estrutura armazenada: {len(structure.tables)} tabelas")
        
        return {
            "message": "Estrutura extraída com sucesso via OCR",
            "structure": structure,
            "summary": {
                "total_tables": len(structure.tables),
                "total_relationships": len(structure.relationships),
                "format": structure.metadata.get("detected_format", "unknown")
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar imagem: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar imagem: {str(e)}"
        )


@router.get("/current")
async def get_current_structure():
    """
    Retorna a estrutura atualmente carregada na sessão
    """
    try:
        structure = StructureManager.get_structure()
        
        if structure is None:
            return {
                "loaded": False,
                "message": "Nenhuma estrutura carregada",
                "structure": None
            }
        
        return {
            "loaded": True,
            "message": "Estrutura carregada",
            "structure": structure,
            "summary": {
                "total_tables": len(structure.tables),
                "total_relationships": len(structure.relationships),
                "format": structure.metadata.get("detected_format", "unknown"),
                "created_at": structure.created_at.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar estrutura atual: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar estrutura: {str(e)}"
        )


@router.delete("/current")
async def clear_current_structure():
    """
    Limpa a estrutura atualmente carregada
    """
    try:
        StructureManager.clear_structure()
        
        return {
            "message": "Estrutura atual removida com sucesso"
        }
        
    except Exception as e:
        logger.error(f"Erro ao limpar estrutura: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao limpar estrutura: {str(e)}"
        )


@router.get("/list", response_model=List[DatabaseStructure])
async def list_structures():
    """
    Lista todas as estruturas de banco de dados cadastradas
    """
    try:
        # TODO: Implementar busca no banco de dados
        return []
        
    except Exception as e:
        logger.error(f"Erro ao listar estruturas: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar estruturas: {str(e)}"
        )


@router.get("/{structure_id}", response_model=DatabaseStructure)
async def get_structure(structure_id: str):
    """
    Retorna uma estrutura específica pelo ID
    """
    try:
        # TODO: Implementar busca no banco de dados
        raise HTTPException(status_code=404, detail="Estrutura não encontrada")
        
    except Exception as e:
        logger.error(f"Erro ao buscar estrutura: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar estrutura: {str(e)}"
        )


@router.delete("/{structure_id}")
async def delete_structure(structure_id: str):
    """
    Remove uma estrutura cadastrada
    """
    try:
        # TODO: Implementar remoção no banco de dados
        return {"message": "Estrutura removida com sucesso"}
        
    except Exception as e:
        logger.error(f"Erro ao remover estrutura: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao remover estrutura: {str(e)}"
        )


@router.post("/test-connection", response_model=DatabaseConnectionTest)
async def test_database_connection(connection: DatabaseConnection):
    """
    Testa conexão com banco de dados sem carregar estrutura
    """
    try:
        logger.info(f"Testando conexão com banco: {connection.database} ({connection.db_type})")
        
        # Testa conexão
        inspector = DatabaseInspector()
        result = inspector.test_connection(
            db_type=connection.db_type,
            host=connection.host,
            port=connection.port,
            username=connection.username,
            password=connection.password,
            database=connection.database,
            connection_timeout=connection.connection_timeout
        )
        
        if result["success"]:
            logger.success(f"✅ Teste de conexão bem-sucedido: {connection.database}")
        else:
            logger.warning(f"⚠️ Teste de conexão falhou: {result['message']}")
        
        return DatabaseConnectionTest(**result)
        
    except Exception as e:
        logger.error(f"Erro ao testar conexão: {e}")
        return DatabaseConnectionTest(
            success=False,
            message=f"Erro ao testar conexão: {str(e)}",
            error=str(e)
        )


@router.post("/connect-database")
async def connect_and_load_database(connection: DatabaseConnection):
    """
    Conecta a banco de dados existente e carrega sua estrutura
    """
    try:
        logger.info(f"Conectando ao banco: {connection.database} ({connection.db_type})")
        
        # Extrai estrutura do banco
        structure = await structure_extractor.extract_from_database(connection)
        
        # Armazena estrutura atual usando StructureManager
        StructureManager.set_structure(structure)
        
        logger.success(f"Estrutura carregada do banco: {len(structure.tables)} tabelas")
        
        return {
            "message": "Estrutura extraída do banco de dados com sucesso",
            "structure": structure,
            "summary": {
                "total_tables": len(structure.tables),
                "total_relationships": len(structure.relationships),
                "format": structure.metadata.get("detected_format", "unknown"),
                "dialect": structure.metadata.get("dialect", "unknown")
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao conectar e carregar banco de dados: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao conectar ao banco de dados: {str(e)}"
        )

