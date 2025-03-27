from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    total_pages = Column(Integer)
    
    extracted_fields = relationship("ExtractedField", back_populates="document")

class ExtractedField(Base):
    __tablename__ = "extracted_fields"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    field_name = Column(String)
    field_value = Column(String)
    description = Column(String, nullable=True)
    bounding_box_x = Column(Float)
    bounding_box_y = Column(Float)
    bounding_box_width = Column(Float)
    bounding_box_height = Column(Float)
    section_name = Column(String)
    page_number = Column(Integer)

    document = relationship("Document", back_populates="extracted_fields")
