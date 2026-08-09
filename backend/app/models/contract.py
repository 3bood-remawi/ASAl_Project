import uuid

from sqlalchemy import BigInteger, Column, DateTime, Enum, ForeignKey, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import ContractStatus, ProcessingStatus


class Contract(Base):
    __tablename__ = "contract"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(Enum(ContractStatus), nullable=False, default=ContractStatus.UPLOADED)
    created_by = Column(UUID(as_uuid=True), ForeignKey("app_user.id", ondelete="RESTRICT"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    versions = relationship("ContractVersion", back_populates="contract")


class ContractVersion(Base):
    __tablename__ = "contract_version"
    __table_args__ = (
        UniqueConstraint("contract_id", "version_number", name="uq_contract_version_number"),
        Index("ix_contract_version_file_hash", "file_hash"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id", ondelete="CASCADE"), nullable=False)
    contract_id = Column(UUID(as_uuid=True), ForeignKey("contract.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_type = Column(String(50), nullable=True)
    file_size_bytes = Column(BigInteger, nullable=True)
    file_hash = Column(String(255), nullable=True)
    page_count = Column(Integer, nullable=True)
    language = Column(String(10), nullable=False)
    processing_status = Column(Enum(ProcessingStatus), nullable=False, default=ProcessingStatus.PENDING)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("app_user.id", ondelete="RESTRICT"), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    contract = relationship("Contract", back_populates="versions")
