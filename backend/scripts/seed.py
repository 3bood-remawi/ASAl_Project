"""
Seed script creates a demo organization, one Editor, and one Approver as documents.

Usage:
    python scripts/seed.py

Safe to run more than once: every document has a fixed id, so a repeat run
replaces it rather than creating a second copy.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.config import settings  # noqa: E402
from app.core.cosmos import create_database_and_containers, get_contracts_container  # noqa: E402
from app.documents.enums import UserRole  # noqa: E402
from app.documents.shapes import OrganizationDocument, UserDocument  # noqa: E402

DEMO_ORG_NAME = "Demo Organization"


def seed() -> None:
    create_database_and_containers()
    container = get_contracts_container()
    organization_id = str(settings.DEVELOPMENT_ORGANIZATION_ID)

    organization = OrganizationDocument(
        id=organization_id,
        organization_id=organization_id,
        name=DEMO_ORG_NAME,
    )
    container.upsert_item(organization.to_item())
    print(f"Organization: {organization.name} ({organization.id})")

    people = [
        ("demo-editor", "editor@demo.local", "Demo Editor", UserRole.EDITOR),
        ("demo-approver", "approver@demo.local", "Demo Approver", UserRole.APPROVER),
    ]
    for external_id, email, full_name, role in people:
        user = UserDocument(
            id=external_id,
            organization_id=organization_id,
            external_id=external_id,
            email=email,
            full_name=full_name,
            role=role,
        )
        container.upsert_item(user.to_item())
        print(f"User: {user.email} ({user.role.value})")

    print("Seed complete.")


if __name__ == "__main__":
    seed()
