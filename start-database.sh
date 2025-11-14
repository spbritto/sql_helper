#!/bin/bash
# Script para iniciar o banco de dados PostgreSQL com pgvector
# Autor: Assistente SQL
# Data: 2025-11-14

echo "🐳 Iniciando PostgreSQL com pgvector..."

# Verificar se Docker está rodando
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Inicie o Docker e tente novamente."
    exit 1
fi

# Parar container antigo se existir
echo "🛑 Verificando containers existentes..."
if docker ps -a --filter "name=postgres_rag" --format "{{.Names}}" | grep -q "postgres_rag"; then
    echo "   Parando container existente..."
    docker stop postgres_rag > /dev/null 2>&1
    docker rm postgres_rag > /dev/null 2>&1
    echo "   ✅ Container antigo removido"
fi

# Verificar se arquivo .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado. Criando com configurações padrão..."
    cat > .env << EOF
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
EOF
    echo "   ✅ Arquivo .env criado"
fi

# Criar diretório init-db se não existir
if [ ! -d "init-db" ]; then
    echo "📁 Criando diretório init-db..."
    mkdir -p init-db
    echo "   ✅ Diretório criado"
fi

# Iniciar serviços
echo "🚀 Iniciando serviços com Docker Compose..."
docker-compose -f docker-compose.pgvector.yml up -d postgres_rag

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ PostgreSQL com pgvector iniciado com sucesso!"
    echo ""
    echo "📊 Informações de Conexão:"
    echo "   Host:     localhost"
    echo "   Porta:    5432"
    echo "   Banco:    postgres_rag"
    echo "   Usuário:  postgres"
    echo "   Senha:    postgres"
    echo ""
    echo "🔍 Aguardando banco de dados ficar pronto..."
    
    # Aguardar o banco ficar pronto
    max_attempts=30
    attempt=0
    ready=false
    
    while [ $attempt -lt $max_attempts ] && [ "$ready" != "true" ]; do
        sleep 1
        attempt=$((attempt + 1))
        if docker exec postgres_rag pg_isready -U postgres -d postgres_rag > /dev/null 2>&1; then
            ready=true
        fi
        echo -n "."
    done
    
    echo ""
    
    if [ "$ready" = "true" ]; then
        echo "✅ Banco de dados está pronto!"
        echo ""
        echo "🔧 Verificando extensão pgvector..."
        docker exec postgres_rag psql -U postgres -d postgres_rag -c "\dx" | grep vector
        echo ""
        echo "📝 Comandos úteis:"
        echo "   Ver logs:    docker logs postgres_rag -f"
        echo "   Parar:       docker-compose -f docker-compose.pgvector.yml down"
        echo "   Reiniciar:   docker-compose -f docker-compose.pgvector.yml restart postgres_rag"
        echo "   Shell SQL:   docker exec -it postgres_rag psql -U postgres -d postgres_rag"
        echo ""
        echo "🌐 Você já pode conectar na interface!"
    else
        echo "⚠️  Tempo limite excedido. Verificar logs:"
        echo "   docker logs postgres_rag"
    fi
else
    echo ""
    echo "❌ Erro ao iniciar os serviços. Verifique os logs:"
    echo "   docker-compose -f docker-compose.pgvector.yml logs"
    exit 1
fi

