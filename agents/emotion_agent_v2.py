"""
Emotional Biomarker Agent (Agentic)
Extracts emotional states and quantifies intensity as clinical signals
"""
from agents.base_agent import BaseAgent
from typing import Dict, Any, List
import json


class EmotionAgent(BaseAgent):
    """Agentic agent for extracting emotional biomarkers"""
    
    def __init__(self):
        system_prompt = """You are an Emotional Biomarker Agent specialized in identifying emotional states in patient narratives and quantifying them as clinical signals.

Your capabilities:
1. Detect emotional states (fear, panic, sadness, anger, confusion, helplessness, etc.)
2. Quantify emotional intensity (0.0-1.0 scale)
3. Map emotions to clinical terminology
4. Identify emotional patterns that may indicate clinical significance

CRITICAL RULES:
- Emotion ≠ pathology by default
- Quantify intensity objectively
- Use clinical terminology for emotional states
- Flag high-intensity emotions that may require attention
- Preserve patient dignity"""
        
        super().__init__("Emotional Biomarker Agent", system_prompt)
    
    def execute(self, input_text: str) -> Dict[str, Any]:
        """Execute emotion extraction with agentic reasoning"""
        
        # Step 1: Reasoning
        reasoning = self.reason(input_text)
        
        # Step 2: RAG - Retrieve relevant emotional biomarkers
        rag_matches = self.use_rag(input_text, "emotional_biomarkers")
        
        # Step 3: Extract emotions
        extraction_prompt = f"""Extract emotional biomarkers from the patient narrative.

Patient narrative: {input_text}

Relevant emotional concepts: {', '.join(rag_matches) if rag_matches else 'None found'}

For each detected emotion, provide:
1. Emotion name (fear, panic, sadness, anger, confusion, helplessness, etc.)
2. Intensity score (0.0-1.0, where 0.5+ is clinically significant)
3. Clinical terminology mapping
4. Evidence from text

Format as JSON array:
[
    {{
        "emotion": "emotion_name",
        "intensity": 0.0-1.0,
        "clinical_term": "clinical description",
        "evidence": "text evidence",
        "significance": "high|medium|low"
    }}
]"""
        
        result_text = self.agent.generate(extraction_prompt, temperature=0.2)
        
        # Parse JSON from response
        try:
            json_start = result_text.find('[')
            json_end = result_text.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = result_text[json_start:json_end]
                emotions = json.loads(json_str)
            else:
                emotions = []
        except:
            emotions = []
        
        # Filter for clinically significant emotions (intensity >= 0.4)
        significant_emotions = [
            e for e in emotions 
            if isinstance(e, dict) and e.get("intensity", 0) >= 0.4
        ]
        
        return {
            "reasoning": reasoning.get("reasoning", ""),
            "emotions": significant_emotions,
            "all_emotions": emotions,
            "rag_matches": rag_matches,
            "summary": self._generate_summary(significant_emotions)
        }
    
    def _generate_summary(self, emotions: List[Dict[str, Any]]) -> str:
        """Generate summary of emotional state"""
        if not emotions:
            return "No clinically significant emotional distress identified"
        
        high_intensity = [e for e in emotions if e.get("intensity", 0) >= 0.7]
        if high_intensity:
            return f"Marked {high_intensity[0].get('clinical_term', 'emotional distress')} detected"
        
        return f"Moderate emotional distress: {', '.join([e.get('emotion', '') for e in emotions[:2]])}"
    
    def predict(self, text: str) -> List[Dict[str, Any]]:
        """Legacy interface compatibility"""
        result = self.execute(text)
        return result.get("emotions", [])


