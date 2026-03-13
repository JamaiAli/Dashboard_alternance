import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True, nullable=False)
    sector = Column(String, nullable=True)
    tech_stack = Column(ARRAY(String), nullable=True)
    glassdoor_link = Column(String, nullable=True)
    linkedin_link = Column(String, nullable=True)

    applications = relationship("Application", back_populates="company", cascade="all, delete-orphan")
