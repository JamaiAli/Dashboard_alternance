import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class Note(Base):
    __tablename__ = "notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False) # Markdown format
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    application = relationship("Application", back_populates="notes")
