"""
Testes dos validadores
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.utils.validators import SQLValidator, FileValidator


def test_sql_is_read_only():
    """Testa validação de query read-only"""
    assert SQLValidator.is_read_only("SELECT * FROM users") == True
    assert SQLValidator.is_read_only("DELETE FROM users") == False
    assert SQLValidator.is_read_only("UPDATE users SET name='x'") == False


def test_sql_dangerous_operations():
    """Testa detecção de operações perigosas"""
    safe_query = "SELECT * FROM users"
    dangerous_query = "DROP TABLE users"
    
    is_dangerous, operations = SQLValidator.has_dangerous_operations(safe_query)
    assert is_dangerous == False
    
    is_dangerous, operations = SQLValidator.has_dangerous_operations(dangerous_query)
    assert is_dangerous == True
    assert "DROP" in operations


def test_sql_validate_syntax():
    """Testa validação de sintaxe"""
    valid_query = "SELECT * FROM users WHERE id = 1"
    invalid_query = "SELECT * FROM users WHERE (id = 1"
    
    is_valid, error = SQLValidator.validate_syntax(valid_query)
    assert is_valid == True
    
    is_valid, error = SQLValidator.validate_syntax(invalid_query)
    assert is_valid == False
    assert "parênteses" in error.lower()


def test_file_extension_validation():
    """Testa validação de extensão de arquivo"""
    assert FileValidator.is_allowed_extension("test.txt", "text") == True
    assert FileValidator.is_allowed_extension("test.png", "image") == True
    assert FileValidator.is_allowed_extension("test.exe", "text") == False


def test_file_size_validation():
    """Testa validação de tamanho de arquivo"""
    small_file = 1024  # 1KB
    large_file = 20 * 1024 * 1024  # 20MB
    
    assert FileValidator.is_valid_size(small_file) == True
    assert FileValidator.is_valid_size(large_file) == False

