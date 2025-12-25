"""
Clinical Synthesis Agent (Agentic)
Produces structured, neutral summaries integrating all agent findings
"""
from agents.base_agent import BaseAgent
from typing import Dict, Any
import json


class SynthesisAgent(BaseAgent):
    """Agentic agent for synthesizing clinical summaries"""
    
    def __init__(self):
        system_prompt = """You are a Clinical Synthesis Agent specialized in creating structured, neutral clinical summaries from multiple agent analyses.

Your capabilities:
1. Integrate findings from metaphor, emotion, and risk agents
2. Produce structured clinical documentation
3. Separate patient voice from clinical interpretation
4. Highlight uncertainties and information gaps
5. Maintain non-diagnostic, objective tone

CRITICAL RULES:
- Write in formal medical documentation style
- Avoid conversational tone
- NEVER diagnose
- NEVER suggest treatment
- Clearly separate patient voice from interpretation
- Highlight uncertainties prominently
- Preserve patient dignity and context"""
        
        super().__init__("Clinical Synthesis Agent", system_prompt)
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute synthesis with agentic reasoning"""
        
        # Step 1: Reasoning about synthesis
        context_text = json.dumps(context, indent=2)
        reasoning = self.reason(context_text)
        
        # Step 2: Generate structured summary
        synthesis_prompt = f"""Synthesize a clinical summary from the following agent analyses.

Context:
{context_text}

Create a structured clinical note with these sections:

1. Presenting Description: Patient's narrative in their own words (brief)
2. Symptom Interpretation: Clinical translation of metaphors and symptoms
3. Emotional State: Clinical description of emotional biomarkers
4. Risk Assessment: Urgency level and red flags
5. Clinical Impression: Non-diagnostic summary of findings
6. Uncertainties: Information gaps, ambiguities, missing data
7. Notes for Clinician: Contextual reminders

Write in formal medical documentation style. Be concise but comprehensive."""
        
        summary_text = self.agent.generate(synthesis_prompt, temperature=0.3, max_tokens=800)
        
        # Step 3: Extract structured components
        structured_prompt = f"""Extract structured components from this clinical summary:

{summary_text}

Format as JSON:
{{
    "presenting_description": "brief patient narrative",
    "symptom_interpretation": "clinical translation",
    "emotional_state": "emotional biomarkers",
    "risk_assessment": "risk level and flags",
    "clinical_impression": "non-diagnostic summary",
    "uncertainties": ["uncertainty1", "uncertainty2"],
    "notes_for_clinician": ["note1", "note2"]
}}"""
        
        structured = self.agent.generate_structured(
            structured_prompt,
            {
                "presenting_description": "",
                "symptom_interpretation": "",
                "emotional_state": "",
                "risk_assessment": "",
                "clinical_impression": "",
                "uncertainties": [],
                "notes_for_clinician": []
            }
        )
        
        return {
            "reasoning": reasoning.get("reasoning", ""),
            "full_summary": summary_text,
            "structured": structured,
            "raw_summary": summary_text
        }
    
    def generate(self, context: str) -> str:
        """Legacy interface compatibility"""
        # Parse context if it's a string
        if isinstance(context, str):
            # Try to extract structured info from context string
            context_dict = {
                "patient_text": context,
                "metaphor": "",
                "emotions": [],
                "risk": {"risk_level": "unknown"}
            }
        else:
            context_dict = context
        
        result = self.execute(context_dict)
        return result.get("full_summary", result.get("raw_summary", ""))


