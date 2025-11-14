"""
Configurações da aplicação
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # API
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_debug: bool = os.getenv("API_DEBUG", "True").lower() == "true"
    
    # OpenAI / LLM
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    openai_temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))
    
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL", 
        f"sqlite:///{BASE_DIR}/assistente_sql.db"
    )
    
    # Docker PostgreSQL (configuração padrão para conexão automática)
    docker_postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    docker_postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    docker_postgres_user: str = os.getenv("POSTGRES_USER", "postgres")
    docker_postgres_password: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    docker_postgres_default_db: str = os.getenv("POSTGRES_DEFAULT_DB", "postgres")
    docker_postgres_db: str = os.getenv("POSTGRES_DB", "rag")
    
    # OCR
    tesseract_path: Optional[str] = os.getenv("TESSERACT_PATH")
    ocr_language: str = os.getenv("OCR_LANGUAGE", "por")
    
    # Upload
    max_upload_size: int = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))
    allowed_extensions: str = os.getenv(
        "ALLOWED_EXTENSIONS", 
        "txt,png,jpg,jpeg,pdf"
    )
    
    @property
    def allowed_extensions_list(self) -> list[str]:
        """Retorna lista de extensões permitidas"""
        return self.allowed_extensions.split(",")
    
    # Diretórios
    uploads_dir: Path = BASE_DIR / "uploads"
    temp_dir: Path = BASE_DIR / "temp"
    logs_dir: Path = BASE_DIR / "logs"
    
    # Logs
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "logs/app.log")
    
    # Segurança
    secret_key: str = os.getenv(
        "SECRET_KEY", 
        "sua_chave_secreta_super_segura_aqui"
    )
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    
    # Configurações de conexão com banco de dados
    db_connection_timeout: int = int(os.getenv("DB_CONNECTION_TIMEOUT", "10"))
    db_connection_max_retries: int = int(os.getenv("DB_CONNECTION_MAX_RETRIES", "3"))
    db_allowed_hosts: Optional[str] = os.getenv("DB_ALLOWED_HOSTS")  # Lista separada por vírgula
    db_enable_ssl: bool = os.getenv("DB_ENABLE_SSL", "False").lower() == "true"
    
    @property
    def db_allowed_hosts_list(self) -> Optional[list[str]]:
        """Retorna lista de hosts permitidos para conexão"""
        if self.db_allowed_hosts:
            return [host.strip() for host in self.db_allowed_hosts.split(",")]
        return None
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Cria diretórios necessários
        self.uploads_dir.mkdir(exist_ok=True, parents=True)
        self.temp_dir.mkdir(exist_ok=True, parents=True)
        self.logs_dir.mkdir(exist_ok=True, parents=True)


# Instância global de configurações
settings = Settings()

