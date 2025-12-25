from transformers import pipeline

class RiskModel:
    def __init__(self):
        self.model = pipeline(
            "zero-shot-classification",
            model="typeform/distilbert-base-uncased-mnli"
        )
        self.labels = ["low", "moderate", "high"]

    def predict(self, text):
        result = self.model(text, self.labels)
        label = result["labels"][0]
        score = result["scores"][0]

        return {
            "risk_level": label,
            "confidence": round(score, 2)
        }
