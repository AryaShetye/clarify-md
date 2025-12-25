from transformers import pipeline

class EmotionModel:
    def __init__(self):
        self.model = pipeline(
            "text-classification",
            model="bhadresh-savani/distilbert-base-uncased-emotion",
            top_k=None
        )

    def predict(self, text):
        raw = self.model(text)
        results = raw[0] if isinstance(raw[0], list) else raw

        emotions = []
        for r in results:
            if r["score"] > 0.25:
                emotions.append({
                    "emotion": r["label"],
                    "intensity": round(float(r["score"]), 2)
                })
        return emotions
