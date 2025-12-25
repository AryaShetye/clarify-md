"""
Metaphor Translation Agent (Agentic)
Maps figurative language to medical terminology using RAG and reasoning
"""
from agents.base_agent import BaseAgent
from typing import Dict, Any
import json


class MetaphorAgent(BaseAgent):
    """Agentic agent for translating patient metaphors to clinical language"""
    
    def __init__(self):
        system_prompt = """You are a Metaphor Translation Agent specialized in converting patient's figurative language into neutral, non-diagnostic clinical terminology.

Your capabilities:
1. Identify metaphorical expressions in patient narratives
2. Map metaphors to appropriate clinical concepts using medical ontology
3. Preserve the patient's original meaning while translating to clinical language
4. Flag ambiguous metaphors that require clarification

CRITICAL RULES:
- NEVER diagnose
- NEVER suggest treatment
- Use neutral, objective clinical language
- Preserve patient dignity and context
- Indicate confidence levels
- Flag uncertainties"""
        
        super().__init__("Metaphor Translation Agent", system_prompt)
    
    def execute(self, input_text: str) -> Dict[str, Any]:
        """Execute metaphor translation with agentic reasoning"""
        
        # Step 1: Reasoning
        reasoning = self.reason(input_text)
        
        # Step 2: RAG - Retrieve relevant medical concepts
        rag_matches = self.use_rag(input_text, "metaphors")
        
        # Step 3: Generate translation
        translation_prompt = f"""Translate the patient's metaphorical language into clinical terminology.

Patient narrative: {input_text}

Relevant medical concepts from ontology: {', '.join(rag_matches) if rag_matches else 'None found'}

Provide:
1. Identified metaphors (list)
2. Clinical translation (single sentence, neutral tone)
3. Confidence level (high/medium/low)
4. Uncertainties or ambiguities

Format as JSON:
{{
    "metaphors": ["metaphor1", "metaphor2"],
    "clinical_translation": "translated clinical description",
    "confidence": "high|medium|low",
    "uncertainties": ["uncertainty1", "uncertainty2"]
}}"""
        
        result = self.agent.generate_structured(
            translation_prompt,
            {
                "metaphors": [],
                "clinical_translation": "",
                "confidence": "medium",
                "uncertainties": []
            }
        )
        
        # Step 4: Combine reasoning with result
        return {
            "reasoning": reasoning.get("reasoning", ""),
            "metaphors": result.get("metaphors", []),
            "clinical_translation": result.get("clinical_translation", ""),
            "confidence": result.get("confidence", "medium"),
            "uncertainties": result.get("uncertainties", []),
            "rag_matches": rag_matches
        }
    
    def translate(self, text: str) -> str:
        """Legacy interface compatibility"""
        result = self.execute(text)
        return result.get("clinical_translation", "")


