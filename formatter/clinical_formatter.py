import re

def emotion_to_clinical(emotions):
    if not emotions:
        return ["- No clinically significant emotional distress identified"]

    out = []
    for e in emotions:
        intensity = e.get("intensity", 0)

        if intensity >= 0.7:
            level = "Marked"
        elif intensity >= 0.4:
            level = "Moderate"
        else:
            continue  # suppress low signal

        mapping = {
            "fear": "anxiety-related distress",
            "sadness": "low mood",
            "anger": "irritability",
            "joy": "positive affect"
        }

        label = mapping.get(e["emotion"], "emotional distress")
        out.append(f"- {level} {label}")

    return out or ["- No clinically significant emotional distress identified"]


def format_for_clinician(result):
    return {
        "patient_voice": result["patient_voice"],

        "emotions": emotion_to_clinical(result.get("emotions", [])),

        "metaphor": (
            ["- Subjective chest heaviness described (non-specific symptom expression)"]
            if result.get("metaphor") in ["neutral", None]
            else [f"- {result['metaphor']}"]
        ),


        "risk": [
            f"- {result['risk']['risk_level'].capitalize()} clinical urgency"
        ],

        "summary": clean_summary(result["summary"]),

        "uncertainties": [
            "Symptom onset not clearly specified",
            "Severity and progression unclear"
        ],

        "notes": [
            "Correlate with vital signs and clinical examination",
            "Interpret in full clinical context"
        ]
    }

def clean_summary(text: str) -> str:
    if not text:
        return ""

    # Remove bullet/dot garbage like • • • • or ..... 
    text = re.sub(r"[•·\.]{2,}", " ", text)

    # Remove leftover structural labels
    forbidden = [
        "Associated Emotional State",
        "Clinical Impression",
        "Uncertainties",
        "Information Gaps",
        "Context",
        "Emotional signals",
        "Risk assessment",
        "Associated E"
    ]

    for f in forbidden:
        text = text.replace(f, "")

    # Normalize medical tone
    replacements = {
        "the patient": "Patient",
        "The patient": "Patient",
        "reports": "describes",
        "appears to": "is noted to",
        "suggests": "is suggestive of"
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()

