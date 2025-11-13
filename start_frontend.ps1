# Script para iniciar o Frontend
Write-Host "🎨 Iniciando Frontend do Assistente SQL..." -ForegroundColor Green

# Verificar se venv existe
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Ambiente virtual não encontrado!" -ForegroundColor Red
    exit 1
}

# Ativar ambiente virtual
Write-Host "🔌 Ativando ambiente virtual..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

Write-Host ""
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Frontend iniciando em:" -ForegroundColor Green
Write-Host "  🎨 http://localhost:8501" -ForegroundColor White
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Iniciar Streamlit
streamlit run src/frontend/app.py




