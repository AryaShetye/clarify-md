from models.model_registry import ModelRegistry

def emotion_agent(text):
    return ModelRegistry.get().emotion.predict(text)
