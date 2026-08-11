from uuid import UUID

from app.core.config import settings


def current_organization_id() -> UUID:
    return settings.DEVELOPMENT_ORGANIZATION_ID
