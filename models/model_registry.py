from models.emotion_model import EmotionModel
from models.metaphor_model import MetaphorModel
from models.risk_model import RiskModel
from models.synthesis_model import SynthesisModel

class ModelRegistry:
    _instance = None

    def __init__(self):
        self.emotion = EmotionModel()
        self.metaphor = MetaphorModel()
        self.risk = RiskModel()
        self.synthesis = SynthesisModel()

    @classmethod
    def get(cls):
        if not cls._instance:
            cls._instance = ModelRegistry()
        return cls._instance
