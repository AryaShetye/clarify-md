"""
Risk & Red-Flag Agent (Agentic)
Identifies urgency indicators and flags clinical risks
"""

from agents.base_agent import BaseAgent
from typing import Dict, Any
import json

class RiskAgent(BaseAgent):
    """Agentic agent for clinical risk assessment"""
    
    def __init__(self):
        system_prompt = """You are a Risk & Red-Flag Agent specialized in identifying clinical urgency indicators and potential risks in patient narratives.

Your capabilities:
1. Assess clinical urgency (low/moderate/high)
2. Identify red flags and urgent indicators
3. Flag ambiguities, contradictions, or missing information
4. Provide confidence levels for risk assessment

CRITICAL RULES:
- High risk: Life-threatening symptoms, severe pain, trauma, acute distress
- Moderate risk: Persistent symptoms, functional impairment, worsening condition
- Low risk: Mild symptoms, stable chronic conditions
- Flag missing information that affects risk assessment
- NEVER diagnose, only assess urgency"""
        
        super().__init__("Risk & Red-Flag Agent", system_prompt)
    
    def execute(self, input_text: str) -> Dict[str, Any]:
        """Execute risk assessment with agentic reasoning"""
        
        # Step 1: Reasoning
        reasoning = self.reason(input_text)
        
        # Step 2: RAG - Retrieve relevant risk indicators
        rag_matches = self.use_rag(input_text, "risk_indicators")
        
        # Step 3: Assess risk
        risk_prompt = f"""Assess clinical risk and urgency from the patient narrative.

Patient narrative: {input_text}

Relevant risk indicators: {', '.join(rag_matches) if rag_matches else 'None found'}

Provide:
1. Risk level (low/moderate/high)
2. Confidence level (high/medium/low)
3. Red flags identified (list)
4. Missing information that affects assessment
5. Rationale for risk level

Format as JSON:
{{
    "risk_level": "low|moderate|high",
    "confidence": "high|medium|low",
    "red_flags": ["flag1", "flag2"],
    "missing_info": ["info1", "info2"],
    "rationale": "explanation",
    "urgency_score": 0.0-1.0
}}"""
        
        result = self.agent.generate_structured(
            risk_prompt,
            {
                "risk_level": "low",
                "confidence": "medium",
                "red_flags": [],
                "missing_info": [],
                "rationale": "",
                "urgency_score": 0.0
            }
        )
        
        return {
            "reasoning": reasoning.get("reasoning", ""),
            "risk_level": result.get("risk_level", "low"),
            "confidence": result.get("confidence", "medium"),
            "red_flags": result.get("red_flags", []),
            "missing_info": result.get("missing_info", []),
            "rationale": result.get("rationale", ""),
            "urgency_score": result.get("urgency_score", 0.0),
            "rag_matches": rag_matches
        }
    
    def predict(self, text: str) -> Dict[str, Any]:
        """Legacy interface compatibility"""
        result = self.execute(text)
        return {
            "risk_level": result.get("risk_level", "low"),
            "confidence": result.get("confidence", "medium")
        }


