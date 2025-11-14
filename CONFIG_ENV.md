# 🔐 Configurações de Ambiente (.env)

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```env
# Configurações do Banco de Dados PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=postgres_rag
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# URL de conexão completa
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres_rag

# Configurações da API
API_HOST=0.0.0.0
API_PORT=8000

# OpenAI (se estiver usando)
OPENAI_API_KEY=sua_chave_aqui

# Outras configurações
LOG_LEVEL=INFO
DEBUG=False
```

## 💡 Como Criar

**PowerShell:**
```powershell
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
```

**Manualmente:**
1. Crie um arquivo chamado `.env` na raiz do projeto
2. Copie o conteúdo acima
3. Ajuste as configurações conforme necessário

