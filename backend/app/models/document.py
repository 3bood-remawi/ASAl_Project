import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.core.database import Base
from app.models.constants import EMBEDDING_DIM


class DocumentChunk(Base):
    __tablename__ = "document_chunk"
    __table_args__ = (
        UniqueConstraint("version_id", "chunk_order", name="uq_document_chunk_order"),
        Index("ix_chunk_version", "version_id", "chunk_order"),
        Index("ix_chunk_vector", "embedding",
              postgresql_using="hnsw",
              postgresql_ops={"embedding": "vector_cosine_ops"}),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id", ondelete="CASCADE"), nullable=False)
    version_id = Column(UUID(as_uuid=True), ForeignKey("contract_version.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer, nullable=True)
    chunk_order = Column(Integer, nullable=False)
    bounding_boxes = Column(JSONB, nullable=False, server_default="[]")
    char_start = Column(Integer, nullable=True)
    char_end = Column(Integer, nullable=True)
    text = Column(Text, nullable=False)
    language = Column(String(10), nullable=True)
    heading_path = Column(String(500), nullable=True)
    token_count = Column(Integer, nullable=True)
    embedding = Column(Vector(EMBEDDING_DIM), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
