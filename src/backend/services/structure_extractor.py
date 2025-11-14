"""
Serviço para extração de estrutura de banco de dados
"""
from typing import Dict, Any
from loguru import logger

from src.backend.models import DatabaseStructure, DatabaseConnection
from src.parsing.text_parser import TextParser
from src.ocr.image_processor import ImageProcessor
from src.backend.services.database_inspector import DatabaseInspector


class StructureExtractor:
    """Extrator de estrutura de banco de dados"""
    
    def __init__(self):
        self.text_parser = TextParser()
        self.image_processor = ImageProcessor()
        self.database_inspector = DatabaseInspector()
    
    async def extract_from_text(self, content: str) -> DatabaseStructure:
        """
        Extrai estrutura de banco de dados a partir de texto
        
        Args:
            content: Conteúdo texto com a estrutura
            
        Returns:
            DatabaseStructure extraída
        """
        try:
            logger.info("Extraindo estrutura de texto")
            
            # Parse do texto
            parsed_data = self.text_parser.parse(content)
            
            # Converte para DatabaseStructure
            structure = DatabaseStructure(
                tables=parsed_data.get("tables", []),
                relationships=parsed_data.get("relationships", []),
                metadata=parsed_data.get("metadata", {})
            )
            
            logger.success(f"Estrutura extraída: {len(structure.tables)} tabelas")
            return structure
            
        except Exception as e:
            logger.error(f"Erro ao extrair estrutura de texto: {e}")
            raise
    
    async def extract_from_image(self, image_bytes: bytes) -> DatabaseStructure:
        """
        Extrai estrutura de banco de dados a partir de imagem (OCR)
        
        Args:
            image_bytes: Bytes da imagem
            
        Returns:
            DatabaseStructure extraída
        """
        try:
            logger.info("Extraindo estrutura de imagem via OCR")
            
            # Processa OCR
            text_content = self.image_processor.extract_text(image_bytes)
            
            # Usa o parser de texto no resultado do OCR
            structure = await self.extract_from_text(text_content)
            
            logger.success("Estrutura extraída via OCR com sucesso")
            return structure
            
        except Exception as e:
            logger.error(f"Erro ao extrair estrutura de imagem: {e}")
            raise
    
    async def extract_from_database(self, connection: DatabaseConnection) -> DatabaseStructure:
        """
        Extrai estrutura de banco de dados a partir de conexão direta
        
        Args:
            connection: Parâmetros de conexão com o banco de dados
            
        Returns:
            DatabaseStructure extraída
        """
        try:
            logger.info(f"Extraindo estrutura do banco: {connection.database} ({connection.db_type})")
            
            # Conecta ao banco
            self.database_inspector.connect(
                db_type=connection.db_type,
                host=connection.host,
                port=connection.port,
                username=connection.username,
                password=connection.password,
                database=connection.database,
                additional_params=connection.additional_params,
                connection_timeout=connection.connection_timeout
            )
            
            # Extrai estrutura
            structure = self.database_inspector.extract_structure()
            
            # Desconecta
            self.database_inspector.disconnect()
            
            logger.success(f"Estrutura extraída do banco de dados com sucesso")
            return structure
            
        except Exception as e:
            logger.error(f"Erro ao extrair estrutura do banco de dados: {e}")
            # Garante desconexão em caso de erro
            try:
                self.database_inspector.disconnect()
            except:
                pass
            raise

