import json
import time
import google.generativeai as genai
from PIL import Image

_model = None

def configure_ai(api_key: str):
    """Configures the Gemini API client directly with the requested model."""
    global _model
    genai.configure(api_key=api_key.strip())
    _model = genai.GenerativeModel(
        model_name="gemini-3.6-flash",
        generation_config={"response_mime_type": "application/json"}
    )

def extract_land_record(image: Image.Image) -> dict:
    """Sends document to Gemini with automatic retry for 429 rate limits."""
    if _model is None:
        raise ValueError("Gemini API is not configured. Please supply an API key first.")

    prompt = """
    You are an expert Indian Land Record Digitization AI. Analyze this scanned land record image (e.g., 7/12 extract, Khasra, Khatauni).
    Extract the following fields in valid JSON:
    {
        "landowner_name": "Full name of the primary landowner(s)",
        "survey_khasra_no": "Survey or Gat or Khasra Number",
        "khata_no": "Khata or Account Number",
        "area_hectares": 0.0,
        "village": "Village name",
        "tehsil": "Taluka or Tehsil name",
        "district": "District name",
        "state": "State name",
        "confidence_score": 0.95
    }
    If any field is illegible or missing, provide your best estimation and reduce the confidence_score accordingly.
    """

    max_retries = 3
    delay = 10  # Seconds to wait before retry

    for attempt in range(max_retries):
        try:
            response = _model.generate_content([prompt, image])
            data = json.loads(response.text.strip())

            conf = float(data.get("confidence_score", 0.80))
            data["validation_status"] = "Auto-Validated" if conf >= 0.85 else "Requires Human Review"
            return data

        except Exception as e:
            err_msg = str(e).lower()
            if "429" in err_msg or "quota" in err_msg:
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2
                    continue
                else:
                    raise RuntimeError("API rate limit reached (5 requests/min). Please wait 30 seconds before processing another document.")
            else:
                raise e