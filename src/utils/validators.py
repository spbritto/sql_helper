"""
Validadores e funções de validação
"""
import re
from typing import Optional, List
from loguru import logger


class SQLValidator:
    """Validador de queries SQL"""
    
    # Palavras-chave perigosas
    DANGEROUS_KEYWORDS = [
        'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 
        'CREATE', 'INSERT', 'UPDATE'
    ]
    
    # Palavras-chave de leitura (seguras)
    READ_KEYWORDS = ['SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN']
    
    @staticmethod
    def is_read_only(sql: str) -> bool:
        """
        Verifica se a query é apenas de leitura
        
        Args:
            sql: Query SQL
            
        Returns:
            True se for apenas leitura, False caso contrário
        """
        sql_upper = sql.upper().strip()
        
        # Verifica se começa com palavra-chave de leitura
        for keyword in SQLValidator.READ_KEYWORDS:
            if sql_upper.startswith(keyword):
                return True
        
        return False
    
    @staticmethod
    def has_dangerous_operations(sql: str) -> tuple[bool, List[str]]:
        """
        Verifica se a query contém operações perigosas
        
        Args:
            sql: Query SQL
            
        Returns:
            Tupla (tem_operações_perigosas, lista_de_operações)
        """
        sql_upper = sql.upper()
        found_dangerous = []
        
        for keyword in SQLValidator.DANGEROUS_KEYWORDS:
            if keyword in sql_upper:
                found_dangerous.append(keyword)
        
        return (len(found_dangerous) > 0, found_dangerous)
    
    @staticmethod
    def validate_syntax(sql: str) -> tuple[bool, Optional[str]]:
        """
        Validação básica de sintaxe SQL
        
        Args:
            sql: Query SQL
            
        Returns:
            Tupla (é_válido, mensagem_erro)
        """
        if not sql or not sql.strip():
            return (False, "Query vazia")
        
        # Verifica parênteses balanceados
        if sql.count('(') != sql.count(')'):
            return (False, "Parênteses não balanceados")
        
        # Verifica aspas balanceadas
        single_quotes = sql.count("'")
        if single_quotes % 2 != 0:
            return (False, "Aspas simples não balanceadas")
        
        double_quotes = sql.count('"')
        if double_quotes % 2 != 0:
            return (False, "Aspas duplas não balanceadas")
        
        return (True, None)
    
    @staticmethod
    def sanitize(sql: str) -> str:
        """
        Remove caracteres potencialmente perigosos
        
        Args:
            sql: Query SQL
            
        Returns:
            Query sanitizada
        """
        # Remove comentários SQL
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        
        # Remove múltiplos espaços
        sql = re.sub(r'\s+', ' ', sql)
        
        return sql.strip()


class FileValidator:
    """Validador de arquivos"""
    
    ALLOWED_TEXT_EXTENSIONS = ['.txt', '.sql', '.ddl']
    ALLOWED_IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @staticmethod
    def is_allowed_extension(filename: str, file_type: str = 'text') -> bool:
        """
        Verifica se a extensão do arquivo é permitida
        
        Args:
            filename: Nome do arquivo
            file_type: Tipo ('text' ou 'image')
            
        Returns:
            True se permitido, False caso contrário
        """
        ext = filename.lower().split('.')[-1]
        ext = f'.{ext}'
        
        if file_type == 'text':
            return ext in FileValidator.ALLOWED_TEXT_EXTENSIONS
        elif file_type == 'image':
            return ext in FileValidator.ALLOWED_IMAGE_EXTENSIONS
        
        return False
    
    @staticmethod
    def is_valid_size(file_size: int, max_size: Optional[int] = None) -> bool:
        """
        Verifica se o tamanho do arquivo é válido
        
        Args:
            file_size: Tamanho em bytes
            max_size: Tamanho máximo permitido (None usa o padrão)
            
        Returns:
            True se válido, False caso contrário
        """
        max_allowed = max_size or FileValidator.MAX_FILE_SIZE
        return file_size <= max_allowed
    
    @staticmethod
    def validate_upload(
        filename: str, 
        file_size: int, 
        file_type: str = 'text'
    ) -> tuple[bool, Optional[str]]:
        """
        Validação completa de upload
        
        Args:
            filename: Nome do arquivo
            file_size: Tamanho em bytes
            file_type: Tipo do arquivo
            
        Returns:
            Tupla (é_válido, mensagem_erro)
        """
        # Valida extensão
        if not FileValidator.is_allowed_extension(filename, file_type):
            return (False, f"Extensão não permitida para tipo {file_type}")
        
        # Valida tamanho
        if not FileValidator.is_valid_size(file_size):
            return (False, f"Arquivo muito grande (máx: {FileValidator.MAX_FILE_SIZE/1024/1024}MB)")
        
        return (True, None)

