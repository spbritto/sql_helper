"""
Gerenciador centralizado de estruturas de banco de dados
"""
from typing import Optional
from loguru import logger

from ..models import DatabaseStructure


class StructureManager:
    """Gerencia o armazenamento e acesso à estrutura de BD carregada"""
    
    _current_structure: Optional[DatabaseStructure] = None
    
    @classmethod
    def set_structure(cls, structure: DatabaseStructure) -> None:
        """
        Define a estrutura atual
        
        Args:
            structure: Estrutura do banco de dados
        """
        cls._current_structure = structure
        logger.info(f"✅ Estrutura definida: {len(structure.tables)} tabelas carregadas")
        
        # Log detalhado de cada tabela
        for table in structure.tables:
            table_name = table.get("name", "N/A")
            fields_count = len(table.get("fields", []))
            logger.debug(f"   • Tabela '{table_name}': {fields_count} campos")
    
    @classmethod
    def get_structure(cls) -> Optional[DatabaseStructure]:
        """
        Retorna a estrutura atual
        
        Returns:
            DatabaseStructure ou None se não houver estrutura carregada
        """
        if cls._current_structure is None:
            logger.warning("⚠️ Tentativa de acessar estrutura, mas nenhuma está carregada")
        return cls._current_structure
    
    @classmethod
    def has_structure(cls) -> bool:
        """
        Verifica se há uma estrutura carregada
        
        Returns:
            True se há estrutura carregada, False caso contrário
        """
        return cls._current_structure is not None
    
    @classmethod
    def clear_structure(cls) -> None:
        """
        Limpa a estrutura atual
        """
        if cls._current_structure:
            tables_count = len(cls._current_structure.tables)
            cls._current_structure = None
            logger.info(f"🗑️ Estrutura limpa ({tables_count} tabelas removidas)")
        else:
            logger.debug("Tentativa de limpar estrutura, mas já estava vazia")
    
    @classmethod
    def get_structure_summary(cls) -> dict:
        """
        Retorna um resumo da estrutura atual
        
        Returns:
            Dict com resumo da estrutura
        """
        if not cls._current_structure:
            return {
                "loaded": False,
                "tables_count": 0,
                "relationships_count": 0,
                "format": None
            }
        
        return {
            "loaded": True,
            "tables_count": len(cls._current_structure.tables),
            "relationships_count": len(cls._current_structure.relationships),
            "format": cls._current_structure.metadata.get("detected_format", "unknown"),
            "tables_names": [table.get("name", "N/A") for table in cls._current_structure.tables]
        }

