# Backend - Contract Intelligence Platform
FastAPI backend for the contract platform.

## Stack
- FastAPI
- Azure Cosmos DB (documents, not tables) via the local emulator
- Vector search in Cosmos for retrieval

## Local setup
Requires Docker Desktop.

1. Clone the repo and enter the `backend` folder.
2. Copy `.env.example` to `.env`.
3. Start Cosmos:
   ```
   docker compose up -d
   ```
   This runs the Cosmos emulator. It takes a couple of minutes on a cold start, so
   wait for the container to report healthy before starting the API.
4. Install dependencies:
   ```
   python -m venv venv
   venv\Scripts\Activate
   pip install -r requirements.txt
   ```
5. Create the demo organization and users:
   ```
   python scripts/seed.py
   ```
6. Start the API:
   ```
   uvicorn app.main:app --reload
   ```
7. Visit http://127.0.0.1:8000/docs

The database and both containers are created on startup, so there are no migrations.
The emulator does not keep data across restarts, so re-run `scripts/seed.py` after
bringing it up again.

## Documents

There are two containers, both partitioned by `organizationId`:

- `contracts` - organization, user, contract, version and job documents, told apart by `type`
- `chunks` - chunk documents, with the vector index used for retrieval

Every shape lives in `app/documents/shapes.py`. Build a document there and write
`document.to_item()` rather than assembling a dict by hand, so field names stay the
same everywhere. Fields are camelCase in Cosmos and snake_case in Python.

```python
from app.documents.shapes import ContractDocument

contract = ContractDocument(
    id=contract_id, organization_id=org_id, name="Nexa Services", created_by=user_id
)
container.upsert_item(contract.to_item())
```

`python scripts/check_documents.py` builds one of every shape and checks the field
names. It needs no database and runs in CI.

Writing several documents that belong together goes in one `execute_item_batch` on
the same partition key, so they cannot half save.

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

The current organization comes from `current_organization_id`. Read queries must use
helpers from `app/data_access`, where the organization filter is always applied.

```python
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import current_organization_id
from app.data_access.contracts import get_contracts

router = APIRouter()


@router.get("/")
def list_contracts(organization_id: UUID = Depends(current_organization_id)):
    return get_contracts(str(organization_id))
```

Do not query the container directly inside a route. Keep tenant-scoped query logic in
the shared read helpers, and always pass the partition key.
