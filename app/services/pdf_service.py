import os
from typing import List, Tuple, Dict
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
from PIL import Image
import io
from app.config import settings

class PDFService:
    @staticmethod
    def extract_text(pdf_path: str) -> List[str]:
        """Extract text from each page of the PDF."""
        reader = PdfReader(pdf_path)
        texts = []
        for page in reader.pages:
            # Extract text and clean it
            text = page.extract_text()
            # Remove multiple spaces and newlines
            text = ' '.join(text.split())
            # Add some spacing between sections
            text = text.replace('. ', '.\n')
            texts.append(text)
        return texts

    @staticmethod
    def get_page_count(pdf_path: str) -> int:
        """Get the total number of pages in the PDF."""
        reader = PdfReader(pdf_path)
        return len(reader.pages)

    @staticmethod
    def convert_to_images(pdf_path: str) -> List[Image.Image]:
        """Convert PDF pages to images."""
        return convert_from_path(pdf_path)

    @staticmethod
    def save_uploaded_file(file_content: bytes, filename: str) -> str:
        """Save uploaded PDF file to disk."""
        # Create upload directory if it doesn't exist
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(file_content)
        return file_path

    @staticmethod
    def cleanup_file(file_path: str) -> None:
        """Remove temporary file after processing."""
        if os.path.exists(file_path):
            os.remove(file_path)

    @staticmethod
    def validate_pdf(file_content: bytes) -> Tuple[bool, str]:
        """Validate PDF file content."""
        try:
            # Try to read the PDF
            pdf_stream = io.BytesIO(file_content)
            reader = PdfReader(pdf_stream)
            
            # Check if PDF is empty
            if len(reader.pages) == 0:
                return False, "PDF file is empty"
            
            # Check if PDF is encrypted
            if reader.is_encrypted:
                return False, "PDF file is encrypted"
            
            # Try to extract text from first page to verify it's readable
            first_page = reader.pages[0]
            text = first_page.extract_text()
            if not text.strip():
                return False, "PDF file appears to be unreadable or contains no text"
            
            return True, "PDF file is valid"
        except Exception as e:
            return False, f"Invalid PDF file: {str(e)}"
