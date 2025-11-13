# Script de Setup Automático - Assistente SQL
# PowerShell Script para Windows

Write-Host "🚀 Iniciando Setup do Assistente SQL..." -ForegroundColor Green
Write-Host ""

# Verificar Python
Write-Host "📌 Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python não encontrado! Instale Python 3.10+ primeiro." -ForegroundColor Red
    exit 1
}

# Criar ambiente virtual
Write-Host ""
Write-Host "📦 Criando ambiente virtual..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "⚠️  Ambiente virtual já existe. Removendo..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force venv
}
python -m venv venv
Write-Host "✅ Ambiente virtual criado!" -ForegroundColor Green

# Ativar ambiente virtual
Write-Host ""
Write-Host "🔌 Ativando ambiente virtual..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Instalar dependências
Write-Host ""
Write-Host "📥 Instalando dependências (isso pode demorar alguns minutos)..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "✅ Dependências instaladas!" -ForegroundColor Green

# Configurar .env
Write-Host ""
Write-Host "⚙️  Configurando variáveis de ambiente..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Arquivo .env criado!" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANTE: Edite o arquivo .env e configure:" -ForegroundColor Yellow
    Write-Host "   - OPENAI_API_KEY (obrigatório)" -ForegroundColor Cyan
    Write-Host "   - TESSERACT_PATH (se usar OCR)" -ForegroundColor Cyan
} else {
    Write-Host "⚠️  Arquivo .env já existe. Pulando..." -ForegroundColor Yellow
}

# Criar diretórios
Write-Host ""
Write-Host "📁 Criando diretórios necessários..." -ForegroundColor Yellow
@("uploads", "temp", "logs") | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ | Out-Null
        Write-Host "✅ Diretório $_ criado" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Diretório $_ já existe" -ForegroundColor Yellow
    }
}

# Verificar Tesseract (opcional)
Write-Host ""
Write-Host "🔍 Verificando Tesseract OCR (opcional)..." -ForegroundColor Yellow
try {
    $tesseractVersion = tesseract --version 2>&1 | Select-Object -First 1
    Write-Host "✅ Tesseract encontrado: $tesseractVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Tesseract não encontrado (opcional para OCR)" -ForegroundColor Yellow
    Write-Host "   Baixe em: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Cyan
}

# Executar testes básicos
Write-Host ""
Write-Host "🧪 Executando testes básicos..." -ForegroundColor Yellow
pytest tests/ -v --tb=short
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Testes passaram!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Alguns testes falharam (normal se API keys não configuradas)" -ForegroundColor Yellow
}

# Resumo
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ Setup Concluído!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Próximos Passos:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1️⃣  Configure a OPENAI_API_KEY no arquivo .env" -ForegroundColor White
Write-Host "2️⃣  Execute o backend:" -ForegroundColor White
Write-Host "    python src/backend/main.py" -ForegroundColor Cyan
Write-Host "3️⃣  Em outro terminal, execute o frontend:" -ForegroundColor White
Write-Host "    streamlit run src/frontend/app.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "📚 Documentação:" -ForegroundColor Yellow
Write-Host "   - README.md" -ForegroundColor Cyan
Write-Host "   - docs/guia_inicio_rapido.md" -ForegroundColor Cyan
Write-Host "   - COMANDOS_RAPIDOS.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 URLs após iniciar:" -ForegroundColor Yellow
Write-Host "   - Frontend: http://localhost:8501" -ForegroundColor Cyan
Write-Host "   - API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   - API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Bom trabalho! 🚀" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan

