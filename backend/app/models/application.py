import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class ApplicationStatus(str, enum.Enum):
    WISHLIST = "Wishlist"
    APPLIED = "Applied"
    INTERVIEW = "Interview"
    TECHNICAL_TEST = "Technical Test"
    REJECTED = "Rejected"
    OFFER = "Offer"

class ApplicationType(str, enum.Enum):
    ALTERNANCE = "Alternance"
    STAGE = "Stage"

class Application(Base):
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    date_sent = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=True)
    last_contact_date = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    status = Column(Enum(ApplicationStatus, native_enum=False), default=ApplicationStatus.WISHLIST)
    salary_proposed = Column(Float, nullable=True)
    type = Column(Enum(ApplicationType, native_enum=False), default=ApplicationType.ALTERNANCE)
    job_url = Column(String, nullable=True)
    raw_description = Column(Text, nullable=True)

    company = relationship("Company", back_populates="applications")
    documents = relationship("Document", back_populates="application", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="application", cascade="all, delete-orphan")
