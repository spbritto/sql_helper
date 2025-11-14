"""
Serviço para inspeção de bancos de dados existentes
"""
from typing import Dict, Any, List, Optional
from loguru import logger
from sqlalchemy import create_engine, inspect, MetaData, Table, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
import re

from src.backend.models import DatabaseStructure


class DatabaseInspector:
    """Inspetor de estrutura de bancos de dados existentes"""
    
    # Mapeamento de dialetos SQL suportados
    SUPPORTED_DIALECTS = {
        "mysql": "mysql+pymysql",
        "postgresql": "postgresql+psycopg2",
        "sqlite": "sqlite",
        "mssql": "mssql+pyodbc"
    }
    
    # Mapeamento de tipos SQL para tipos genéricos
    TYPE_MAPPING = {
        # Numéricos
        "INT": "int",
        "INTEGER": "int",
        "BIGINT": "bigint",
        "SMALLINT": "smallint",
        "TINYINT": "tinyint",
        "DECIMAL": "decimal",
        "NUMERIC": "numeric",
        "FLOAT": "float",
        "DOUBLE": "double",
        "REAL": "real",
        
        # String
        "VARCHAR": "varchar",
        "CHAR": "char",
        "TEXT": "text",
        "LONGTEXT": "text",
        "MEDIUMTEXT": "text",
        "TINYTEXT": "text",
        "NVARCHAR": "varchar",
        "NCHAR": "char",
        
        # Data/Hora
        "DATE": "date",
        "DATETIME": "datetime",
        "TIMESTAMP": "timestamp",
        "TIME": "time",
        
        # Boolean
        "BOOLEAN": "boolean",
        "BOOL": "boolean",
        "BIT": "boolean",
        
        # Outros
        "JSON": "json",
        "JSONB": "json",
        "BLOB": "blob",
        "BINARY": "binary",
        "UUID": "uuid"
    }
    
    def __init__(self):
        self.engine: Optional[Engine] = None
        self.inspector = None
    
    def build_connection_string(
        self, 
        db_type: str, 
        host: str, 
        port: int, 
        username: str, 
        password: str, 
        database: str,
        additional_params: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Constrói string de conexão para diferentes tipos de banco
        
        Args:
            db_type: Tipo do banco (mysql, postgresql, sqlite, mssql)
            host: Host do banco
            port: Porta do banco
            username: Usuário
            password: Senha
            database: Nome do banco de dados
            additional_params: Parâmetros adicionais de conexão
            
        Returns:
            String de conexão SQLAlchemy
        """
        db_type_lower = db_type.lower()
        
        if db_type_lower not in self.SUPPORTED_DIALECTS:
            raise ValueError(
                f"Tipo de banco '{db_type}' não suportado. "
                f"Tipos suportados: {', '.join(self.SUPPORTED_DIALECTS.keys())}"
            )
        
        dialect = self.SUPPORTED_DIALECTS[db_type_lower]
        
        # SQLite usa apenas o caminho do arquivo
        if db_type_lower == "sqlite":
            return f"{dialect}:///{database}"
        
        # Constrói URL para outros bancos
        connection_string = f"{dialect}://{username}:{password}@{host}:{port}/{database}"
        
        # Adiciona parâmetros adicionais se fornecidos
        if additional_params:
            params = "&".join([f"{k}={v}" for k, v in additional_params.items()])
            connection_string += f"?{params}"
        
        return connection_string
    
    def connect(
        self,
        db_type: str,
        host: str = "localhost",
        port: Optional[int] = None,
        username: str = "",
        password: str = "",
        database: str = "",
        additional_params: Optional[Dict[str, str]] = None,
        connection_timeout: int = 10
    ) -> bool:
        """
        Estabelece conexão com o banco de dados
        
        Args:
            db_type: Tipo do banco de dados
            host: Host do banco
            port: Porta do banco (None usa porta padrão)
            username: Usuário
            password: Senha
            database: Nome do banco de dados
            additional_params: Parâmetros adicionais
            connection_timeout: Timeout de conexão em segundos
            
        Returns:
            True se conectou com sucesso
            
        Raises:
            Exception: Se falhar ao conectar
        """
        try:
            # Define porta padrão se não fornecida
            if port is None:
                default_ports = {
                    "mysql": 3306,
                    "postgresql": 5432,
                    "mssql": 1433,
                    "sqlite": None
                }
                port = default_ports.get(db_type.lower())
            
            # Constrói string de conexão
            connection_string = self.build_connection_string(
                db_type, host, port, username, password, database, additional_params
            )
            
            # Cria engine com timeout
            self.engine = create_engine(
                connection_string,
                connect_args={"connect_timeout": connection_timeout} if db_type.lower() != "sqlite" else {},
                pool_pre_ping=True,  # Verifica conexão antes de usar
                echo=False
            )
            
            # Testa conexão
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            # Cria inspector
            self.inspector = inspect(self.engine)
            
            logger.success(f"✅ Conectado ao banco {db_type}: {database}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"❌ Erro ao conectar ao banco: {e}")
            raise Exception(f"Falha na conexão: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Erro inesperado ao conectar: {e}")
            raise
    
    def disconnect(self):
        """Fecha conexão com o banco de dados"""
        if self.engine:
            self.engine.dispose()
            self.engine = None
            self.inspector = None
            logger.info("🔌 Conexão com banco de dados fechada")
    
    def extract_structure(self) -> DatabaseStructure:
        """
        Extrai estrutura completa do banco de dados conectado
        
        Returns:
            DatabaseStructure com tabelas, campos e relacionamentos
            
        Raises:
            Exception: Se não houver conexão ativa
        """
        if not self.inspector:
            raise Exception("Nenhuma conexão ativa. Execute connect() primeiro.")
        
        try:
            logger.info("🔍 Iniciando extração de estrutura do banco de dados...")
            
            # Extrai tabelas
            tables = self._extract_tables()
            
            # Extrai relacionamentos
            relationships = self._extract_relationships(tables)
            
            # Metadados
            metadata = {
                "source": "database_connection",
                "detected_format": "database_inspector",
                "dialect": str(self.engine.dialect.name),
                "total_tables": len(tables),
                "total_relationships": len(relationships)
            }
            
            structure = DatabaseStructure(
                tables=tables,
                relationships=relationships,
                metadata=metadata
            )
            
            logger.success(
                f"✅ Estrutura extraída: {len(tables)} tabelas, "
                f"{len(relationships)} relacionamentos"
            )
            
            return structure
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair estrutura: {e}")
            raise
    
    def _extract_tables(self) -> List[Dict[str, Any]]:
        """
        Extrai todas as tabelas e seus campos
        
        Returns:
            Lista de dicionários com informações das tabelas
        """
        tables = []
        table_names = self.inspector.get_table_names()
        
        logger.info(f"📊 Encontradas {len(table_names)} tabelas")
        
        for table_name in table_names:
            logger.debug(f"   Processando tabela: {table_name}")
            
            # Extrai colunas
            columns = self.inspector.get_columns(table_name)
            
            # Extrai chaves primárias
            pk_constraint = self.inspector.get_pk_constraint(table_name)
            primary_keys = pk_constraint.get("constrained_columns", []) if pk_constraint else []
            
            # Extrai chaves estrangeiras
            foreign_keys = self.inspector.get_foreign_keys(table_name)
            fk_columns = {fk["constrained_columns"][0]: fk for fk in foreign_keys if fk.get("constrained_columns")}
            
            # Processa campos
            fields = []
            for column in columns:
                col_name = column["name"]
                col_type = str(column["type"])
                
                # Normaliza tipo
                normalized_type = self._normalize_type(col_type)
                
                # Verifica se é FK
                is_fk = col_name in fk_columns
                fk_reference = None
                
                if is_fk:
                    fk_info = fk_columns[col_name]
                    ref_table = fk_info.get("referred_table")
                    ref_column = fk_info.get("referred_columns", [None])[0]
                    if ref_table and ref_column:
                        fk_reference = f"{ref_table}.{ref_column}"
                
                field = {
                    "name": col_name,
                    "type": normalized_type,
                    "original_type": col_type,
                    "nullable": column.get("nullable", True),
                    "primary_key": col_name in primary_keys,
                    "foreign_key": is_fk,
                    "reference": fk_reference,
                    "default": str(column.get("default")) if column.get("default") is not None else None,
                    "autoincrement": column.get("autoincrement", False)
                }
                
                fields.append(field)
            
            table = {
                "name": table_name,
                "fields": fields,
                "primary_keys": primary_keys,
                "foreign_keys": list(fk_columns.keys())
            }
            
            tables.append(table)
        
        return tables
    
    def _extract_relationships(self, tables: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Extrai relacionamentos entre tabelas baseado em foreign keys
        
        Args:
            tables: Lista de tabelas extraídas
            
        Returns:
            Lista de relacionamentos
        """
        relationships = []
        
        for table in tables:
            table_name = table["name"]
            
            # Busca foreign keys da tabela
            foreign_keys = self.inspector.get_foreign_keys(table_name)
            
            for fk in foreign_keys:
                # Extrai informações do relacionamento
                from_table = table_name
                from_columns = fk.get("constrained_columns", [])
                to_table = fk.get("referred_table")
                to_columns = fk.get("referred_columns", [])
                
                # Cria relacionamento para cada par de colunas
                for from_col, to_col in zip(from_columns, to_columns):
                    relationship = {
                        "from_table": from_table,
                        "from_field": from_col,
                        "to_table": to_table,
                        "to_field": to_col,
                        "type": "foreign_key",
                        "detected": "explicit",
                        "confidence": "high"
                    }
                    
                    relationships.append(relationship)
                    logger.debug(
                        f"   🔗 Relacionamento: {from_table}.{from_col} -> {to_table}.{to_col}"
                    )
        
        return relationships
    
    def _normalize_type(self, sql_type: str) -> str:
        """
        Normaliza tipo SQL para tipo genérico
        
        Args:
            sql_type: Tipo SQL original
            
        Returns:
            Tipo normalizado
        """
        # Remove parâmetros (ex: VARCHAR(255) -> VARCHAR)
        base_type = re.match(r"^([A-Z]+)", sql_type.upper())
        
        if base_type:
            type_name = base_type.group(1)
            return self.TYPE_MAPPING.get(type_name, sql_type.lower())
        
        return sql_type.lower()
    
    def test_connection(
        self,
        db_type: str,
        host: str = "localhost",
        port: Optional[int] = None,
        username: str = "",
        password: str = "",
        database: str = "",
        connection_timeout: int = 5
    ) -> Dict[str, Any]:
        """
        Testa conexão com o banco de dados sem estabelecer conexão persistente
        
        Returns:
            Dicionário com resultado do teste
        """
        try:
            # Tenta conectar
            self.connect(db_type, host, port, username, password, database, connection_timeout=connection_timeout)
            
            # Busca informações básicas
            table_count = len(self.inspector.get_table_names()) if self.inspector else 0
            
            result = {
                "success": True,
                "message": f"Conexão bem-sucedida! {table_count} tabelas encontradas.",
                "dialect": str(self.engine.dialect.name) if self.engine else None,
                "table_count": table_count
            }
            
            # Desconecta
            self.disconnect()
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Falha na conexão: {str(e)}",
                "error": str(e)
            }
    
    def get_table_names(self) -> List[str]:
        """
        Retorna lista de nomes de tabelas do banco conectado
        
        Returns:
            Lista de nomes de tabelas
        """
        if not self.inspector:
            raise Exception("Nenhuma conexão ativa")
        
        return self.inspector.get_table_names()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - fecha conexão automaticamente"""
        self.disconnect()




