# Script para iniciar o backend do Assistente SQL
# Este script garante que o ambiente virtual está ativo e inicia o servidor

Write-Host "🚀 Iniciando Assistente SQL - Backend" -ForegroundColor Cyan
Write-Host ""

# Ativa o ambiente virtual se existir
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "📦 Ativando ambiente virtual..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
} else {
    Write-Host "⚠️  Ambiente virtual não encontrado em .\venv" -ForegroundColor Yellow
    Write-Host "   Execute primeiro: python -m venv venv" -ForegroundColor Yellow
    Write-Host ""
}

# Verifica se está no diretório correto
if (-not (Test-Path ".\src\backend\main.py")) {
    Write-Host "❌ Erro: Arquivo main.py não encontrado!" -ForegroundColor Red
    Write-Host "   Execute este script na raiz do projeto." -ForegroundColor Red
    exit 1
}

Write-Host "🌐 Iniciando servidor FastAPI..." -ForegroundColor Green
Write-Host ""

# Executa o backend
python src\backend\main.py

