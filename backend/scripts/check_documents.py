"""
Builds one of every document and prints the fields it would write to Cosmos.

Runs in CI without a database. It catches a shape that no longer builds, a field
that lost its camelCase name, and a document missing the partition key.

Usage:
    python scripts/check_documents.py
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.documents.shapes import (  # noqa: E402
    CHUNKS_CONTAINER,
    CONTRACTS_CONTAINER,
    PARTITION_KEY_PATH,
    ChunkDocument,
    ContractDocument,
    Document,
    JobDocument,
    OrganizationDocument,
    UserDocument,
    VersionDocument,
)

ORG = "00000000-0000-0000-0000-000000000001"

SAMPLES = {
    CONTRACTS_CONTAINER: [
        OrganizationDocument(id=ORG, organization_id=ORG, name="Demo Organization"),
        UserDocument(id="demo-editor", organization_id=ORG, external_id="demo-editor",
                     email="editor@demo.local", full_name="Demo Editor", role="editor"),
        ContractDocument(id="contract-1", organization_id=ORG, name="Nexa Services Agreement",
                         created_by="demo-editor"),
        VersionDocument(id="version-1", organization_id=ORG, contract_id="contract-1",
                        file_name="agreement.pdf", file_path=f"{ORG}/contract-1/version-1/agreement.pdf",
                        uploaded_by="demo-editor"),
        JobDocument(id="job-1", organization_id=ORG, version_id="version-1"),
    ],
    CHUNKS_CONTAINER: [
        ChunkDocument(id="chunk-1", organization_id=ORG, version_id="version-1",
                      chunk_order=0, text="Either party may end the agreement."),
    ],
}

partition_field = PARTITION_KEY_PATH.lstrip("/")
problems = []

for container, documents in SAMPLES.items():
    print(f"\n{container}  (partition key {PARTITION_KEY_PATH})")
    for document in documents:
        item = document.to_item()
        print(f"  - {item['type']:13} {len(item):2} fields: {', '.join(item)}")

        if partition_field not in item:
            problems.append(f"{item['type']} has no {partition_field}")
        if not item.get("id"):
            problems.append(f"{item['type']} has no id")
        underscored = [k for k in item if "_" in k]
        if underscored:
            problems.append(f"{item['type']} is not camelCase: {underscored}")

shapes = [c.__name__ for c in Document.__subclasses__()]
covered = {type(d).__name__ for docs in SAMPLES.values() for d in docs}
missing = set(shapes) - covered
if missing:
    problems.append(f"shapes with no sample here: {sorted(missing)}")

if problems:
    print("\nPROBLEMS:")
    for problem in problems:
        print(f"  - {problem}")
    sys.exit(1)

print(f"\nAll {len(shapes)} document shapes are valid.")
