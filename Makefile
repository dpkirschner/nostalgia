.PHONY: help install test test-unit test-integration lint format check clean docker-up docker-down docker-logs docker-restart db-migrate db-upgrade db-downgrade db-revision load-data run dev

.DEFAULT_GOAL := help

help:
	@echo "Available commands:"
	@echo "  make install              Install dependencies with poetry"
	@echo "  make test                 Run all tests"
	@echo "  make test-unit            Run unit tests only"
	@echo "  make test-integration     Run integration tests only"
	@echo "  make test-coverage        Run tests with coverage report"
	@echo "  make lint                 Run ruff linter"
	@echo "  make format               Format code with black"
	@echo "  make format-check         Check code formatting without modifying"
	@echo "  make check                Run linting and format checks"
	@echo "  make clean                Clean up cache and build files"
	@echo "  make docker-up            Start docker containers"
	@echo "  make docker-down          Stop docker containers"
	@echo "  make docker-logs          Follow docker logs"
	@echo "  make docker-restart       Stop, rebuild, and start containers (foreground)"
	@echo "  make docker-clean         Stop containers and remove volumes"
	@echo "  make db-migrate           Run alembic migrations (upgrade)"
	@echo "  make db-upgrade           Upgrade database to head"
	@echo "  make db-downgrade         Downgrade database by 1 revision"
	@echo "  make db-revision          Create new alembic revision (use MSG='description')"
	@echo "  make db-reset             Reset database (downgrade to base and upgrade to head)"
	@echo "  make load-data            Load KC food inspections data"
	@echo "  make run                  Run the FastAPI application"
	@echo "  make dev                  Run the application in development mode with reload"
	@echo "  make shell                Open a Python shell with app context"
	@echo "  make db-shell             Open PostgreSQL shell"
	@echo "  make ci                   Run all CI checks (format-check, lint, test)"

install:
	poetry install

test:
	poetry run pytest tests/ -v

test-unit:
	poetry run pytest tests/unit/ -v

test-integration:
	poetry run pytest tests/integration/ -v

test-coverage:
	poetry run pytest tests/ -v --cov=app --cov=scripts --cov-report=html --cov-report=term

test-watch:
	poetry run pytest-watch tests/

lint:
	poetry run ruff check .

lint-fix:
	poetry run ruff check --fix .

format:
	poetry run black .

format-check:
	poetry run black --check .

check: format-check lint
	@echo "All checks passed!"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	rm -rf htmlcov/ .coverage 2>/dev/null || true
	@echo "Cleaned up cache and build files"

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-restart:
	docker-compose down
	docker-compose build
	docker-compose up

docker-clean:
	docker-compose down -v
	@echo "Warning: This removed all volumes including database data!"

docker-rebuild:
	docker-compose up -d --build

db-migrate: db-upgrade

db-upgrade:
	poetry run alembic upgrade head

db-downgrade:
	poetry run alembic downgrade -1

db-revision:
	@if [ -z "$(MSG)" ]; then \
		echo "Error: Please provide a message with MSG='your message'"; \
		echo "Example: make db-revision MSG='add user table'"; \
		exit 1; \
	fi
	poetry run alembic revision --autogenerate -m "$(MSG)"

db-reset:
	poetry run alembic downgrade base
	poetry run alembic upgrade head

db-shell:
	docker-compose exec postgres psql -U nostalgia -d nostalgia

load-data:
	@if [ ! -f "data/Food_Establishment_Inspection_Data_20251101.csv" ]; then \
		echo "Error: CSV file not found at data/Food_Establishment_Inspection_Data_20251101.csv"; \
		exit 1; \
	fi
	poetry run python scripts/load_kc_food_inspections.py data/Food_Establishment_Inspection_Data_20251101.csv

run:
	poetry run uvicorn app.main:app --host 0.0.0.0 --port 8080

dev:
	poetry run uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

shell:
	poetry run python -i -c "import asyncio; from app.db.session import AsyncSessionLocal; from app.models import *; print('App context loaded. AsyncSessionLocal available.')"

setup: install docker-up db-upgrade
	@echo "Setup complete! Run 'make dev' to start the development server."

ci:
	@echo "Running CI checks..."
	@echo "1/3 Checking code formatting..."
	@poetry run black --check .
	@echo "2/3 Running linter..."
	@poetry run ruff check .
	@echo "3/3 Running tests..."
	@poetry run pytest tests/ -v
	@echo ""
	@echo "✅ All CI checks passed!"
