# Script de instalação de dependências
# Execute com: .\instalar_dependencias.ps1

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Instalando Dependencias do Projeto" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Limpar cache
Write-Host "[1/4] Limpando cache do pip..." -ForegroundColor Yellow
pip cache purge

# Atualizar ferramentas
Write-Host "[2/4] Atualizando pip, setuptools e wheel..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel

# Instalar pacotes essenciais
Write-Host "[3/4] Instalando pacotes essenciais..." -ForegroundColor Yellow

$pacotes = @(
    "fastapi==0.104.1",
    "uvicorn[standard]==0.24.0",
    "python-multipart==0.0.6",
    "pydantic==2.5.2",
    "pydantic-settings==2.1.0",
    "python-dotenv==1.0.0",
    "openai==1.6.1",
    "streamlit==1.29.0",
    "Pillow",
    "pytesseract==0.3.10",
    "loguru==0.7.2",
    "pytest==7.4.3",
    "httpx==0.25.2",
    "requests==2.31.0"
)

foreach ($pacote in $pacotes) {
    Write-Host "  → Instalando $pacote..." -ForegroundColor Gray
    pip install --no-cache-dir $pacote
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ✗ Erro ao instalar $pacote" -ForegroundColor Red
    } else {
        Write-Host "  ✓ $pacote instalado" -ForegroundColor Green
    }
}

# LangChain (por último, pode ter mais dependências)
Write-Host "[4/4] Instalando LangChain..." -ForegroundColor Yellow
pip install --no-cache-dir langchain==0.1.0
pip install --no-cache-dir langchain-openai==0.0.2

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Instalação Concluída!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Verifique se há erros acima." -ForegroundColor Yellow
Write-Host "Para testar, execute: python -c 'import fastapi, streamlit, langchain'" -ForegroundColor Yellow




