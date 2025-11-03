.PHONY: help install test test-unit test-integration test-coverage test-watch lint lint-fix format format-check check clean docker-up docker-down docker-logs docker-restart docker-recreate docker-recreate-fg docker-clean db-migrate db-upgrade db-downgrade db-revision db-reset db-shell load-data transform-data run dev shell setup ci

.DEFAULT_GOAL := help

# Check for .env.local and include it.
# This exports all variables from the file into the shell environment for all targets.
ifneq ($(wildcard .env.local),)
    include .env.local
    export
endif

# Define variables
POETRY = poetry
POETRY_RUN = $(POETRY) run
COMPOSE = docker compose
PYTEST = $(POETRY_RUN) pytest
RUFF = $(POETRY_RUN) ruff check
BLACK = $(POETRY_RUN) black
UVICORN = $(POETRY_RUN) uvicorn app.main:app --host 0.0.0.0 --port 8080
ALEMBIC = $(POETRY_RUN) alembic
PYTHON = $(POETRY_RUN) python

help: ## Show this help message
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies with poetry
	$(POETRY) install

test: ## Run all tests
	$(PYTEST) tests/ -v

test-unit: ## Run unit tests only
	$(PYTEST) tests/unit/ -v

test-integration: ## Run integration tests only
	$(PYTEST) tests/integration/ -v

test-coverage: ## Run tests with coverage report
	$(PYTEST) tests/ -v --cov=app --cov=scripts --cov-report=html --cov-report=term

test-watch: ## Run tests in watch mode
	$(POETRY_RUN) pytest-watch tests/

lint: ## Run ruff linter
	$(RUFF) .

lint-fix: ## Run ruff linter with auto-fix
	$(RUFF) --fix .

format: ## Format code with black
	$(BLACK) .

format-check: ## Check code formatting without modifying
	$(BLACK) --check .

check: format-check lint ## Run all format and lint checks
	@echo "✅ All formatting and lint checks passed!"

clean: ## Clean up cache and build files
	@find . -type d \( -name "__pycache__" -o -name "*.egg-info" -o -name ".pytest_cache" -o -name ".ruff_cache" \) -exec rm -rf {} + 2>/dev/null || true
	@find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete 2>/dev/null || true
	@rm -rf htmlcov/ .coverage 2>/dev/null || true
	@echo "Cleaned up cache and build files"

docker-up: ## Start docker containers in detached mode
	$(COMPOSE) up -d

docker-down: ## Stop docker containers
	$(COMPOSE) down

docker-logs: ## Follow docker logs
	$(COMPOSE) logs -f

docker-restart: ## Restart all containers without rebuilding
	$(COMPOSE) restart

docker-recreate: ## Stop, rebuild, and start containers in detached mode
	$(COMPOSE) up -d --build --force-recreate

docker-recreate-fg: ## Stop, rebuild, and start containers in foreground
	$(COMPOSE) down
	$(COMPOSE) build
	$(COMPOSE) up

docker-clean: ## Stop containers and remove all volumes (WARNING: data loss)
	$(COMPOSE) down -v
	@echo "⚠️  Warning: This removed all volumes including database data!"

db-migrate: db-upgrade ## Run alembic migrations (alias for db-upgrade)

db-upgrade: ## Upgrade database to head
	$(ALEMBIC) upgrade head

db-downgrade: ## Downgrade database by 1 revision
	$(ALEMBIC) downgrade -1

db-revision: ## Create new alembic revision (use MSG='description')
	@if [ -z "$(MSG)" ]; then \
		echo "Error: Please provide a message with MSG='your message'"; \
		echo "Example: make db-revision MSG='add user table'"; \
		exit 1; \
	fi
	$(ALEMBIC) revision --autogenerate -m "$(MSG)"

db-reset: ## Reset database (downgrade to base and upgrade to head)
	$(ALEMBIC) downgrade base
	$(ALEMBIC) upgrade head

db-shell: ## Open PostgreSQL shell
	$(COMPOSE) exec postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

load-data: ## Load KC food inspections data
	@if [ ! -f "data/Food_Establishment_Inspection_Data_20251101.csv" ]; then \
		echo "Error: CSV file not found at data/Food_Establishment_Inspection_Data_20251101.csv"; \
		exit 1; \
	fi
	$(PYTHON) -m scripts.load_kc_food_inspections data/Food_Establishment_Inspection_Data_20251101.csv

transform-data: ## Transform KC food inspections to locations and tenancies
	$(PYTHON) -m scripts.transform_kc_to_tenancies

run: ## Run the FastAPI application
	$(UVICORN)

dev: ## Run the application in development mode with reload
	$(UVICORN) --reload

shell: ## Open a Python shell with app context
	$(PYTHON) -i -c "import asyncio; from app.db.session import AsyncSessionLocal; from app.models import *; print('App context loaded. AsyncSessionLocal available.')"

setup: install docker-up db-upgrade ## Complete setup: install, start docker, and run migrations
	@echo "✅ Setup complete! Run 'make dev' to start the development server."

ci: format-check lint test ## Run all CI checks (format, lint, test)
	@echo ""
	@echo "✅ All CI checks passed!"
