import streamlit as st
import requests
import json
from typing import List, Dict, Any
import os
from PIL import Image
import io
import base64
from pdf2image import convert_from_bytes
import tempfile

# API Configuration
API_URL = "http://localhost:8000/api"

# Configure Streamlit page
st.set_page_config(
    layout="wide",
    page_title="Document Parser",
    page_icon="📄",
    initial_sidebar_state="expanded"
)

def upload_documents(files: List[Any]) -> List[Dict[str, Any]]:
    """Upload documents to the API."""
    files_data = []
    for file in files:
        files_data.append(
            ("files", (file.name, file.getvalue(), "application/pdf"))
        )
    
    response = requests.post(f"{API_URL}/upload", files=files_data)
    if response.status_code != 200:
        st.error(f"Error uploading documents: {response.text}")
        return []
    return response.json()

def get_document_fields(doc_id: int) -> List[Dict[str, Any]]:
    """Get extracted fields for a document."""
    response = requests.get(f"{API_URL}/documents/{doc_id}/fields")
    if response.status_code != 200:
        st.error(f"Error getting document fields: {response.text}")
        return []
    return response.json()

def get_page_details(doc_id: int, page_number: int) -> Dict[str, Any]:
    """Get details for a specific page."""
    response = requests.get(f"{API_URL}/documents/{doc_id}/pages/{page_number}")
    if response.status_code != 200:
        st.error(f"Error getting page details: {response.text}")
        return {}
    return response.json()

def display_pdf_page(pdf_bytes: bytes, page_number: int, total_pages: int) -> None:
    """Display a PDF page with bounding boxes."""
    # Convert PDF page to image
    images = convert_from_bytes(pdf_bytes, first_page=page_number, last_page=page_number)
    if not images:
        st.error("Could not convert PDF page to image")
        return
    
    # Display the image
    st.image(images[0], use_container_width=True)
    
    # Add page navigation controls
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if page_number > 1:
            if st.button("Previous Page"):
                st.session_state.current_page = page_number - 1
    with col2:
        st.write(f"Page {page_number} of {total_pages}")
    with col3:
        if page_number < total_pages:
            if st.button("Next Page"):
                st.session_state.current_page = page_number + 1

def main():
    # Initialize session state for page navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1

    # Custom CSS for better layout and dark theme support
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stButton>button {
            width: 100%;
            margin-top: 1rem;
        }
        .stExpander {
            background-color: var(--background-color);
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        .stTable {
            font-size: 0.9rem;
            background-color: var(--background-color);
        }
        .stTable th {
            background-color: var(--secondary-background-color);
            color: var(--text-color);
        }
        .stTable td {
            background-color: var(--background-color);
            color: var(--text-color);
        }
        .stTable tr:hover {
            background-color: var(--secondary-background-color);
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("Document Parser")
    st.write("Upload PDF documents to extract and analyze their contents.")

    # File upload
    uploaded_files = st.file_uploader(
        "Upload PDF documents",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:
        if len(uploaded_files) > 5:
            st.error("Maximum 5 documents allowed per upload")
            return

        if st.button("Process Documents"):
            with st.spinner("Processing documents..."):
                # Upload documents
                documents = upload_documents(uploaded_files)
                
                if documents:
                    st.success(f"Successfully processed {len(documents)} documents")
                    
                    # Create tabs for each document
                    for doc in documents:
                        with st.expander(f"Document: {doc['filename']}", expanded=True):
                            # Get document fields
                            fields = get_document_fields(doc['id'])
                            
                            # Create two columns with better proportions (2:3 ratio)
                            col1, col2 = st.columns([2, 3])
                            
                            with col1:
                                st.subheader("Document Viewer")
                                # Display PDF page with bounding boxes
                                display_pdf_page(uploaded_files[0].getvalue(), st.session_state.current_page, doc['total_pages'])
                            
                            with col2:
                                st.subheader("Extracted Fields")
                                # Display fields in a table with better formatting
                                if fields:
                                    field_data = []
                                    for field in fields:
                                        field_data.append({
                                            "Field": field['field_name'],
                                            "Value": field['field_value'],
                                            "Section": field['section_name'],
                                            "Page": field['page_number']
                                        })
                                    st.table(field_data)
                                else:
                                    st.info("No fields extracted from this document")

if __name__ == "__main__":
    main()
