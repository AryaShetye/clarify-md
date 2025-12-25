# llm_config.py
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

if not HF_API_KEY:
    raise RuntimeError(
        "HF_API_KEY not found. "
        "Set it in your .env file or environment variables."
    )

def hf_generate(model: str, prompt: str):
    url = f"https://api-inference.huggingface.co/models/{model}"
    payload = {"inputs": prompt}

    response = requests.post(url, headers=HEADERS, json=payload, timeout=30)

    # Handle model loading or deprecation gracefully
    if response.status_code in [503, 410]:
        return "Model temporarily unavailable. Using fallback reasoning."

    response.raise_for_status()
    data = response.json()

    if isinstance(data, list) and "generated_text" in data[0]:
        return data[0]["generated_text"]

    return str(data)



def hf_classify(model: str, text: str):
    url = f"https://api-inference.huggingface.co/models/{model}"
    payload = {"inputs": text}

    response = requests.post(url, headers=HEADERS, json=payload, timeout=30)
    response.raise_for_status()

    return response.json()

def hf_zero_shot_safe(model: str, text: str, labels: list):
    try:
        url = f"https://api-inference.huggingface.co/models/{model}"
        payload = {
            "inputs": text,
            "parameters": {"candidate_labels": labels}
        }
        response = requests.post(url, headers=HEADERS, json=payload, timeout=30)

        if response.status_code in [410, 503]:
            return None

        response.raise_for_status()
        return response.json()

    except Exception:
        return None

