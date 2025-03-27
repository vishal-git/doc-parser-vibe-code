from typing import List, Dict, Any
from app.services.pdf_service import PDFService
from app.services.llm_service import LLMService
from app.schemas.document import DocumentCreate, ExtractedFieldCreate
from datetime import datetime
import logging
import traceback

logger = logging.getLogger(__name__)

class ExtractionService:
    def __init__(self):
        self.pdf_service = PDFService()
        self.llm_service = LLMService()

    async def process_document(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Process a PDF document and extract all relevant information."""
        try:
            # Validate PDF
            is_valid, message = self.pdf_service.validate_pdf(file_content)
            if not is_valid:
                logger.error(f"PDF validation failed for {filename}: {message}")
                return {"error": message}

            # Save file temporarily
            file_path = self.pdf_service.save_uploaded_file(file_content, filename)
            logger.info(f"Saved temporary file: {file_path}")
            
            try:
                # Get document metadata
                total_pages = self.pdf_service.get_page_count(file_path)
                logger.info(f"Document {filename} has {total_pages} pages")
                
                # Create document record
                document = DocumentCreate(
                    filename=filename,
                    total_pages=total_pages
                )

                # Extract text from all pages
                page_texts = self.pdf_service.extract_text(file_path)
                logger.info(f"Extracted text from {len(page_texts)} pages")
                
                # Process each page
                extracted_fields = []
                for page_num, text in enumerate(page_texts, 1):
                    logger.info(f"Processing page {page_num} of {filename}")
                    # Extract fields from the page
                    fields = self.llm_service.extract_fields(text, page_num)
                    logger.info(f"Extracted {len(fields)} fields from page {page_num}")
                    
                    # Convert to ExtractedFieldCreate objects
                    for field in fields:
                        extracted_field = ExtractedFieldCreate(
                            field_name=field["field_name"],
                            field_value=field["field_value"],
                            description=field.get("description"),
                            bounding_box=field["bounding_box"],
                            section_name=field["section_name"],
                            page_number=page_num
                        )
                        extracted_fields.append(extracted_field)

                logger.info(f"Total fields extracted from {filename}: {len(extracted_fields)}")

                return {
                    "document": document,
                    "extracted_fields": extracted_fields
                }

            except Exception as e:
                logger.error(f"Error processing document {filename}: {str(e)}")
                logger.error(traceback.format_exc())
                return {"error": f"Error processing document: {str(e)}"}

            finally:
                # Clean up temporary file
                self.pdf_service.cleanup_file(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")

        except Exception as e:
            logger.error(f"Unexpected error processing {filename}: {str(e)}")
            logger.error(traceback.format_exc())
            return {"error": f"Unexpected error: {str(e)}"}

    async def process_multiple_documents(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process multiple PDF documents."""
        results = []
        for file in files:
            result = await self.process_document(file["content"], file["filename"])
            results.append(result)
        return results
