# Script para iniciar o Backend
# Resolve problema de imports relativos

Write-Host "🚀 Iniciando Backend do Assistente SQL..." -ForegroundColor Green

# Verificar se venv existe
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Ambiente virtual não encontrado!" -ForegroundColor Red
    Write-Host "   Execute: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Verificar se .env existe
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Arquivo .env não encontrado!" -ForegroundColor Yellow
    Write-Host "   Configure a OPENAI_API_KEY no arquivo .env" -ForegroundColor Yellow
}

# Ativar ambiente virtual
Write-Host "🔌 Ativando ambiente virtual..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Verificar se a porta 8000 está livre
$port = 8000
$listener = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
if ($listener) {
    Write-Host "⚠️  Porta $port já está em uso!" -ForegroundColor Yellow
    Write-Host "   Matando processo anterior..." -ForegroundColor Yellow
    Stop-Process -Id $listener.OwningProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Backend iniciando em:" -ForegroundColor Green
Write-Host "  🌐 http://localhost:8000" -ForegroundColor White
Write-Host "  📚 Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Executar como módulo (resolve imports relativos)
python -m src.backend.main



