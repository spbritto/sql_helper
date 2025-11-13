.PHONY: help install setup run-backend run-frontend test lint clean docker-up docker-down

help:
	@echo "Comandos disponíveis:"
	@echo "  make install       - Instala dependências"
	@echo "  make setup         - Configura ambiente inicial"
	@echo "  make run-backend   - Executa backend"
	@echo "  make run-frontend  - Executa frontend"
	@echo "  make test          - Executa testes"
	@echo "  make lint          - Executa linters"
	@echo "  make clean         - Limpa arquivos temporários"
	@echo "  make docker-up     - Inicia containers Docker"
	@echo "  make docker-down   - Para containers Docker"

install:
	pip install -r requirements.txt

setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Arquivo .env criado. Configure suas variáveis de ambiente."; \
	fi
	mkdir -p uploads temp logs
	@echo "Setup concluído!"

run-backend:
	python src/backend/main.py

run-frontend:
	streamlit run src/frontend/app.py

test:
	pytest tests/ -v --cov=src --cov-report=html

lint:
	flake8 src tests
	black --check src tests
	mypy src

format:
	black src tests

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov
	rm -rf temp/*

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

