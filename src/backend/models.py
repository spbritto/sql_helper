"""
Modelos Pydantic para validação de dados
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class DatabaseStructure(BaseModel):
    """Estrutura de banco de dados"""
    tables: List[Dict[str, Any]] = Field(
        ..., 
        description="Lista de tabelas do banco de dados"
    )
    relationships: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Relacionamentos entre tabelas"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadados adicionais"
    )
    created_at: datetime = Field(default_factory=datetime.now)


class NaturalLanguageQuery(BaseModel):
    """Query em linguagem natural"""
    question: str = Field(..., description="Pergunta em linguagem natural")
    structure_id: Optional[str] = Field(
        None, 
        description="ID da estrutura do banco de dados"
    )
    context: Optional[str] = Field(
        None,
        description="Contexto adicional para a query"
    )


class SQLQueryResponse(BaseModel):
    """Resposta com query SQL gerada"""
    sql: str = Field(..., description="Query SQL gerada")
    explanation: str = Field(..., description="Explicação da query")
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0,
        description="Nível de confiança da query gerada"
    )
    optimizations: List[str] = Field(
        default_factory=list,
        description="Sugestões de otimização"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Avisos sobre a query"
    )
    generated_at: datetime = Field(default_factory=datetime.now)


class FileUpload(BaseModel):
    """Informações sobre arquivo enviado"""
    filename: str
    content_type: str
    size: int
    upload_type: str = Field(
        ..., 
        description="Tipo de upload: 'text' ou 'image'"
    )


class QueryHistory(BaseModel):
    """Histórico de queries"""
    id: str
    question: str
    sql: str
    executed_at: datetime
    execution_time: Optional[float] = None
    success: bool
    error_message: Optional[str] = None


class OptimizationSuggestion(BaseModel):
    """Sugestão de otimização"""
    original_sql: str
    optimized_sql: str
    improvement_description: str
    estimated_performance_gain: Optional[str] = None


class HealthResponse(BaseModel):
    """Resposta de health check"""
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.now)
    services: Dict[str, str] = Field(default_factory=dict)


class DatabaseConnection(BaseModel):
    """Parâmetros de conexão com banco de dados"""
    db_type: str = Field(
        ..., 
        description="Tipo do banco: mysql, postgresql, sqlite, mssql"
    )
    host: str = Field(default="localhost", description="Host do banco de dados")
    port: Optional[int] = Field(None, description="Porta do banco (usa padrão se não fornecida)")
    username: str = Field(default="", description="Usuário do banco")
    password: str = Field(default="", description="Senha do banco")
    database: str = Field(..., description="Nome do banco de dados")
    connection_timeout: int = Field(
        default=10, 
        ge=1, 
        le=60, 
        description="Timeout de conexão em segundos"
    )
    additional_params: Optional[Dict[str, str]] = Field(
        None, 
        description="Parâmetros adicionais de conexão"
    )


class DatabaseConnectionTest(BaseModel):
    """Resposta do teste de conexão"""
    success: bool
    message: str
    dialect: Optional[str] = None
    table_count: Optional[int] = None
    error: Optional[str] = None
