# 🚀 SQL Helper

**Assistente inteligente que transforma linguagem natural em queries SQL otimizadas**

SQL Helper é uma ferramenta poderosa que permite extrair estruturas de bancos de dados (via texto ou imagens) e gerar queries SQL automaticamente através de perguntas em linguagem natural.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## ✨ Funcionalidades

- 🔍 **Extração Inteligente**: Capture estruturas de BD a partir de texto ou imagens (OCR)
- 💬 **Linguagem Natural**: Faça perguntas simples e receba queries SQL prontas
- ⚡ **Otimização Automática**: Queries são geradas já otimizadas
- 🎨 **Interface Amigável**: Frontend interativo com Streamlit
- 📊 **API RESTful**: Backend robusto com FastAPI
- 🧪 **Testado**: Suíte de testes automatizados

---

## 🎯 Como Funciona?

1. **Carregue sua estrutura**: Cole texto ou faça upload de uma imagem da estrutura do seu banco
2. **Faça perguntas**: Use linguagem natural como "Liste os 10 clientes com mais pedidos"
3. **Receba a query**: O sistema gera SQL otimizado pronto para usar

---

## 📦 Instalação Rápida

### Pré-requisitos

- Python 3.10 ou superior
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) (para processar imagens)
- Chave API da OpenAI

### Passo a Passo

1️⃣ **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/SQL_Helper.git
cd SQL_Helper
```

2️⃣ **Crie e ative o ambiente virtual**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3️⃣ **Instale as dependências**
```bash
pip install -r requirements.txt
```

4️⃣ **Configure as variáveis de ambiente**

Crie um arquivo `.env` na raiz do projeto:
```env
OPENAI_API_KEY=sua_chave_aqui
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

5️⃣ **Execute a aplicação**

**Backend:**
```bash
python src/backend/main.py
```
🌐 API disponível em: http://localhost:8000

**Frontend:**
```bash
streamlit run src/frontend/app.py
```
🌐 Interface disponível em: http://localhost:8501

---

## 📖 Exemplo de Uso

### 1. Defina sua estrutura de banco

```sql
tabela: clientes
campos: id (int, pk), nome (varchar), email (varchar), criado_em (datetime)

tabela: pedidos
campos: id (int, pk), cliente_id (int, fk->clientes), valor (decimal), status (varchar)
```

### 2. Faça perguntas em português

- *"Quais clientes fizeram pedidos acima de R$ 1000?"*
- *"Mostre o total de vendas por mês"*
- *"Liste clientes sem pedidos nos últimos 90 dias"*

### 3. Receba a query SQL otimizada

```sql
SELECT c.nome, c.email, COUNT(p.id) as total_pedidos
FROM clientes c
LEFT JOIN pedidos p ON c.id = p.cliente_id
WHERE p.valor > 1000
GROUP BY c.id, c.nome, c.email
ORDER BY total_pedidos DESC;
```

---

## 🏗️ Estrutura do Projeto

```
SQL_Helper/
├── src/
│   ├── backend/          # API FastAPI
│   │   ├── main.py       # Ponto de entrada da API
│   │   ├── routes/       # Endpoints REST
│   │   └── services/     # Lógica de negócio
│   ├── frontend/         # Interface Streamlit
│   ├── ocr/              # Processamento de imagens
│   ├── parsing/          # Análise de texto
│   └── utils/            # Funções auxiliares
├── tests/                # Testes automatizados
├── requirements.txt      # Dependências Python
└── README.md            # Este arquivo
```

---

## 🛠️ Tecnologias

| Categoria | Tecnologia |
|-----------|-----------|
| **Backend** | FastAPI, Uvicorn |
| **Frontend** | Streamlit |
| **IA** | LangChain, OpenAI GPT-4 |
| **OCR** | Tesseract, EasyOCR, Pytesseract |
| **Testes** | Pytest |
| **Formatação** | Black, isort |

---

## 🧪 Testes

Execute a suíte de testes:

```bash
# Todos os testes
pytest tests/ -v

# Com cobertura
pytest tests/ -v --cov=src --cov-report=html
```

---

## 🚢 Deploy com Docker

```bash
# Construir e executar com Docker Compose
docker-compose up -d

# Ou individualmente
docker build -f Dockerfile.backend -t sql-helper-backend .
docker build -f Dockerfile.frontend -t sql-helper-frontend .
```

---

## 🤝 Contribuindo

Contribuições são muito bem-vindas! 

1. Faça um Fork do projeto
2. Crie sua Feature Branch (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a Branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para mais detalhes.

---

## 📝 Licença

Este projeto está sob a licença MIT. Consulte [LICENSE](LICENSE) para mais informações.

---

## 💡 Suporte

- 🐛 **Issues**: [GitHub Issues](https://github.com/seu-usuario/SQL_Helper/issues)
- 📧 **Email**: suporte@sqlhelper.com
- 💬 **Discussões**: [GitHub Discussions](https://github.com/seu-usuario/SQL_Helper/discussions)

---

<p align="center">Desenvolvido com ❤️ para simplificar seu trabalho com SQL</p>

