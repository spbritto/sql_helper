# Guia de Contribuição

Obrigado por considerar contribuir com o Assistente SQL! 🎉

## Como Contribuir

### 1. Fork e Clone

```bash
# Fork o repositório no GitHub
# Clone seu fork
git clone https://github.com/seu-usuario/assistente-sql.git
cd assistente-sql
```

### 2. Configure o Ambiente

```bash
# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações
```

### 3. Crie uma Branch

```bash
git checkout -b feature/minha-nova-feature
# ou
git checkout -b fix/correcao-de-bug
```

### 4. Faça suas Alterações

- Escreva código limpo e bem documentado
- Siga as convenções de estilo do projeto
- Adicione testes para novas funcionalidades
- Atualize documentação quando necessário

### 5. Execute os Testes

```bash
# Testes unitários
pytest tests/ -v

# Cobertura de código
pytest tests/ --cov=src --cov-report=html

# Linting
flake8 src tests
black --check src tests
mypy src
```

### 6. Commit e Push

```bash
git add .
git commit -m "feat: adiciona nova funcionalidade X"
git push origin feature/minha-nova-feature
```

### 7. Abra um Pull Request

- Vá para o repositório original no GitHub
- Clique em "New Pull Request"
- Descreva suas alterações detalhadamente
- Aguarde revisão

## Convenções de Código

### Python Style Guide

- Seguimos [PEP 8](https://pep8.org/)
- Use `black` para formatação automática
- Máximo de 88 caracteres por linha
- Use type hints quando possível

### Commits

Seguimos [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: nova funcionalidade
fix: correção de bug
docs: atualização de documentação
style: formatação de código
refactor: refatoração
test: adição/atualização de testes
chore: tarefas de manutenção
```

### Docstrings

Use formato Google:

```python
def funcao_exemplo(parametro1: str, parametro2: int) -> bool:
    """
    Breve descrição da função.
    
    Descrição mais detalhada se necessário.
    
    Args:
        parametro1: Descrição do parâmetro 1
        parametro2: Descrição do parâmetro 2
        
    Returns:
        Descrição do retorno
        
    Raises:
        ValueError: Quando ocorre erro X
    """
    pass
```

### Testes

- Coloque testes em `tests/`
- Nome de arquivos: `test_*.py`
- Nome de funções: `test_*`
- Use fixtures quando apropriado
- Mantenha cobertura acima de 70%

## Estrutura de Branches

- `main`: código estável em produção
- `develop`: código em desenvolvimento
- `feature/*`: novas funcionalidades
- `fix/*`: correções de bugs
- `hotfix/*`: correções urgentes em produção

## Reportando Bugs

Use o template de issue no GitHub:

**Descrição:**
Descrição clara do bug

**Passos para Reproduzir:**
1. Passo 1
2. Passo 2
3. ...

**Comportamento Esperado:**
O que deveria acontecer

**Comportamento Atual:**
O que está acontecendo

**Ambiente:**
- OS: [Windows/Linux/Mac]
- Python: [versão]
- Versão do projeto: [versão]

**Screenshots:**
Se aplicável

## Solicitando Features

Use o template de feature request:

**Problema:**
Qual problema esta feature resolve?

**Solução Proposta:**
Como você sugere resolver?

**Alternativas Consideradas:**
Outras abordagens possíveis

**Contexto Adicional:**
Informações extras relevantes

## Código de Conduta

### Nossos Valores

- Seja respeitoso e inclusivo
- Aceite críticas construtivas
- Foque no que é melhor para a comunidade
- Mostre empatia com outros membros

### Comportamentos Inaceitáveis

- Linguagem ou imagens ofensivas
- Assédio público ou privado
- Publicar informações privadas de outros
- Conduta não profissional

## Revisão de Código

Revisores irão verificar:

- [ ] Código segue as convenções do projeto
- [ ] Testes passam e cobertura é adequada
- [ ] Documentação está atualizada
- [ ] Não há problemas de segurança
- [ ] Performance não foi degradada
- [ ] Commits seguem convenções

## Perguntas?

- Abra uma issue com a tag `question`
- Entre em contato com os mantenedores
- Consulte a documentação em `docs/`

## Reconhecimento

Contribuidores serão listados no README.md! 🌟

Obrigado por contribuir! ❤️

