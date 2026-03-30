import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

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

Analyze the following input. Automatically detect its type 
(email,message, contract, loan, app permissions, job offer, etc.) and return STRICT JSON.

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

ONLY RETURN JSON. NO EXTRA TEXT.
"""

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "AI Risk Analyzer"
    }

    data = {
        "model": "openrouter/auto",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    response = requests.post(url, headers=headers, json=data)

    print("STATUS:", response.status_code)
    print("RAW RESPONSE:", response.text)

    if response.status_code != 200:
        return {"error": response.text}

    result = response.json()
    

    try:
        content = result["choices"][0]["message"]["content"]

        # 🔥 Remove markdown ```json ```
        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "").strip()

        # 🔥 Convert string → JSON
        parsed_json = json.loads(content)

        return parsed_json

    except Exception as e:
        return {
            "error": "Failed to parse AI response",
            "details": str(e),
            "raw": content if 'content' in locals() else None
        }