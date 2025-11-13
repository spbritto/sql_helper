"""
Testes da API
"""
import pytest


def test_health_check(client):
    """Testa o endpoint de health check"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_root_endpoint(client):
    """Testa o endpoint raiz"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_generate_query(client, sample_query):
    """Testa geração de query"""
    response = client.post("/api/query/generate", json=sample_query)
    assert response.status_code == 200
    data = response.json()
    assert "sql" in data
    assert "explanation" in data
    assert "confidence" in data


def test_generate_query_empty(client):
    """Testa geração de query com dados vazios"""
    response = client.post("/api/query/generate", json={"question": ""})
    # Deve retornar erro de validação
    assert response.status_code in [422, 500]

