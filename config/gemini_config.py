"""
Google Gemini API Configuration
Uses free-tier Gemini Flash model for hackathon MVP
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise RuntimeError(
        "GOOGLE_API_KEY not found. "
        "Get your free API key from: https://makersuite.google.com/app/apikey"
    )

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# Use Gemini Flash 1.5 (free tier, fast, capable)
MODEL_NAME = "gemini-1.5-flash"

# Safety settings - critical for medical context
SAFETY_SETTINGS = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_ONLY_HIGH"  # Allow medical discussions
    }
]

def get_model():
    """Get configured Gemini model instance"""
    return genai.GenerativeModel(
        model_name=MODEL_NAME,
        safety_settings=SAFETY_SETTINGS
    )

