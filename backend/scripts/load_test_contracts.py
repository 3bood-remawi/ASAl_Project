"""
Load the contract PDF fixtures into Cosmos DB using the existing application
upload and processing pipeline.

Usage:
    python scripts/seed.py
    python scripts/load_test_contracts.py

Safe to run more than once: files already stored with the same SHA-256 hash
are skipped instead of creating duplicate contracts.
"""

import sys
from pathlib import Path
from typing import Any

from fastapi import UploadFile

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.core.config import settings  # noqa: E402
from app.core.cosmos import create_database_and_containers  # noqa: E402
from app.data_access.contracts import get_editor, get_version_by_hash  # noqa: E402
from app.services.processing import process_version  # noqa: E402
from app.services.upload import inspect_upload, store_upload  # noqa: E402

FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures" / "contracts"


def load_contract(path: Path, user: dict[str, Any]) -> bool:
    """
    Store and process one PDF fixture.

    Returns True when a new contract is created and False when a version with
    the same file hash already exists.
    """
    organization_id = user["organizationId"]

    with path.open("rb") as source:
        upload = UploadFile(file=source, filename=path.name)
        file_hash, size = inspect_upload(upload)

        existing_version = get_version_by_hash(
            organization_id,
            file_hash,
        )
        if existing_version is not None:
            print(f"Skipped existing: {path.name}")
            return False

        _, version, _ = store_upload(
            user,
            upload,
            file_hash,
            size,
        )

    # Processing reads the PDF back from storage. A scanned PDF is retained as
    # a failed contract by the existing processing pipeline.
    process_version(organization_id, version.id)
    print(f"Created: {path.name}")
    return True


def load_test_contracts(
    fixtures_dir: Path = FIXTURES_DIR,
) -> tuple[int, int]:
    """
    Load every PDF in the fixture directory.

    Returns the number of newly created and skipped contracts.
    """
    organization_id = str(settings.DEVELOPMENT_ORGANIZATION_ID)
    user = get_editor(organization_id)

    if user is None:
        raise RuntimeError(
            "No Editor exists in Cosmos DB. Run scripts/seed.py first."
        )

    pdf_paths = sorted(fixtures_dir.glob("*.pdf"))
    if not pdf_paths:
        raise RuntimeError(
            f"No PDF fixtures found in {fixtures_dir}."
        )

    created = 0
    skipped = 0

    for path in pdf_paths:
        if load_contract(path, user):
            created += 1
        else:
            skipped += 1

    return created, skipped


def main() -> None:
    create_database_and_containers()

    try:
        created, skipped = load_test_contracts()
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc

    print(
        f"Finished. Created {created} contract(s); "
        f"skipped {skipped} existing contract(s)."
    )


if __name__ == "__main__":
    main()