from typing import List, Dict, Any
import json
from openai import OpenAI
from app.config import settings

class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4-turbo-preview"

    def extract_fields(self, text: str, page_number: int) -> List[Dict[str, Any]]:
        """Extract fields from text using OpenAI's LLM."""
        prompt = f"""
        You are a document analysis expert. Analyze the following text from page {page_number} of a document and extract key-value pairs.
        Focus on common fields in documents like:
        - Dates
        - Amounts (with currency symbols)
        - Names
        - Account numbers
        - Reference numbers
        - Addresses
        - Phone numbers
        - Email addresses
        - Status indicators
        - Section headers
        - Total amounts
        - Due dates
        - Service periods

        For each field you find, provide:
        1. A clear, concise field name (e.g., "total_amount", "due_date", "account_number")
        2. The exact value as it appears in the document
        3. A brief description of what the field represents
        4. The section name where this field appears (e.g., "header", "billing_summary", "call_details")
        5. The approximate bounding box coordinates where this field appears in the document (x, y, width, height)

        Text to analyze:
        {text}

        Return the results as a JSON object with a "fields" array containing objects with this structure:
        {{
            "fields": [
                {{
                    "field_name": "string",
                    "field_value": "string",
                    "description": "string",
                    "section_name": "string",
                    "bounding_box": {{
                        "x": float,
                        "y": float,
                        "width": float,
                        "height": float
                    }}
                }}
            ]
        }}

        Important:
        - Extract ALL fields you can find, even if they seem obvious
        - Use consistent field names (lowercase, underscores)
        - Include currency symbols with amounts
        - Preserve exact formatting of values
        - Make bounding box coordinates reasonable (0-1000 range)
        - Identify clear section boundaries
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a document analysis expert. Extract key-value pairs from documents and provide their locations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            if not result.get("fields"):
                print(f"No fields extracted from page {page_number}")
                print(f"Raw text: {text[:200]}...")  # Print first 200 chars for debugging
            return result.get("fields", [])
            
        except Exception as e:
            print(f"Error in LLM extraction: {str(e)}")
            return []

    def identify_sections(self, text: str) -> List[Dict[str, Any]]:
        """Identify document sections using OpenAI's LLM."""
        prompt = f"""
        Analyze the following text and identify distinct sections.
        Look for:
        - Headers and subheaders
        - Billing summaries
        - Call detail records
        - Payment information
        - Account information
        - Terms and conditions
        - Footer information

        For each section, provide:
        1. A clear section name
        2. The starting line number
        3. The ending line number
        4. A brief description of the section's content

        Text to analyze:
        {text}

        Return the results as a JSON object with a "sections" array containing objects with this structure:
        {{
            "sections": [
                {{
                    "section_name": "string",
                    "start_line": integer,
                    "end_line": integer,
                    "description": "string"
                }}
            ]
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a document analysis expert. Identify distinct sections in documents."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("sections", [])
            
        except Exception as e:
            print(f"Error in section identification: {str(e)}")
            return []
