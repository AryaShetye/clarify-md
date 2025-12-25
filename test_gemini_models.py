"""
Test script to find available Gemini models
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("❌ GOOGLE_API_KEY not found in .env file")
    exit(1)

genai.configure(api_key=GOOGLE_API_KEY)

print("🔍 Listing available Gemini models...\n")

try:
    models = genai.list_models()
    available_models = []
    
    for model in models:
        if hasattr(model, 'supported_generation_methods'):
            if 'generateContent' in model.supported_generation_methods:
                available_models.append(model.name)
                print(f"✅ {model.name}")
                if hasattr(model, 'display_name'):
                    print(f"   Display Name: {model.display_name}")
    
    if available_models:
        print(f"\n📋 Found {len(available_models)} available model(s)")
        print(f"🎯 Recommended: {available_models[0]}")
    else:
        print("\n❌ No models found with generateContent support")
        
except Exception as e:
    print(f"❌ Error listing models: {e}")
    print("\n💡 Trying common model names directly...")
    
    common_models = [
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash",
        "gemini-1.5-pro-latest",
        "gemini-1.5-pro",
        "gemini-pro"
    ]
    
    for model_name in common_models:
        try:
            model = genai.GenerativeModel(model_name)
            print(f"✅ {model_name} - Available")
        except Exception as e:
            print(f"❌ {model_name} - {str(e)[:100]}")

