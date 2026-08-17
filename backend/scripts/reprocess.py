"""
Re-runs extraction, chunking and embedding for a contract's current version.

Deletes its existing chunks first, so a shorter re-chunk never leaves stale
chunks behind. Useful when a job failed or the chunking logic changed.

Usage:
    python scripts/reprocess.py <contract_id>
"""
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.config import settings  # noqa: E402
from app.data_access.chunks import delete_chunks_for_version  # noqa: E402
from app.data_access.contracts import get_current_version_for_contract  # noqa: E402
from app.services.processing import process_version  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logging.getLogger("azure").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def reprocess(organization_id: str, contract_id: str) -> None:
    version = get_current_version_for_contract(organization_id, contract_id)
    if version is None:
        logger.error("Contract %s has no version to reprocess", contract_id)
        return

    version_id = version["id"]
    deleted = delete_chunks_for_version(organization_id, version_id)
    logger.info("Deleted %d existing chunk(s) for version %s", deleted, version_id)

    logger.info("Reprocessing version %s", version_id)
    process_version(organization_id, version_id)
    logger.info("Done.")


def main() -> None:
    if len(sys.argv) != 2:
        logger.error("Usage: python scripts/reprocess.py <contract_id>")
        sys.exit(1)

    reprocess(str(settings.DEVELOPMENT_ORGANIZATION_ID), sys.argv[1])


if __name__ == "__main__":
    main()
