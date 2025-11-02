# Nostalgia API

FastAPI backend for "What Used To Be Here" - tracking business location history.

## Architecture

The application uses a **generic data access layer** with a PostgreSQL implementation that works with both local PostgreSQL and Supabase:

```
API Layer (FastAPI)
    ↓
Service Layer (Business Logic)
    ↓
Repository Interface (Generic)
    ↓
PostgreSQL Implementation
    ↓
Database (PostgreSQL / Supabase)
```

## Local Development

### Prerequisites

- Python 3.12+
- Poetry
- Docker & Docker Compose

### Setup

1. **Install dependencies**:
   ```bash
   poetry install
   ```

2. **Create `.env` file**:
   ```bash
   cp .env.example .env
   ```

3. **Start PostgreSQL database**:
   ```bash
   docker-compose up postgres -d
   ```

4. **Run database migrations**:
   ```bash
   poetry run alembic upgrade head
   ```

5. **Start the API**:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

### Using Docker Compose

To run the entire stack (PostgreSQL + API):

```bash
docker-compose up
```

This will:
- Start PostgreSQL on port 5432
- Start the API on port 8080
- Automatically run migrations

## Database Options

The application supports both local PostgreSQL and Supabase using the same codebase:

### Local PostgreSQL (docker-compose)
```bash
DATABASE_URL=postgresql+asyncpg://nostalgia:nostalgia_dev@localhost:5432/nostalgia
```

### Supabase
```bash
DATABASE_URL=postgresql+asyncpg://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

Both use the same PostgreSQL implementation - just change the connection string!

## API Endpoints

- `GET /healthz` - Health check
- `GET /readyz` - Readiness check (includes database connectivity)
- `GET /metrics` - Prometheus metrics
- `GET /v1/locations` - List locations in bounding box
- `GET /v1/locations/{id}` - Get location details with timeline
- `POST /v1/memories` - Submit a memory for review

## Testing

Run all tests:
```bash
poetry run pytest
```

Run with coverage:
```bash
poetry run pytest --cov=app --cov-report=term-missing
```

Run only unit tests:
```bash
poetry run pytest tests/unit/
```

Run only integration tests:
```bash
poetry run pytest tests/integration/
```

## Code Structure

```
app/
├── api/                    # FastAPI route handlers
├── core/                   # Configuration
├── db/
│   ├── postgres/          # PostgreSQL implementation
│   └── base.py            # SQLAlchemy declarative base
├── middleware/            # Custom middleware
├── models/                # SQLAlchemy ORM models
├── repositories/          # Repository interfaces
├── schemas/               # Pydantic schemas
└── services/              # Business logic

tests/
├── unit/                  # Unit tests (mocked)
└── integration/           # API integration tests
```

## Development Workflow

1. Make changes to code
2. Run tests: `poetry run pytest`
3. Run linter: `poetry run ruff check .`
4. Format code: `poetry run black .`
5. Commit changes

## Migrations

Create a new migration:
```bash
poetry run alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
poetry run alembic upgrade head
```

Rollback one migration:
```bash
poetry run alembic downgrade -1
```

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `CORS_ORIGINS` - Allowed CORS origins (JSON array)
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
