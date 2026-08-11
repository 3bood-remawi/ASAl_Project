# Backend - Contract Intelligence Platform
FastAPI backend for the contract platform.

## Stack
- FastAPI
- SQLAlchemy + PostgreSQL (via Docker, pgvector-enabled)
- pgvector for embedding storage

## Local setup
Requires Docker Desktop.

1. Clone the repo and enter the `backend` folder.
2. Copy `.env.example` to `.env`.
3. Start the database:
   ```
   docker compose up -d
   ```
   This starts PostgreSQL 16 with pgvector already enabled (via the mounted init script) and a health check, so it's ready as soon as the container reports healthy. Data persists across restarts in a named volume.
4. Install dependencies:
   ```
   python -m venv venv
   venv\Scripts\Activate
   pip install -r requirements.txt
   ```
5. Run migrations:
   ```
   alembic upgrade head
   ```
6. Start the API:
   ```
   uvicorn app.main:app --reload
   ```
7. Visit http://127.0.0.1:8000/docs

## Database migrations

Schema changes go through Alembic — never edit the database by hand and never rely on `create_all()`.

- Apply all migrations:
  ```
  alembic upgrade head
  ```
- Create a new migration after changing a model:
  ```
  alembic revision --autogenerate -m "Describe the change"
  ```
  Review the generated file before committing — autogenerate doesn't reliably detect extension requirements (e.g. `CREATE EXTENSION IF NOT EXISTS vector`) or some index types, so check those by hand.
- Roll back the last migration:
  ```
  alembic downgrade -1
  ```

## Seed data

To populate a fresh database with a demo organization, one Editor, and one Approver:
```
python scripts/seed.py
```
Safe to run more than once — it checks for existing records first and won't create duplicates.

## Data model (Task 833/851 - Sprint 2/3 schema)
Six tables built per mentor spec, tested and confirmed working against Postgres + pgvector:
- organization - tenant record
- app_user - id, organization_id, external_id, email, full_name, role, is_active
- contract - id, organization_id, name, status, created_by, created_at
- contract_version - file metadata, processing_status, no circular FK (current version derived via MAX(version_number))
- processing_job - tracks async pipeline stage/status/retries
- document_chunk - id, organization_id, version_id, page_number, chunk_order, bounding_boxes (JSONB), char_start, char_end, text, language, heading_path, token_count, embedding

## File storage (Task 839)
Contract files go through `app/storage`. Callers work in keys, so nothing outside that package knows whether the file is on disk or in Azure.

```python
from app.storage import build_key, get_storage

storage = get_storage()
key = build_key(organization_id, contract_id, version_id, upload.filename)
storage.save(key, upload.file)
```

Keys are `{organization_id}/{contract_id}/{version_id}/{filename}`. The filename is sanitised in `build_key`, and the local backend re-checks the resolved path so a key cannot point outside the storage root.

`LocalFileStorage` runs this sprint, under `UPLOAD_DIR`. `AzureBlobStorage` implements the same interface and is selected with `STORAGE_BACKEND=azure_blob` - it raises "not configured" until the subscription exists and `azure-storage-blob` is in requirements.

No delete and no overwrite anywhere in the interface, per NFR-1. `url_for()` returns `/api/files/{key}` on local.

## Shared database access

Every endpoint receives its database session through `get_db`. Do not create
database sessions manually inside routes.

The current organization is provided by `current_organization_id`. Read queries
must use helpers from `app/data_access`, where the organization filter is always
applied.

Example:

```python
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import current_organization_id
from app.data_access.contracts import get_contracts

router = APIRouter()


@router.get("/")
def list_contracts(
    db: Session = Depends(get_db),
    organization_id: UUID = Depends(current_organization_id),
):
    return get_contracts(db, organization_id)
```

Do not write `Contract.organization_id` filters directly inside routes. Keep
tenant-scoped query logic inside the shared read helpers.
