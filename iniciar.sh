#!/bin/bash
# Script Rápido de Inicialização - Linux/Mac

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

echo -e "${GREEN}🚀 Iniciando Assistente SQL...${NC}"
echo ""

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Ambiente virtual não encontrado!${NC}"
    echo -e "${YELLOW}   Execute primeiro: ./setup_automatico.sh${NC}"
    exit 1
fi

# Verificar se .env existe
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Arquivo .env não encontrado!${NC}"
    echo -e "${YELLOW}   Copiando .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ Configure a OPENAI_API_KEY no arquivo .env${NC}"
fi

echo -e "${YELLOW}🔌 Ativando ambiente virtual...${NC}"
source venv/bin/activate

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Para iniciar a aplicação, execute em terminais separados:${NC}"
echo ""
echo -e "${GREEN}Terminal 1 - Backend:${NC}"
echo -e "${WHITE}  python src/backend/main.py${NC}"
echo ""
echo -e "${GREEN}Terminal 2 - Frontend:${NC}"
echo -e "${WHITE}  streamlit run src/frontend/app.py${NC}"
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Pressione Enter para iniciar o backend...${NC}"
read

echo ""
echo -e "${GREEN}🚀 Iniciando Backend...${NC}"
python src/backend/main.py

