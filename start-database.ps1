# Script para iniciar o banco de dados PostgreSQL com pgvector
# Autor: Assistente SQL
# Data: 2025-11-14

Write-Host "🐳 Iniciando PostgreSQL com pgvector..." -ForegroundColor Cyan

# Verificar se Docker está rodando
$dockerRunning = docker ps 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker não está rodando. Inicie o Docker Desktop e tente novamente." -ForegroundColor Red
    exit 1
}

# Parar container antigo se existir
Write-Host "🛑 Verificando containers existentes..." -ForegroundColor Yellow
$existingContainer = docker ps -a --filter "name=postgres_rag" --format "{{.Names}}"
if ($existingContainer -eq "postgres_rag") {
    Write-Host "   Parando container existente..." -ForegroundColor Yellow
    docker stop postgres_rag | Out-Null
    docker rm postgres_rag | Out-Null
    Write-Host "   ✅ Container antigo removido" -ForegroundColor Green
}

# Verificar se arquivo .env existe
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Arquivo .env não encontrado. Criando com configurações padrão..." -ForegroundColor Yellow
    @"
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=postgres_rag
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres_rag
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
DEBUG=False
"@ | Out-File -FilePath .env -Encoding UTF8
    Write-Host "   ✅ Arquivo .env criado" -ForegroundColor Green
}

# Criar diretório init-db se não existir
if (-not (Test-Path "init-db")) {
    Write-Host "📁 Criando diretório init-db..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "init-db" | Out-Null
    Write-Host "   ✅ Diretório criado" -ForegroundColor Green
}

# Iniciar serviços
Write-Host "🚀 Iniciando serviços com Docker Compose..." -ForegroundColor Cyan
docker-compose -f docker-compose.pgvector.yml up -d postgres_rag

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ PostgreSQL com pgvector iniciado com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Informações de Conexão:" -ForegroundColor Cyan
    Write-Host "   Host:     localhost" -ForegroundColor White
    Write-Host "   Porta:    5432" -ForegroundColor White
    Write-Host "   Banco:    postgres_rag" -ForegroundColor White
    Write-Host "   Usuário:  postgres" -ForegroundColor White
    Write-Host "   Senha:    postgres" -ForegroundColor White
    Write-Host ""
    Write-Host "🔍 Aguardando banco de dados ficar pronto..." -ForegroundColor Yellow
    
    # Aguardar o banco ficar pronto
    $maxAttempts = 30
    $attempt = 0
    $ready = $false
    
    while ($attempt -lt $maxAttempts -and -not $ready) {
        Start-Sleep -Seconds 1
        $attempt++
        $healthCheck = docker exec postgres_rag pg_isready -U postgres -d postgres_rag 2>&1
        if ($LASTEXITCODE -eq 0) {
            $ready = $true
        }
        Write-Host "." -NoNewline -ForegroundColor Yellow
    }
    
    Write-Host ""
    
    if ($ready) {
        Write-Host "✅ Banco de dados está pronto!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🔧 Verificando extensão pgvector..." -ForegroundColor Cyan
        docker exec postgres_rag psql -U postgres -d postgres_rag -c "\dx" | Select-String "vector"
        Write-Host ""
        Write-Host "📝 Comandos úteis:" -ForegroundColor Cyan
        Write-Host "   Ver logs:    docker logs postgres_rag -f" -ForegroundColor White
        Write-Host "   Parar:       docker-compose -f docker-compose.pgvector.yml down" -ForegroundColor White
        Write-Host "   Reiniciar:   docker-compose -f docker-compose.pgvector.yml restart postgres_rag" -ForegroundColor White
        Write-Host "   Shell SQL:   docker exec -it postgres_rag psql -U postgres -d postgres_rag" -ForegroundColor White
        Write-Host ""
        Write-Host "🌐 Você já pode conectar na interface!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Tempo limite excedido. Verificar logs:" -ForegroundColor Yellow
        Write-Host "   docker logs postgres_rag" -ForegroundColor White
    }
} else {
    Write-Host ""
    Write-Host "❌ Erro ao iniciar os serviços. Verifique os logs:" -ForegroundColor Red
    Write-Host "   docker-compose -f docker-compose.pgvector.yml logs" -ForegroundColor White
    exit 1
}

