"""
Serviço para gerenciar conexão automática com PostgreSQL do Docker
"""
from typing import Dict, Any, List, Optional
from loguru import logger
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from src.backend.config import settings
from src.backend.services.database_inspector import DatabaseInspector
from src.backend.models import DatabaseStructure


class DockerPostgresConnection:
    """Gerencia conexão automática com PostgreSQL rodando no Docker"""
    
    def __init__(self):
        self.host = settings.docker_postgres_host
        self.port = settings.docker_postgres_port
        self.user = settings.docker_postgres_user
        self.password = settings.docker_postgres_password
        self.default_db = settings.docker_postgres_default_db
        self.connection = None
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Testa conexão com o PostgreSQL do Docker
        
        Returns:
            Dict com status da conexão
        """
        try:
            logger.info("🔍 Testando conexão com Docker PostgreSQL...")
            
            # Tenta conectar ao database padrão
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.default_db,
                connect_timeout=5
            )
            
            # Busca versão do PostgreSQL
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            
            # Extrai versão limpa
            version_short = version.split(',')[0].replace('PostgreSQL ', '')
            
            cursor.close()
            conn.close()
            
            logger.success(f"✅ Conectado ao PostgreSQL: {version_short}")
            
            return {
                "connected": True,
                "message": "Conectado ao PostgreSQL no Docker",
                "version": version_short,
                "host": self.host,
                "port": self.port
            }
            
        except psycopg2.OperationalError as e:
            logger.error(f"❌ Erro ao conectar ao Docker PostgreSQL: {e}")
            return {
                "connected": False,
                "message": "Não foi possível conectar ao Docker PostgreSQL",
                "error": "Conexão com o banco de dados não estabelecida! Necessário acionar o suporte da aplicação.",
                "details": str(e)
            }
        except Exception as e:
            logger.error(f"❌ Erro inesperado: {e}")
            return {
                "connected": False,
                "message": "Erro inesperado ao testar conexão",
                "error": "Conexão com o banco de dados não estabelecida! Necessário acionar o suporte da aplicação.",
                "details": str(e)
            }
    
    def list_databases(self) -> Dict[str, Any]:
        """
        Lista todos os databases disponíveis no PostgreSQL
        
        Returns:
            Dict com lista de databases
        """
        try:
            logger.info("📊 Listando databases disponíveis...")
            
            # Conecta ao database padrão
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.default_db,
                connect_timeout=5
            )
            
            cursor = conn.cursor()
            
            # Busca databases (excluindo templates)
            cursor.execute("""
                SELECT 
                    datname,
                    pg_encoding_to_char(encoding) as encoding,
                    datcollate,
                    pg_size_pretty(pg_database_size(datname)) as size,
                    (SELECT rolname FROM pg_roles WHERE oid = datdba) as owner
                FROM pg_database
                WHERE datistemplate = false
                ORDER BY datname;
            """)
            
            databases = []
            for row in cursor.fetchall():
                databases.append({
                    "name": row[0],
                    "encoding": row[1],
                    "collate": row[2],
                    "size": row[3],
                    "owner": row[4]
                })
            
            cursor.close()
            conn.close()
            
            logger.success(f"✅ Encontrados {len(databases)} databases")
            
            return {
                "success": True,
                "databases": databases,
                "total": len(databases)
            }
            
        except psycopg2.Error as e:
            logger.error(f"❌ Erro ao listar databases: {e}")
            return {
                "success": False,
                "error": "Erro ao listar databases",
                "details": str(e),
                "databases": [],
                "total": 0
            }
        except Exception as e:
            logger.error(f"❌ Erro inesperado: {e}")
            return {
                "success": False,
                "error": "Erro inesperado ao listar databases",
                "details": str(e),
                "databases": [],
                "total": 0
            }
    
    def connect_and_extract_structure(self, database_name: str) -> Dict[str, Any]:
        """
        Conecta a um database específico e extrai sua estrutura
        
        Args:
            database_name: Nome do database para conectar
            
        Returns:
            Dict com estrutura extraída
        """
        try:
            logger.info(f"🔌 Conectando ao database '{database_name}'...")
            
            # Usa o DatabaseInspector para extrair estrutura
            inspector = DatabaseInspector()
            
            # Conecta ao database específico
            inspector.connect(
                db_type="postgresql",
                host=self.host,
                port=self.port,
                username=self.user,
                password=self.password,
                database=database_name,
                connection_timeout=10
            )
            
            # Extrai estrutura
            structure = inspector.extract_structure()
            
            # Desconecta
            inspector.disconnect()
            
            logger.success(
                f"✅ Estrutura extraída do database '{database_name}': "
                f"{len(structure.tables)} tabelas, {len(structure.relationships)} relacionamentos"
            )
            
            # Prepara resumo
            summary = {
                "total_tables": len(structure.tables),
                "total_relationships": len(structure.relationships),
                "dialect": "postgresql",
                "format": "database_connection",
                "database_name": database_name
            }
            
            return {
                "success": True,
                "structure": structure.dict(),
                "summary": summary,
                "message": f"Estrutura do database '{database_name}' importada com sucesso"
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao conectar e extrair estrutura: {e}")
            return {
                "success": False,
                "error": f"Erro ao conectar ao database '{database_name}'",
                "details": str(e)
            }
    
    def get_database_info(self, database_name: str) -> Dict[str, Any]:
        """
        Obtém informações detalhadas sobre um database específico
        
        Args:
            database_name: Nome do database
            
        Returns:
            Dict com informações do database
        """
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.default_db,
                connect_timeout=5
            )
            
            cursor = conn.cursor()
            
            # Busca informações do database
            cursor.execute("""
                SELECT 
                    datname,
                    pg_encoding_to_char(encoding) as encoding,
                    datcollate,
                    pg_size_pretty(pg_database_size(datname)) as size,
                    (SELECT rolname FROM pg_roles WHERE oid = datdba) as owner,
                    datconnlimit,
                    (SELECT count(*) FROM pg_stat_activity WHERE datname = %s) as active_connections
                FROM pg_database
                WHERE datname = %s;
            """, (database_name, database_name))
            
            row = cursor.fetchone()
            
            if row:
                info = {
                    "name": row[0],
                    "encoding": row[1],
                    "collate": row[2],
                    "size": row[3],
                    "owner": row[4],
                    "connection_limit": row[5],
                    "active_connections": row[6]
                }
            else:
                info = None
            
            cursor.close()
            conn.close()
            
            return {
                "success": True,
                "info": info
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar informações do database: {e}")
            return {
                "success": False,
                "error": str(e),
                "info": None
            }

