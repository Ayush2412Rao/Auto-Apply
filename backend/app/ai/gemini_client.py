import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from google import genai
from google.genai import types
from backend.app.config import settings

class GeminiClient:
    def __init__(self):
        self.api_key = settings.get_gemini_key()
        if not self.api_key:
            print("WARNING: GEMINI_API_KEY is not set in environment or .env")
            self.client = None
        else:
            self.client = genai.Client(api_key=self.api_key)

    def generate_json(self, prompt: str, system_instruction: Optional[str] = None, model: Optional[str] = None) -> Dict[str, Any]:
        """Generates structured JSON output from Gemini."""
        if not self.client:
            raise ValueError("Gemini API client is not initialized. Please verify your GEMINI_API_KEY.")

        chosen_model = model or settings.GEMINI_MODEL
        
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
        )
        if system_instruction:
            config.system_instruction = system_instruction

        response = self.client.models.generate_content(
            model=chosen_model,
            contents=prompt,
            config=config
        )
        
        try:
            return json.loads(response.text)
        except Exception as e:
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            return json.loads(text.strip())

gemini_client = GeminiClient()
