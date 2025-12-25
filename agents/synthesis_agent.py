from models.model_registry import ModelRegistry

def synthesis_agent(context):
    return ModelRegistry.get().synthesis.generate(context)
