import google.generativeai as genai
from PIL import Image
import json
import re

def configure_ai(api_key: str):
    """Configures the Gemini client with the API key."""
    genai.configure(api_key=api_key.strip())

def extract_land_record(image: Image.Image) -> dict:
    """
    Extracts structured fields from scanned land records (7/12, Khasra, RoR)
    using Gemini Vision and performs validation.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = """
    You are an expert OCR and Land Records Digitization AI system for India (DILRMP).
    Analyze this land document image (e.g., 7/12 extract, Khasra, Khatauni, RoR, Patta).
    The document may contain text in English, Hindi, Marathi, or other Indian scripts.
    
    Extract the key details and return ONLY a strict, valid JSON object with these exact keys:
    {
        "landowner_name": "Full name of primary owner/occupant",
        "survey_khasra_no": "Survey or Khasra/Gat Number (e.g., 142/2A)",
        "khata_no": "Khata/Account Number",
        "area_hectares": 0.0,
        "village": "Village name",
        "tehsil": "Tehsil / Taluka name",
        "district": "District name",
        "state": "State name",
        "confidence_score": 0.95
    }
    
    Extraction Guidelines:
    - area_hectares MUST be a numeric float.
    - confidence_score MUST be a float between 0.0 and 1.0 reflecting text clarity.
    - If any field is faded, torn, or unreadable, lower the confidence_score below 0.80.
    - Output pure JSON only. Do not include markdown code fences or conversational text.
    """
    
    try:
        response = model.generate_content([prompt, image])
        clean_text = response.text.strip()
        
        # Clean markdown code blocks if present
        clean_text = re.sub(r"^```json\s*", "", clean_text)
        clean_text = re.sub(r"^```\s*", "", clean_text)
        clean_text = re.sub(r"\s*```$", "", clean_text)
        
        data = json.loads(clean_text)
        
        # Automated Rule Validation
        conf = float(data.get("confidence_score", 0.70))
        area = float(data.get("area_hectares", 0.0))
        khasra = str(data.get("survey_khasra_no", "")).strip()
        
        if conf >= 0.85 and area > 0 and len(khasra) > 0 and khasra != "N/A":
            data["validation_status"] = "Auto-Validated"
        else:
            data["validation_status"] = "Requires Human Review"
            
        return data

    except Exception as e:
        print(f"❌ AI Extraction Error: {str(e)}")
        return {
            "landowner_name": "Unreadable / Error",
            "survey_khasra_no": "N/A",
            "khata_no": "N/A",
            "area_hectares": 0.0,
            "village": "N/A",
            "tehsil": "N/A",
            "district": "N/A",
            "state": "N/A",
            "confidence_score": 0.0,
            "validation_status": "Processing Failed",
            "error_message": str(e)
        }