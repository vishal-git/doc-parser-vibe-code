from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import shutil
import os
import logging
import traceback

from app.database.database import get_db, engine
from app.database import models
from app.schemas.document import Document, DocumentCreate, ExtractedField
from app.services.extraction_service import ExtractionService
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
extraction_service = ExtractionService()

@app.post("/api/upload", response_model=List[Document])
async def upload_documents(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process multiple PDF documents."""
    try:
        if len(files) > settings.MAX_DOCUMENTS:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum {settings.MAX_DOCUMENTS} documents allowed per upload"
            )

        processed_files = []
        for file in files:
            try:
                if not file.filename.endswith('.pdf'):
                    raise HTTPException(
                        status_code=400,
                        detail=f"File {file.filename} is not a PDF"
                    )

                # Read file content
                content = await file.read()
                if len(content) > settings.MAX_UPLOAD_SIZE:
                    raise HTTPException(
                        status_code=400,
                        detail=f"File {file.filename} exceeds maximum size of {settings.MAX_UPLOAD_SIZE/1024/1024}MB"
                    )

                logger.info(f"Processing file: {file.filename}")
                
                # Process document
                result = await extraction_service.process_document(content, file.filename)
                if "error" in result:
                    logger.error(f"Error processing document {file.filename}: {result['error']}")
                    raise HTTPException(status_code=400, detail=result["error"])

                # Create document in database
                db_document = models.Document(
                    filename=result["document"].filename,
                    total_pages=result["document"].total_pages
                )
                db.add(db_document)
                db.flush()  # Get the document ID

                # Create extracted fields
                for field in result["extracted_fields"]:
                    db_field = models.ExtractedField(
                        document_id=db_document.id,
                        field_name=field.field_name,
                        field_value=field.field_value,
                        description=field.description,
                        bounding_box_x=field.bounding_box.x,
                        bounding_box_y=field.bounding_box.y,
                        bounding_box_width=field.bounding_box.width,
                        bounding_box_height=field.bounding_box.height,
                        section_name=field.section_name,
                        page_number=field.page_number
                    )
                    db.add(db_field)

                db.commit()
                processed_files.append(db_document)
                logger.info(f"Successfully processed document: {file.filename}")

            except Exception as e:
                logger.error(f"Error processing file {file.filename}: {str(e)}")
                logger.error(traceback.format_exc())
                raise HTTPException(
                    status_code=500,
                    detail=f"Error processing file {file.filename}: {str(e)}"
                )

        return processed_files

    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Upload error: {str(e)}"
        )

@app.get("/api/documents", response_model=List[Document])
def list_documents(db: Session = Depends(get_db)):
    """List all processed documents."""
    return db.query(models.Document).all()

@app.get("/api/documents/{doc_id}", response_model=Document)
def get_document(doc_id: int, db: Session = Depends(get_db)):
    """Get document details by ID."""
    document = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@app.get("/api/documents/{doc_id}/fields", response_model=List[ExtractedField])
def get_document_fields(doc_id: int, db: Session = Depends(get_db)):
    """Get extracted fields for a document."""
    fields = db.query(models.ExtractedField).filter(
        models.ExtractedField.document_id == doc_id
    ).all()
    if not fields:
        raise HTTPException(status_code=404, detail="No fields found for document")
    return fields

@app.get("/api/documents/{doc_id}/pages/{page_number}")
def get_page_details(doc_id: int, page_number: int, db: Session = Depends(get_db)):
    """Get details for a specific page of a document."""
    document = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if page_number < 1 or page_number > document.total_pages:
        raise HTTPException(status_code=400, detail="Invalid page number")
    
    fields = db.query(models.ExtractedField).filter(
        models.ExtractedField.document_id == doc_id,
        models.ExtractedField.page_number == page_number
    ).all()
    
    return {
        "document_id": doc_id,
        "page_number": page_number,
        "fields": fields
    }
