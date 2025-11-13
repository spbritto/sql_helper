"""
Testes do módulo de parsing
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.parsing.text_parser import TextParser


def test_parse_simple_structure(sample_text_structure):
    """Testa parse de estrutura simples"""
    parser = TextParser()
    result = parser.parse(sample_text_structure)
    
    assert "tables" in result
    assert "relationships" in result
    assert len(result["tables"]) == 2
    
    # Verifica primeira tabela
    usuarios = result["tables"][0]
    assert usuarios["name"] == "usuarios"
    assert len(usuarios["fields"]) > 0


def test_parse_empty_content():
    """Testa parse de conteúdo vazio"""
    parser = TextParser()
    result = parser.parse("")
    
    assert "tables" in result
    assert len(result["tables"]) == 0


def test_parse_fields():
    """Testa parse de campos"""
    parser = TextParser()
    fields_str = "id (int, pk), nome (varchar), email (varchar, nullable)"
    fields = parser._parse_fields(fields_str)
    
    assert len(fields) == 3
    assert fields[0]["name"] == "id"
    assert fields[0]["primary_key"] == True
    assert fields[2]["nullable"] == True

