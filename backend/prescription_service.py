"""
Prescription Upload Service
Handles file upload, Gemini extraction, and database storage
"""

import os
import hashlib
import google.generativeai as genai
from typing import Dict, Any, List, Optional
from fastapi import UploadFile
from PIL import Image
import io
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Allowed file types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Gemini extraction prompt
EXTRACTION_PROMPT = """
You are a medical prescription data extraction assistant. Extract ONLY the following information from this prescription image:

1. Doctor Name (full name as written)
2. Doctor ID (registration/license number if present, otherwise null)
3. Medications with their intake slots

CRITICAL RULES:
- ONLY extract explicitly written information
- DO NOT infer, guess, or add any information
- If doctor ID is not visible, return null
- For medications, ONLY extract the drug name and timing slots mentioned
- Slots MUST be one of: "morning", "afternoon", "night" (lowercase)
- If timing is unclear, do NOT include that slot
- Return ONLY valid JSON, no other text

Expected JSON format:
{
  "doctor_name": "Dr. [Full Name]",
  "doctor_id_external": "[ID number or null]",
  "drugs": [
    {
      "drug_name": "[Exact drug name]",
      "slots": ["morning", "afternoon", "night"]
    }
  ]
}

Extract now:
"""


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def calculate_file_hash(file_content: bytes) -> str:
    """Calculate SHA-256 hash of file content"""
    return hashlib.sha256(file_content).hexdigest()


async def validate_upload_file(file: UploadFile) -> tuple[bool, str]:
    """
    Validate uploaded file
    Returns: (is_valid, error_message)
    """
    # Check file extension
    if not allowed_file(file.filename):
        return False, f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Read file content
    content = await file.read()
    await file.seek(0)  # Reset file pointer
    
    # Check file size
    if len(content) > MAX_FILE_SIZE:
        return False, f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
    
    # Verify it's actually an image (for png/jpg)
    if file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        try:
            Image.open(io.BytesIO(content))
        except Exception:
            return False, "Invalid image file"
    
    return True, ""


async def extract_prescription_data(file: UploadFile) -> Dict[str, Any]:
    """
    Extract prescription data using Gemini Vision API
    
    Returns:
        Dict with doctor_name, doctor_id_external, and list of drugs with slots
    """
    if not GEMINI_API_KEY:
        # Mock response for testing without Gemini
        return {
            "doctor_name": "Dr. Mock Doctor",
            "doctor_id_external": "MOCK123",
            "drugs": [
                {"drug_name": "Paracetamol 500mg", "slots": ["morning", "night"]},
                {"drug_name": "Vitamin D3", "slots": ["morning"]}
            ]
        }
    
    try:
        # Read file content
        content = await file.read()
        await file.seek(0)
        
        # For images, use Gemini Vision
        if file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Load image
            image = Image.open(io.BytesIO(content))
            
            # Use Gemini Pro Vision
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Generate content with image
            response = model.generate_content([EXTRACTION_PROMPT, image])
            
            # Parse JSON response
            import json
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            extracted_data = json.loads(response_text.strip())
            
            return extracted_data
        
        else:
            # For PDFs, would need different handling (future enhancement)
            raise ValueError("PDF extraction not yet implemented")
    
    except Exception as e:
        print(f"Gemini extraction error: {e}")
        raise Exception(f"Failed to extract data from prescription: {str(e)}")


def normalize_drug_name(name: str) -> str:
    """Normalize drug name for database storage"""
    return name.strip().title()


def validate_slot(slot: str) -> bool:
    """Validate medication slot"""
    return slot.lower() in ['morning', 'afternoon', 'night']


def normalize_extracted_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize and validate extracted data
    """
    normalized = {
        "doctor_name": data.get("doctor_name", "").strip(),
        "doctor_id_external": data.get("doctor_id_external"),
        "drugs": []
    }
    
    # Validate doctor name
    if not normalized["doctor_name"]:
        raise ValueError("Doctor name is required")
    
    # Normalize drugs
    for drug in data.get("drugs", []):
        drug_name = normalize_drug_name(drug.get("drug_name", ""))
        if not drug_name:
            continue
        
        # Validate and normalize slots
        valid_slots = [
            slot.lower() for slot in drug.get("slots", [])
            if validate_slot(slot)
        ]
        
        if valid_slots:
            normalized["drugs"].append({
                "drug_name": drug_name,
                "slots": list(set(valid_slots))  # Remove duplicates
            })
    
    if not normalized["drugs"]:
        raise ValueError("No valid medications found in prescription")
    
    return normalized
