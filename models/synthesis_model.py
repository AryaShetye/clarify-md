from transformers import pipeline

class SynthesisModel:
    def __init__(self):
        self.model = pipeline(
            "text2text-generation",
            model="google/flan-t5-small",
            max_length=220
        )

    def generate(self, context):
        prompt = f"""
You are assisting in drafting a clinical note.

Write in formal medical documentation style.
Avoid conversational tone.
Do NOT diagnose.
Do NOT suggest treatment.

Use the following structure strictly:

- Presenting Description:
- Associated Emotional State:
- Clinical Impression (non-diagnostic):
- Uncertainties / Information Gaps:

Context:
{context}

Clinical Note:
"""
        return self.model(prompt)[0]["generated_text"].strip()
