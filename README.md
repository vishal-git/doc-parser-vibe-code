# Document Parser Application

A powerful document parsing application that automatically extracts text, identifies sections, and extracts key-value pairs from PDF documents using OpenAI's LLM capabilities.

## Features

- Upload and process multiple PDF documents (up to 5 documents per run)
- Automatic text extraction from PDF documents
- Section identification (e.g., summary, call detail records)
- Key-value pair extraction using OpenAI's LLM
- Interactive document viewer with page navigation
- Visual display of extracted fields and values
- Bounding box visualization for extracted fields
- Section break indicators
- Document-by-document navigation
- Local database storage for extracted information
- Type validation using Pydantic models

## Project Structure

```
doc-parser/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py        # SQLAlchemy database models
│   │   └── database.py      # Database connection and operations
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── document.py      # Pydantic models for document data
│   │   └── field.py         # Pydantic models for extracted fields
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pdf_service.py   # PDF processing functions
│   │   ├── llm_service.py   # OpenAI API integration
│   │   └── extraction_service.py  # Key-value extraction logic
│   └── utils/
│       ├── __init__.py
│       └── helpers.py       # Utility functions
├── frontend/
│   ├── __init__.py
│   └── streamlit_app.py     # Streamlit frontend application
├── requirements.txt         # Project dependencies
└── README.md               # This file
```

## Dependencies

- Python 3.8+
- FastAPI
- Streamlit
- PyPDF2
- OpenAI
- SQLAlchemy
- Pydantic
- pdf2image
- Pillow
- python-multipart
- uvicorn

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd doc-parser
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install uv (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

4. Install dependencies using uv:
```bash
uv pip install -r requirements.txt
```

5. Set up environment variables:
Create a `.env` file in the root directory with:
```
OPENAI_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./doc_parser.db
```

## Usage

1. Start the FastAPI backend:
```bash
uvicorn app.main:app --reload
```

2. Start the Streamlit frontend:
```bash
streamlit run frontend/streamlit_app.py
```

3. Open your browser and navigate to `http://localhost:8501`

## Application Flow

1. User uploads up to 5 PDF documents through the Streamlit interface
2. Backend processes each document:
   - Extracts text using PyPDF2
   - Identifies document sections
   - Sends text to OpenAI LLM for key-value extraction
   - Stores results in local database
3. Frontend displays:
   - PDF viewer with page navigation
   - Extracted fields and values
   - Bounding boxes for fields
   - Section break indicators

## Data Models

### Pydantic Models

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class BoundingBox(BaseModel):
    x: float
    y: float
    width: float
    height: float

class ExtractedField(BaseModel):
    field_name: str
    field_value: str
    description: Optional[str] = None
    bounding_box: BoundingBox
    section_name: str
    page_number: int

class Document(BaseModel):
    id: Optional[int] = None
    filename: str
    upload_date: datetime
    total_pages: int
    extracted_fields: List[ExtractedField] = []
```

### Database Schema

The application uses SQLAlchemy with the following main tables:

- Documents
  - id (Primary Key)
  - filename
  - upload_date
  - total_pages

- ExtractedFields
  - id (Primary Key)
  - document_id (Foreign Key)
  - page_number
  - field_name
  - field_value
  - description
  - bounding_box_coordinates
  - section_name

## API Endpoints

- POST `/api/upload`: Upload PDF documents
- GET `/api/documents`: List all processed documents
- GET `/api/documents/{doc_id}`: Get document details
- GET `/api/documents/{doc_id}/fields`: Get extracted fields for a document
- GET `/api/documents/{doc_id}/pages/{page_number}`: Get page details

## Contributing

This is a personal project and is not currently accepting contributions.

## License

MIT License
