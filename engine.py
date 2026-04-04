import os
import re
import requests
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

import fitz  # PyMuPDF
from PIL import Image
import pytesseract

def extract_text_from_file(file):

    filename = file.filename.lower()

    # 📄 PDF
    if filename.endswith(".pdf"):
        text = ""
        pdf = fitz.open(stream=file.read(), filetype="pdf")
        for page in pdf:
            text += page.get_text()
        return text

    # 🖼️ Image
    elif filename.endswith((".png", ".jpg", ".jpeg")):
        image = Image.open(file)
        text = pytesseract.image_to_string(image)
        return text

    # 📄 TXT / DOC (basic)
    elif filename.endswith(".txt"):
        return file.read().decode("utf-8")

    else:
        return None

def analyze_with_ai(user_input, category):

    prompt = f"""
You are an expert risk analysis AI.

Analyze the input, Automatically detect its type(email,message, contract, loan, app permissions, job offer, etc.) and return STRICT JSON.

INPUT:
{user_input}

OUTPUT FORMAT:
{{
  "detected_type": "",
  "summary": "",
  "risk_level": "Low/Medium/High",
  "risk_score": {{
    "financial": 0-100,
    "legal": 0-100,
    "privacy": 0-100,
    "overall": 0-100
  }},
  "detected_issues": [],
  "hidden_traps": [],
  "missing_elements": [],
  "personalized_impact": "",
  "consequences": {{
    "if_accept": "",
    "if_reject": ""
  }},
  "scam_signals": [],
  "recommendations": [],
  "negotiation_suggestions": [],
  "final_decision": ""
}}

ONLY RETURN JSON. NO EXPLANATION. NO EXTRA TEXT.
"""

    MODELS = [
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-pro"
    ]

    for model_name in MODELS:
        try:
            print(f"Trying model: {model_name}")

            model = genai.GenerativeModel(model_name)

            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.3}
            )

            content = response.text

            print("RAW RESPONSE:", content[:200])

            content = content.strip()

            if content.startswith("```"):
                content = content.replace("```json", "").replace("```", "").strip()

            # 🔥 Convert to JSON
            parsed_json = json.loads(content)

            return parsed_json

        except Exception as e:
            print(f"❌ Model failed: {model_name} → {e}")
            continue

    return {
        "error": "All Gemini models failed"
    }

