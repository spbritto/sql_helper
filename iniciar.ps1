# Script Rápido de Inicialização - Windows PowerShell
# Execute este script para iniciar o Assistente SQL rapidamente

Write-Host "🚀 Iniciando Assistente SQL..." -ForegroundColor Green
Write-Host ""

# Verificar se o ambiente virtual existe
if (-not (Test-Path "venv")) {
    Write-Host "❌ Ambiente virtual não encontrado!" -ForegroundColor Red
    Write-Host "   Execute primeiro: .\setup_automatico.ps1" -ForegroundColor Yellow
    exit 1
}

# Verificar se .env existe
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Arquivo .env não encontrado!" -ForegroundColor Yellow
    Write-Host "   Copiando .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Configure a OPENAI_API_KEY no arquivo .env" -ForegroundColor Green
}

Write-Host "🔌 Ativando ambiente virtual..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Para iniciar a aplicação, execute em terminais separados:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Terminal 1 - Backend:" -ForegroundColor Green
Write-Host "  python src/backend/main.py" -ForegroundColor White
Write-Host ""
Write-Host "Terminal 2 - Frontend:" -ForegroundColor Green
Write-Host "  streamlit run src/frontend/app.py" -ForegroundColor White
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pressione qualquer tecla para iniciar o backend..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host ""
Write-Host "🚀 Iniciando Backend..." -ForegroundColor Green
python src/backend/main.py

