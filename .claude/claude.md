# Nostalgia API - Claude Code Repository Guide

## Project Overview

FastAPI backend for "What Used To Be Here" - tracking business location history using King County food inspection data.

**Stack:** Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), PostgreSQL 16, Alembic, Pydantic

## Issue Tracking with `bd` (Beads)

This project uses **bd** - a dependency-aware issue tracker designed for AI-supervised workflows.

### Quick Reference

```bash
bd quickstart              # Show full getting started guide
bd init                    # Initialize (auto-detects prefix from dir name)
bd create "Task title"     # Create new issue
bd list                    # List all issues
bd list --status open      # Filter by status
bd ready                   # Show ready work (no blocking dependencies)
bd show nostalgia-1        # Show issue details
bd update nostalgia-1 --status in_progress
bd close nostalgia-1
```

### Dependency Management

```bash
bd dep add nostalgia-2 nostalgia-1  # nostalgia-1 blocks nostalgia-2
bd dep tree nostalgia-1             # Visualize dependency tree
bd dep cycles                        # Detect circular dependencies
```

**Dependency Types:**
- `blocks` - Hard blocker (must complete before dependent can start)
- `related` - Soft connection (doesn't block progress)
- `parent-child` - Epic/subtask hierarchy
- `discovered-from` - Auto-created when AI discovers related work

### AI Workflow Integration

**Key Commands for Claude:**
- `bd ready` - Shows unblocked work ready to claim
- `bd create` - Create issues when discovering new work
- Use `--json` flags for programmatic parsing
- Dependencies prevent duplicate effort across AI sessions

### Database Location

bd stores data in SQLite:
1. `--db /path/to/db.db` flag (highest priority)
2. `$BEADS_DB` environment variable
3. `.beads/*.db` in current directory or ancestors
4. `~/.beads/default.db` (fallback)

### Extension Pattern

The bd database can be extended with custom tables:
```sql
CREATE TABLE nostalgia_etl_runs (
    id INTEGER PRIMARY KEY,
    issue_id TEXT REFERENCES issues(id),
    records_processed INTEGER,
    duration_seconds REAL,
    started_at TEXT,
    completed_at TEXT
);
```

This allows joining with the `issues` table for powerful queries linking work items to execution metrics.

## Architecture

```
API Layer (FastAPI)
    ↓
Repository Interface (Generic)
    ↓
PostgreSQL Implementation (SQLAlchemy async)
    ↓
Database (PostgreSQL/Supabase)
```

## Database Schema

### Core Tables

**locations** (public schema)
- `id`: Integer (auto-increment) - **NOTE:** Migration 001 must have `autoincrement=True`
- `lat`, `lon`: Float (rounded to 6 decimal places for identity)
- `address`: String(500)
- Unique identity: `(lat, lon, address)`
- Index: `idx_locations_lat_lon`

**tenancies** (public schema)
- `id`: Integer (auto-increment)
- `location_id`: Integer FK → locations.id (CASCADE)
- `business_name`: String(255)
- `category`: String(100), nullable
- `start_date`, `end_date`: Date, nullable
- `is_current`: Boolean (default False)
- `sources`: JSON (source tracking with dates/counts)
- **UNIQUE constraint:** `(location_id, business_name)` for upserts
- Index: `idx_tenancies_location_business` (unique)

**kc_food_inspections** (staging schema)
- Raw King County food inspection data
- Has `raw_line` field storing original CSV row as JSON

### Views

**staging.v_kc_norm**
- Normalizes inspection data:
  - Uppercases business names and addresses
  - Rounds lat/lon to 6 decimal places (`lat6`, `lon6`)
  - Trims and collapses whitespace
  - Filters out null/empty values

**staging.v_kc_latest**
- Gets latest inspection per `(lat6, lon6, street)` combination

## ETL Pipeline

### Data Flow

```
CSV → staging.kc_food_inspections → v_kc_norm → v_kc_latest
                                         ↓
                            locations + tenancies (normalized)
```

### Commands

```bash
make load-data          # Load CSV into staging
make transform-data     # Transform staging → locations/tenancies
```

### Critical Configuration

**File:** `app/core/config.py`

```python
round_places: int = 6                    # Coordinate rounding precision
recent_months: int = 18                  # Threshold for is_current flag
outdated_tenancy_months: int = 18        # When to mark tenancies outdated
```

### ETL Script: `scripts/transform_kc_to_tenancies.py`

**CRITICAL CONSTRAINTS:**

1. **PostgreSQL Parameter Limit:** Max 32,767 parameters per query
   - With 7 fields per tenancy: `batch_size <= 4,681`
   - **Default batch size: 4,000** (safe margin)
   - DO NOT increase above 4,600!

2. **Location Cache:** In-memory cache `(lat, lon, address) → location_id`
   - Pre-loads existing locations on startup
   - Prevents redundant SELECT queries
   - ~23 inspections per location on average

3. **Idempotent Upserts:**
   ```sql
   ON CONFLICT (location_id, business_name) DO UPDATE SET
     start_date = LEAST(existing, new),
     end_date = GREATEST(existing, new),
     is_current = recalculated,
     sources = merged
   ```

4. **Consistency Enforcement:**
   - Max 1 `is_current=true` per location_id
   - Keeps tenancy with latest `end_date`
   - Flips outdated tenancies to `is_current=false`

### Source Tracking Format

```json
[{
  "type": "seed",
  "dataset": "king_county_food_inspections",
  "first_seen": "2023-01-15",
  "last_seen": "2025-08-15",
  "inspection_count": 12
}]
```

## Code Structure

```
app/
├── api/                    # FastAPI route handlers
├── core/
│   └── config.py          # Settings (uses pydantic-settings)
├── db/
│   ├── session.py         # AsyncSessionLocal
│   └── base.py            # SQLAlchemy declarative base
├── middleware/            # Custom middleware
├── models/                # SQLAlchemy ORM models
│   ├── location.py        # Location model
│   ├── tenancy.py         # Tenancy model
│   └── kc_food_inspection.py
├── repositories/          # Repository interfaces (IRepository pattern)
│   ├── base.py
│   ├── location_repository.py
│   └── tenancy_repository.py
├── schemas/               # Pydantic schemas
└── services/              # Business logic

scripts/
├── __init__.py            # Makes it a module (required!)
├── load_kc_food_inspections.py
└── transform_kc_to_tenancies.py

alembic/
└── versions/
    ├── 001_initial_schema.py
    └── 002_kc_food_inspections_views.py
```

## Important Patterns & Conventions

### 1. Running Scripts as Modules

**Always use `-m` flag:**
```bash
poetry run python -m scripts.load_kc_food_inspections
poetry run python -m scripts.transform_kc_to_tenancies
```

**DO NOT use `sys.path.insert()`** - scripts should import normally as modules.

### 2. Async SQLAlchemy

```python
from app.db.session import AsyncSessionLocal

async with AsyncSessionLocal() as session:
    result = await session.execute(select(Location))
    await session.commit()
```

### 3. Batch Processing Pattern

```python
batch = []
for record in records:
    batch.append(entity)
    if len(batch) >= batch_size:
        session.add_all(batch)
        await session.commit()
        batch = []
```

### 4. Date Handling

Uses `python-dateutil` for relative dates:
```python
from dateutil.relativedelta import relativedelta
cutoff = datetime.now().date() - relativedelta(months=18)
```

## Common Gotchas & Fixes

### 1. Makefile Indentation

**MUST use TABS, not spaces!** Most editors default to spaces, but Makefiles require tabs.

If you get: `Makefile:27: *** missing separator. Stop.`
→ Replace spaces with tabs (use `\t` character)

### 2. Migration Schema Mismatches

**Always verify migration matches ORM models:**
- Migration 001 had `locations.id` as String(64), model had Integer
- Solution: Add `autoincrement=True` to Integer columns
- Also made `source`, `last_seen`, `parcel_pin` nullable (not in current model)

### 3. PostgreSQL Parameter Limits

**Error:** `the number of query arguments cannot exceed 32767`

**Cause:** Batch size too large for bulk INSERT
**Solution:** Reduce batch size (formula: `32767 / num_fields`)

### 4. Module Not Found Errors

**Error:** `ModuleNotFoundError: No module named 'app'`

**Causes:**
1. Script not run as module (use `-m` flag)
2. Missing `scripts/__init__.py`
3. Using `sys.path.insert()` instead of proper module imports

### 5. Database Downgrade Failures

**Error:** `index "idx_tenancies_location_business" does not exist`

**Cause:** Trying to drop an index that wasn't created in the current DB

**Solution:**
```bash
make docker-clean  # Nuclear option - drops all data
make docker-up
make db-upgrade
```

## Development Workflow

### Initial Setup

```bash
make setup          # Install deps, start docker, run migrations
make load-data      # Load inspection CSV
make transform-data # Transform to normalized tables
```

### Day-to-day

```bash
make dev           # Run API with hot reload
make test          # Run all tests
make lint          # Check linting
make format        # Format code with black
```

### Database Operations

```bash
make db-shell                           # Open psql
make db-revision MSG='add new table'    # Create migration
make db-upgrade                          # Apply migrations
make docker-clean && make docker-up     # Fresh start
```

## Testing

- `pytest` with async support (`pytest-asyncio`)
- Structure: `tests/unit/` and `tests/integration/`
- Coverage target: `pytest --cov=app --cov=scripts`

## Environment Variables

Required in `.env`:
```bash
DATABASE_URL=postgresql+asyncpg://nostalgia:nostalgia_dev@localhost:5432/nostalgia
ROUND_PLACES=6
RECENT_MONTHS=18
OUTDATED_TENANCY_MONTHS=18
LOG_LEVEL=INFO
```

## Performance Notes

### ETL Performance

**~277,000 inspection records → 10,584 locations + 11,302 tenancies in ~4 seconds**

Key optimizations:
1. **In-memory location cache** - Prevents 200k+ SELECT queries
2. **Batch commits** - 4,000 records at a time
3. **View-based normalization** - v_kc_norm does heavy lifting in SQL
4. **Bulk upserts** - PostgreSQL `ON CONFLICT DO UPDATE`

### Indexing Strategy

- `idx_locations_lat_lon` - Spatial queries
- `idx_tenancies_location_business` (UNIQUE) - Upsert key
- `idx_tenancies_location_id_is_current` - Current tenancy lookups

## Known Data Quality Issues

1. **Duplicate locations with slight coordinate drift:**
   - Example: `(47.770078, -122.145500)` vs `(47.770080, -122.145500)`
   - Same address, different lat/lon due to GPS precision
   - Creates separate location records

2. **High-turnover locations:**
   - Food courts, commissary kitchens show 20-30+ tenancies
   - Example: `19600 144TH AVE NE` has 31 tenancies

3. **Missing inspection dates:**
   - Some records have `inspection_dt = NULL`
   - Tenancy gets `start_date = NULL`, `is_current = False`

## Future Improvements

1. **Fuzzy location matching** - Merge near-duplicate locations
2. **Incremental ETL** - Process only new inspections
3. **Category inference** - Use business names to guess categories
4. **Address geocoding** - Normalize addresses before coordinate comparison
5. **Data validation** - Flag suspicious patterns (e.g., 30+ tenancies)

## Dependencies

Core:
- `fastapi ^0.115.0`
- `sqlalchemy[asyncio] ^2.0.35`
- `asyncpg ^0.30.0`
- `alembic ^1.14.0`
- `pydantic ^2.9.2`
- `pydantic-settings ^2.6.0`
- `python-dateutil ^2.9.0`

Dev:
- `pytest ^8.3.3`
- `pytest-asyncio ^0.24.0`
- `black ^24.10.0`
- `ruff ^0.7.0`

## Useful Queries

**Find high-turnover locations:**
```sql
SELECT l.address, COUNT(t.id) AS tenancy_count
FROM locations l
JOIN tenancies t ON t.location_id = l.id
GROUP BY l.id, l.address
ORDER BY tenancy_count DESC
LIMIT 20;
```

**Current businesses:**
```sql
SELECT t.business_name, l.address, t.end_date
FROM tenancies t
JOIN locations l ON l.id = t.location_id
WHERE t.is_current = true
ORDER BY t.end_date DESC;
```

**Inspection history for a location:**
```sql
SELECT business_name, inspection_date
FROM staging.kc_food_inspections
WHERE ROUND(latitude::numeric, 6) = 47.611234
  AND ROUND(longitude::numeric, 6) = -122.336789
ORDER BY inspection_date DESC;
```

## Using bd in Claude Sessions

### Recommended Workflow

**At the start of a session:**
```bash
bd ready                    # Check what work is ready
bd list --status open       # See all open issues
```

**When discovering new work:**
```bash
bd create "Add category inference to ETL"
bd create "Write integration tests for tenancy API" -d "Cover CRUD operations"
bd dep add nostalgia-2 nostalgia-1  # If nostalgia-1 blocks nostalgia-2
```

**When starting work:**
```bash
bd update nostalgia-3 --status in_progress
# ... do the work ...
bd close nostalgia-3 --reason "Implemented in scripts/infer_categories.py"
```

**When stuck or blocked:**
```bash
bd create "Debug coordinate rounding precision" -p 0
bd dep add nostalgia-5 nostalgia-4  # nostalgia-4 blocks nostalgia-5
bd update nostalgia-5 --status blocked
```

### Example: ETL Enhancement Session

```bash
# Check what's ready
$ bd ready
nostalgia-1: Add fuzzy location matching

# Claim the work
$ bd update nostalgia-1 --status in_progress

# Discover new subtasks while working
$ bd create "Research fuzzy string matching libraries" -p 1
$ bd create "Add Levenshtein distance to requirements" -p 1
$ bd create "Implement location merge logic" -p 0
$ bd dep add nostalgia-3 nostalgia-2  # Need library before implementing

# Complete the work
$ bd close nostalgia-2
$ bd close nostalgia-3
$ bd close nostalgia-1 --reason "Merged 847 duplicate locations"

# Next session can pick up from bd ready
```

### Integration with Future Improvements

The "Future Improvements" section above should be tracked as bd issues:

```bash
bd create "Implement fuzzy location matching" -p 0 -t feature
bd create "Add incremental ETL mode" -p 1 -t feature
bd create "Infer categories from business names" -p 2 -t feature
bd create "Add address geocoding normalization" -p 2 -t feature
bd create "Build data validation dashboard" -p 3 -t feature
```

Then use `bd dep add` to establish dependencies between them.

## Support

- GitHub Issues: (add repo URL)
- Documentation: `README.md`, this file
- API Docs (when running): `http://localhost:8080/docs`
- Task Management: `bd list` or `bd ready`
