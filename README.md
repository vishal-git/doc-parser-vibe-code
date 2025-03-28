This entire codebase is developed by 100% vibe coding using Cursor AI. It took me less than a couple of hours to do this from start to finish. The entire chat history is available in [cursorai_chat_history.pdf](./cursorai_chat_history.pdf).

# Document Parser Application

A powerful document parsing application that allows users to upload PDF documents, extract text, identify sections, and extract key-value pairs using OpenAI's API. The application features a document viewer and displays extracted fields with bounding boxes.

## Features

- Upload multiple PDF documents (up to 5 at a time)
- Extract text and identify sections from PDFs
- Extract key-value pairs using OpenAI's API
- Display PDF documents with bounding boxes
- Show extracted fields in a table format
- Modern UI with Streamlit
- FastAPI backend for efficient processing

## Project Structure

```
doc-parser/
├── app/
│   ├── main.py              # FastAPI application
│   ├── database/
│   │   ├── models.py        # Database models
│   │   └── database.py      # Database configuration
│   ├── services/
│   │   ├── pdf_service.py   # PDF processing service
│   │   ├── llm_service.py   # OpenAI API service
│   │   └── extraction_service.py  # Field extraction service
│   └── schemas/
│       └── document.py      # Pydantic schemas
├── frontend/
│   └── streamlit_app.py     # Streamlit frontend
├── requirements.txt         # Python dependencies
└── README.md               # Project documentation
```

## Prerequisites

- Python 3.8+
- Poppler (for PDF processing)
- OpenAI API key

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd doc-parser
   ```

2. Install Poppler:
   - On Ubuntu/Debian:
     ```bash
     sudo apt-get install poppler-utils
     ```
   - On macOS:
     ```bash
     brew install poppler
     ```
   - On Windows:
     Download and install from: http://blog.alivate.com.au/poppler-windows/

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

## Running the Application

1. Start the FastAPI backend:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Start the Streamlit frontend:
   ```bash
   streamlit run frontend/streamlit_app.py
   ```

3. Open your browser and navigate to:
   - Frontend: http://localhost:8501
   - API Documentation: http://localhost:8000/docs

## Usage

1. Upload PDF documents through the Streamlit interface
2. Click "Process Documents" to start extraction
3. View the extracted fields and their locations in the document
4. Navigate through pages using the page controls

## API Endpoints

- `POST /api/upload`: Upload PDF documents
- `GET /api/documents`: List all documents
- `GET /api/documents/{doc_id}`: Get document details
- `GET /api/documents/{doc_id}/fields`: Get extracted fields
- `GET /api/documents/{doc_id}/pages/{page_number}`: Get page details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
