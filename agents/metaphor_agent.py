from models.model_registry import ModelRegistry

def metaphor_agent(text):
    return ModelRegistry.get().metaphor.translate(text)
