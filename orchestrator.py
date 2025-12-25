from agents.emotion_agent import emotion_agent
from agents.metaphor_agent import metaphor_agent
from agents.risk_agent import risk_agent
from agents.synthesis_agent import synthesis_agent

def run_clarify(patient_text):
    emotions = emotion_agent(patient_text)
    metaphor = metaphor_agent(patient_text)
    risk = risk_agent(patient_text)

    context = f"""
Presenting complaint:
{patient_text}

Symptom interpretation:
{metaphor}

Emotional state:
{', '.join([e['emotion'] for e in emotions]) or 'No prominent affect'}

Risk level:
{risk['risk_level']}
"""


    summary = synthesis_agent(context)

    return {
        "patient_voice": patient_text,
        "metaphor": metaphor,
        "emotions": emotions,
        "risk": risk,
        "summary": summary
    }
