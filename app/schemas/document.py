from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class BoundingBox(BaseModel):
    x: float
    y: float
    width: float
    height: float

class ExtractedFieldBase(BaseModel):
    field_name: str
    field_value: str
    description: Optional[str] = None
    bounding_box: BoundingBox
    section_name: str
    page_number: int

class ExtractedFieldCreate(ExtractedFieldBase):
    pass

class ExtractedField(BaseModel):
    id: int
    document_id: int
    field_name: str
    field_value: str
    description: Optional[str] = None
    bounding_box_x: float
    bounding_box_y: float
    bounding_box_width: float
    bounding_box_height: float
    section_name: str
    page_number: int

    @property
    def bounding_box(self) -> BoundingBox:
        return BoundingBox(
            x=self.bounding_box_x,
            y=self.bounding_box_y,
            width=self.bounding_box_width,
            height=self.bounding_box_height
        )

    class Config:
        from_attributes = True

class DocumentBase(BaseModel):
    filename: str
    total_pages: int

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: int
    upload_date: datetime
    extracted_fields: List[ExtractedField] = []

    class Config:
        from_attributes = True

class DocumentInDB(Document):
    pass
