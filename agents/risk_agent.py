from models.model_registry import ModelRegistry

def risk_agent(text):
    return ModelRegistry.get().risk.predict(text)
