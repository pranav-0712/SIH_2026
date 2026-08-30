from google import genai
from PIL import Image
import json
import re

def extract_land_record(image: Image.Image, api_key: str) -> dict:
    """
    Extracts structured land registry records using Gemini 3.6 Flash
    capturing all joint landowners and co-occupants.
    """
    client = genai.Client(api_key=api_key.strip())
    
    prompt = """
    You are an expert OCR and Land Records Digitization AI system for India (DILRMP).
    Analyze this land document image (e.g., 7/12 extract, Khasra, Khatauni, RoR, Patta).
    The document may contain text in English, Hindi, Marathi, or other Indian scripts.
    
    Extract the key details and return ONLY a strict, valid JSON object with these exact keys:
    {
        "landowner_name": "Comma-separated list of ALL joint owners/occupants",
        "survey_khasra_no": "Survey or Khasra/Gat Number (e.g., 248/3B)",
        "khata_no": "Khata/Account Number",
        "area_hectares": 0.0,
        "village": "Village name",
        "tehsil": "Tehsil / Taluka name",
        "district": "District name",
        "state": "State name",
        "confidence_score": 0.95
    }
    
    Extraction Guidelines:
    - landowner_name MUST include ALL co-owners/joint landowners listed in the document separated by commas (e.g. "Rameshwar Balasaheb Patil, Sunita Rameshwar Patil"). Do NOT omit joint holders.
    - area_hectares MUST be a numeric float (convert Guntha, Bigha, Are, or Acres to Hectares if specified, e.g. 2 Hectares 25 Are = 2.2500).
    - confidence_score MUST be a float between 0.0 and 1.0 reflecting visual text clarity.
    - If any field is faded, torn, handwritten, or ambiguous, assign confidence_score below 0.80.
    - Output pure JSON only. Do not include markdown fences, greetings, or conversational text.
    """
    
    models_to_try = [
        "gemini-3.6-flash",
    ]
    
    response = None
    model_used = "gemini-3.6-flash"
    last_exception = None
    
    for m in models_to_try:
        try:
            response = client.models.generate_content(
                model=m,
                contents=[prompt, image]
            )
            model_used = m
            break
        except Exception as e:
            last_exception = e
            continue
            
    if not response:
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
            "model_used": "None",
            "error_message": str(last_exception)
        }
        
    try:
        clean_text = response.text.strip()
        clean_text = re.sub(r"^```json\s*", "", clean_text)
        clean_text = re.sub(r"^```\s*", "", clean_text)
        clean_text = re.sub(r"\s*```$", "", clean_text)
        
        data = json.loads(clean_text)
        data["model_used"] = model_used
        
        # Rule-based validation checks
        conf = float(data.get("confidence_score", 0.70))
        area = float(data.get("area_hectares", 0.0))
        khasra = str(data.get("survey_khasra_no", "")).strip()
        
        if conf >= 0.85 and area > 0 and len(khasra) > 0 and khasra != "N/A":
            data["validation_status"] = "Auto-Validated"
        else:
            data["validation_status"] = "Requires Human Review"
            
        return data

    except Exception as e:
        return {
            "landowner_name": "Unreadable / Parse Error",
            "survey_khasra_no": "N/A",
            "khata_no": "N/A",
            "area_hectares": 0.0,
            "village": "N/A",
            "tehsil": "N/A",
            "district": "N/A",
            "state": "N/A",
            "confidence_score": 0.0,
            "validation_status": "Processing Failed",
            "model_used": model_used,
            "error_message": f"JSON decode failed: {str(e)}"
        }