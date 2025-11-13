"""
Configuração de fixtures para pytest
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.backend.main import app


@pytest.fixture
def client():
    """Cliente de teste para a API"""
    return TestClient(app)


@pytest.fixture
def sample_text_structure():
    """Estrutura de banco de dados de exemplo em texto"""
    return """
    tabela: usuarios
    campos: id (int, pk), nome (varchar), email (varchar), data_cadastro (datetime)
    
    tabela: pedidos
    campos: id (int, pk), usuario_id (int, fk->usuarios), valor (decimal), status (varchar)
    """


@pytest.fixture
def sample_query():
    """Query de exemplo"""
    return {
        "question": "Liste todos os usuários",
        "context": None
    }

