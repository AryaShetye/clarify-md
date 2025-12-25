"""
Google Gemini API Configuration for CLARIFY.MD

Ownership and boundaries:
- CLARIFY.MD implements the multi-agent architecture, orchestration,
  RAG over a medical ontology, and deterministic safety guardrails.
- Google Gemini provides **bounded reasoning** inside each agent only:
  language understanding, step-wise reasoning, and text generation.

Google-first strategy:
- This module is compatible with free-tier Gemini usage (via
  https://aistudio.google.com / makersuite).
- The same pattern can be migrated to Vertex AI for production
  without changing any agent interfaces.
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import json

load_dotenv()

# Initialize Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise RuntimeError(
        "GOOGLE_API_KEY not found. "
        "Get your free API key from: https://makersuite.google.com/app/apikey"
    )

genai.configure(api_key=GOOGLE_API_KEY)

# Initialize model name - try available models in order
MODEL_NAME = None

# Try to find an available model (order: latest -> stable -> fallback)
model_candidates = [
    "gemini-flash-latest",      # Fast, free tier
    "gemini-pro-latest",        # More capable, free tier  
    "gemini-2.0-flash",         # Newer version
    "gemini-pro",               # Stable fallback
]

for candidate in model_candidates:
    try:
        test_model = genai.GenerativeModel(candidate)
        MODEL_NAME = candidate
        print(f"Using Gemini model: {MODEL_NAME}")
        break
    except Exception:
        continue

# Final fallback
if MODEL_NAME is None:
    MODEL_NAME = "gemini-pro"
    print(f"Using fallback model: {MODEL_NAME}")


class GeminiAgent:
    """Base class for agentic agents using Gemini"""
    
    def __init__(self, system_prompt: str, model_name: Optional[str] = None):
        if model_name is None:
            model_name = MODEL_NAME
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_prompt
        )
        self.system_prompt = system_prompt
        self.model_name = model_name
    
    def generate(self, prompt: str, temperature: float = 0.3, max_tokens: int = 1000) -> str:
        """Generate response with safety settings"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    top_p=0.95,
                    top_k=40,
                ),
                safety_settings=[
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
                        "threshold": "BLOCK_ONLY_HIGH"  # Medical content needs flexibility
                    }
                ]
            )
            
            if response.candidates and response.candidates[0].content:
                return response.candidates[0].content.parts[0].text
            else:
                return "Unable to generate response. Please try again."
                
        except Exception as e:
            error_msg = str(e)
            # If model not found, try fallback
            if "404" in error_msg or "not found" in error_msg.lower():
                try:
                    # Try with -latest suffix if not already present
                    if "-latest" not in self.model_name:
                        fallback_name = f"{self.model_name}-latest"
                        fallback_model = genai.GenerativeModel(
                            model_name=fallback_name,
                            system_instruction=self.system_prompt
                        )
                        response = fallback_model.generate_content(
                            prompt,
                            generation_config=genai.types.GenerationConfig(
                                temperature=temperature,
                                max_output_tokens=max_tokens,
                                top_p=0.95,
                                top_k=40,
                            ),
                            safety_settings=[
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
                                    "threshold": "BLOCK_ONLY_HIGH"
                                }
                            ]
                        )
                        if response.candidates and response.candidates[0].content:
                            return response.candidates[0].content.parts[0].text
                except:
                    pass
            return f"Error: {error_msg}"
    
    def generate_structured(self, prompt: str, response_format: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured JSON response"""
        structured_prompt = f"""{prompt}

Respond in valid JSON format matching this schema:
{json.dumps(response_format, indent=2)}

Return ONLY valid JSON, no additional text."""
        
        response_text = self.generate(structured_prompt, temperature=0.2)
        
        # Extract JSON from response
        try:
            # Try to find JSON in response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback: return parsed structure
        return response_format


def get_medical_ontology() -> Dict[str, list]:
    """Return the local medical ontology used for RAG.

    Ownership:
    - CLARIFY.MD owns this ontology and retrieval logic.
    - Gemini does NOT invent medical knowledge here; it reasons *over*
      structured concepts supplied by the system.

    Google-first extension path:
    - In production, this function can delegate to a Google Vertex AI
      Search index (medical ontology / FHIR resources) while preserving
      the same interface. A mock/local implementation is used here to
      keep the project hackathon-friendly and free-tier compatible.
    """
    return {
        "metaphors": {
            "pressure/tightness": ["tension", "cephalalgia", "pressure sensation", "constriction"],
            "hollow/empty": ["palpitations", "chest discomfort", "sensation of emptiness"],
            "burning": ["dyspepsia", "gastroesophageal reflux", "burning sensation"],
            "sharp/stabbing": ["acute pain", "sharp pain", "stabbing sensation"],
            "dull/aching": ["chronic pain", "dull ache", "persistent discomfort"],
            "fluttering": ["palpitations", "arrhythmia", "irregular heartbeat"],
            "snapping/breaking": ["acute exacerbation", "sudden onset", "acute episode"],
            "weight/heaviness": ["chest heaviness", "dyspnea", "respiratory distress"],
            "foggy/cloudy": ["cognitive impairment", "mental fog", "confusion"],
            "racing": ["tachycardia", "anxiety", "hyperarousal"]
        },
        "emotional_biomarkers": {
            "fear": ["anxiety-related distress", "apprehension", "fearful affect"],
            "panic": ["acute anxiety", "panic-like symptoms", "severe distress"],
            "sadness": ["low mood", "depressed affect", "dysphoria"],
            "anger": ["irritability", "agitation", "hostile affect"],
            "confusion": ["cognitive disorientation", "mental confusion", "altered mental status"],
            "helplessness": ["sense of powerlessness", "vulnerability", "loss of control"]
        },
        "risk_indicators": {
            "high": ["chest pain", "shortness of breath", "loss of consciousness", "severe pain", "trauma", "bleeding"],
            "moderate": ["persistent symptoms", "worsening condition", "functional impairment"],
            "low": ["mild symptoms", "stable condition", "chronic well-managed"]
        }
    }


