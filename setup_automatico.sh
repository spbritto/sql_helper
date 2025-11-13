#!/bin/bash
# Script de Setup Automático - Assistente SQL
# Bash Script para Linux/Mac

set -e

echo "🚀 Iniciando Setup do Assistente SQL..."
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Verificar Python
echo -e "${YELLOW}📌 Verificando Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ Python encontrado: $PYTHON_VERSION${NC}"
    PYTHON_CMD=python3
    PIP_CMD=pip3
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo -e "${GREEN}✅ Python encontrado: $PYTHON_VERSION${NC}"
    PYTHON_CMD=python
    PIP_CMD=pip
else
    echo -e "${RED}❌ Python não encontrado! Instale Python 3.10+ primeiro.${NC}"
    exit 1
fi

# Criar ambiente virtual
echo ""
echo -e "${YELLOW}📦 Criando ambiente virtual...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Ambiente virtual já existe. Removendo...${NC}"
    rm -rf venv
fi
$PYTHON_CMD -m venv venv
echo -e "${GREEN}✅ Ambiente virtual criado!${NC}"

# Ativar ambiente virtual
echo ""
echo -e "${YELLOW}🔌 Ativando ambiente virtual...${NC}"
source venv/bin/activate

# Instalar dependências
echo ""
echo -e "${YELLOW}📥 Instalando dependências (isso pode demorar alguns minutos)...${NC}"
$PIP_CMD install --upgrade pip
$PIP_CMD install -r requirements.txt
echo -e "${GREEN}✅ Dependências instaladas!${NC}"

# Configurar .env
echo ""
echo -e "${YELLOW}⚙️  Configurando variáveis de ambiente...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ Arquivo .env criado!${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANTE: Edite o arquivo .env e configure:${NC}"
    echo -e "${CYAN}   - OPENAI_API_KEY (obrigatório)${NC}"
    echo -e "${CYAN}   - TESSERACT_PATH (se usar OCR)${NC}"
else
    echo -e "${YELLOW}⚠️  Arquivo .env já existe. Pulando...${NC}"
fi

# Criar diretórios
echo ""
echo -e "${YELLOW}📁 Criando diretórios necessários...${NC}"
for dir in uploads temp logs; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo -e "${GREEN}✅ Diretório $dir criado${NC}"
    else
        echo -e "${YELLOW}⚠️  Diretório $dir já existe${NC}"
    fi
done

# Verificar Tesseract (opcional)
echo ""
echo -e "${YELLOW}🔍 Verificando Tesseract OCR (opcional)...${NC}"
if command -v tesseract &> /dev/null; then
    TESSERACT_VERSION=$(tesseract --version 2>&1 | head -n 1)
    echo -e "${GREEN}✅ Tesseract encontrado: $TESSERACT_VERSION${NC}"
else
    echo -e "${YELLOW}⚠️  Tesseract não encontrado (opcional para OCR)${NC}"
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo -e "${CYAN}   Instale com: sudo apt-get install tesseract-ocr tesseract-ocr-por${NC}"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo -e "${CYAN}   Instale com: brew install tesseract tesseract-lang${NC}"
    fi
fi

# Executar testes básicos
echo ""
echo -e "${YELLOW}🧪 Executando testes básicos...${NC}"
if pytest tests/ -v --tb=short; then
    echo -e "${GREEN}✅ Testes passaram!${NC}"
else
    echo -e "${YELLOW}⚠️  Alguns testes falharam (normal se API keys não configuradas)${NC}"
fi

# Resumo
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Setup Concluído!${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}📋 Próximos Passos:${NC}"
echo ""
echo -e "1️⃣  Configure a OPENAI_API_KEY no arquivo .env"
echo -e "2️⃣  Execute o backend:"
echo -e "${CYAN}    python src/backend/main.py${NC}"
echo -e "3️⃣  Em outro terminal, execute o frontend:"
echo -e "${CYAN}    streamlit run src/frontend/app.py${NC}"
echo ""
echo -e "${YELLOW}📚 Documentação:${NC}"
echo -e "${CYAN}   - README.md${NC}"
echo -e "${CYAN}   - docs/guia_inicio_rapido.md${NC}"
echo -e "${CYAN}   - COMANDOS_RAPIDOS.md${NC}"
echo ""
echo -e "${YELLOW}🌐 URLs após iniciar:${NC}"
echo -e "${CYAN}   - Frontend: http://localhost:8501${NC}"
echo -e "${CYAN}   - API: http://localhost:8000${NC}"
echo -e "${CYAN}   - API Docs: http://localhost:8000/docs${NC}"
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Bom trabalho! 🚀${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"

