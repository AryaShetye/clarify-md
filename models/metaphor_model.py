from transformers import pipeline

class MetaphorModel:
    def __init__(self):
        self.model = pipeline(
            "text2text-generation",
            model="google/flan-t5-small",
            max_length=128
        )

    def translate(self, text):
        prompt = (
            "Convert the patient's metaphorical description into "
            "neutral, non-diagnostic clinical language.\n\n"
            f"Patient: {text}\nClinical:"
        )
        out = self.model(prompt)[0]["generated_text"]
        return out.strip()
