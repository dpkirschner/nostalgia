# Nostalgia Backend

FastAPI backend for "What Used To Be Here" - tracking the history of businesses and locations.

## Setup

1. Install Poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
poetry install
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your Supabase connection string
```

4. Run database migrations:
```bash
poetry run alembic upgrade head
```

5. Start the server:
```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

## Development

Run tests:
```bash
poetry run pytest
```

Format code:
```bash
poetry run black .
poetry run ruff check --fix .
```

## Docker

Build:
```bash
docker build -t nostalgia-backend .
```

Run:
```bash
docker-compose up
```

## API Endpoints

- `GET /healthz` - Health check
- `GET /readyz` - Readiness check (DB connectivity)
- `GET /v1/locations` - Search locations by bounding box
- `GET /v1/locations/{id}` - Get location details with timeline
- `POST /v1/memories` - Submit a memory about a location
- `GET /metrics` - Prometheus metrics
