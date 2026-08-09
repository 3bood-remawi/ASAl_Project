"""
Seed script creates a demo organization, one Editor, and one Approver.

Usage:
    python scripts/seed.py

Safe to run multiple times: it checks for the demo organization by name
before inserting, so it won't create duplicates on repeat runs.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy.orm import Session

from app.core.database import engine
from app.models.app_user import AppUser
from app.models.enums import UserRole
from app.models.organization import Organization

DEMO_ORG_NAME = "Demo Organization"


def seed() -> None:
    with Session(engine) as session:
        org = (
            session.query(Organization)
            .filter(Organization.name == DEMO_ORG_NAME)
            .first()
        )
        if org is None:
            org = Organization(name=DEMO_ORG_NAME)
            session.add(org)
            session.flush()  # get org.id before creating users
            print(f"Created organization: {org.name} ({org.id})")
        else:
            print(f"Organization already exists: {org.name} ({org.id})")

        editor = (
            session.query(AppUser)
            .filter(AppUser.email == "editor@demo.local")
            .first()
        )
        if editor is None:
            editor = AppUser(
                organization_id=org.id,
                external_id="demo-editor",
                email="editor@demo.local",
                full_name="Demo Editor",
                role=UserRole.EDITOR.value,
                is_active=True,
            )
            session.add(editor)
            print("Created demo Editor user")
        else:
            print("Demo Editor user already exists")

        approver = (
            session.query(AppUser)
            .filter(AppUser.email == "approver@demo.local")
            .first()
        )
        if approver is None:
            approver = AppUser(
                organization_id=org.id,
                external_id="demo-approver",
                email="approver@demo.local",
                full_name="Demo Approver",
                role=UserRole.APPROVER.value,
                is_active=True,
            )
            session.add(approver)
            print("Created demo Approver user")
        else:
            print("Demo Approver user already exists")

        session.commit()
        print("Seed complete.")


if __name__ == "__main__":
    seed()