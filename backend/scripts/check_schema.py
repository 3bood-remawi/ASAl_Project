"""Check that every SQLAlchemy model renders as valid PostgreSQL DDL.

Run by CI. No database needed - this compiles the metadata against the Postgres
dialect and fails if any column type cannot be rendered.

This exists because it is easy to write a model that imports fine and only blows
up later at migration time. Catching it here takes a second instead of a rebuild.
"""

import sys
from pathlib import Path

# Allow running as `python scripts/check_schema.py` from the backend directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.dialects import postgresql  # noqa: E402
from sqlalchemy.schema import CreateIndex, CreateTable  # noqa: E402

from app import models  # noqa: F401,E402 - registers every model with Base
from app.core.database import Base  # noqa: E402


def main() -> int:
    dialect = postgresql.dialect()
    tables = Base.metadata.sorted_tables

    if not tables:
        print("ERROR: no tables registered. Is something missing from app/models/__init__.py?")
        return 1

    failures = []
    for table in tables:
        try:
            CreateTable(table).compile(dialect=dialect)
            for index in table.indexes:
                CreateIndex(index).compile(dialect=dialect)
        except Exception as exc:
            failures.append((table.name, exc))

    for name, exc in failures:
        print(f"FAIL {name}: {type(exc).__name__}: {exc}")

    if failures:
        print(f"\n{len(failures)} table(s) will not build on PostgreSQL.")
        return 1

    print(f"OK: {len(tables)} tables render as valid PostgreSQL DDL")
    for table in tables:
        cols = len(table.columns)
        idx = len(table.indexes)
        print(f"  - {table.name} ({cols} columns, {idx} indexes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
