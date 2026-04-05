import os
import re
import requests
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def get_groq_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

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

ONLY RETURN JSON. NO EXTRA TEXT.GIVE CLEAR EXPLANATIONS.
"""

    GROQ_MODELS = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "qwen/qwen3-32b"
    ]
    client = get_groq_client()
    for model_name in GROQ_MODELS:
        try:
            print(f"Trying Groq model: {model_name}")

            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are an expert risk analysis AI. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            content = response.choices[0].message.content.strip()

            print("RAW RESPONSE:", content[:200])

            # 🔥 Clean markdown if exists
            if content.startswith("```"):
                content = re.sub(r"```json|```", "", content).strip()

            # 🔥 Convert to JSON
            parsed_json = json.loads(content)

            return parsed_json

        except Exception as e:
            print(f"❌ Groq failed: {model_name} → {e}")
            continue

    return {
        "error": "All Groq models failed"
    }