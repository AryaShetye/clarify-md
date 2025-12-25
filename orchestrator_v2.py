"""
Agentic Orchestrator for CLARIFY.MD
Coordinates multi-agent collaboration with reasoning and RAG
"""
from agents.metaphor_agent_v2 import MetaphorAgent
from agents.emotion_agent_v2 import EmotionAgent
from agents.risk_agent_v2 import RiskAgent
from agents.synthesis_agent_v2 import SynthesisAgent
from safety_guardrails import apply_safety_guardrails
from agents.what_if_agent import WhatIfAgent
from typing import Dict, Any
import time


class AgenticOrchestrator:
    """Orchestrates agentic agents with collaboration and reasoning.

    Ownership:
    - CLARIFY.MD implements orchestration, safety overrides, and
      agent collaboration.
    - Individual agents use Google Gemini **only as bounded reasoning
      engines**; Gemini is never the system or the final arbiter of risk.
    """
    
    def __init__(self):
        # Agent boundaries are preserved – no changes to agent classes
        # or their public interfaces.
        self.metaphor_agent = MetaphorAgent()
        self.emotion_agent = EmotionAgent()
        self.risk_agent = RiskAgent()
        self.synthesis_agent = SynthesisAgent()
        self.what_if_agent = WhatIfAgent()

    def _apply_deterministic_risk_overrides(self, patient_text: str, risk_result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply SMALL, rule-based high-risk overrides on top of the RiskAgent.

        Architectural intent:
        - CLARIFY.MD, not Gemini, owns high-risk escalation.
        - Gemini may *suggest* a risk level, but deterministic rules
          for critical symptoms (chest pain, dyspnea, neurological
          compromise) can only escalate, never downgrade, risk.

        This function preserves the existing agent flow and signatures –
        it only adjusts the risk_result dict produced by RiskAgent.
        """
        text = (patient_text or "").lower()
        risk_level = str(risk_result.get("risk_level", "low")).lower()
        red_flags = list(risk_result.get("red_flags", []) or [])
        rationale = risk_result.get("rationale", "") or ""
        urgency_score = float(risk_result.get("urgency_score", 0.0) or 0.0)

        # Non-negotiable high-risk symptom patterns (deterministic)
        high_risk_triggers = {
            "chest pain": "chest pain with possible cardiac or pulmonary aetiology",
            "tightness in my chest": "chest tightness",
            "pressure in my chest": "chest pressure",
            "shortness of breath": "dyspnea / shortness of breath",
            "cant breathe": "subjective inability to breathe",
            "cannot breathe": "subjective inability to breathe",
            "trouble breathing": "respiratory difficulty",
            "difficulty breathing": "respiratory difficulty",
            "face drooping": "possible facial droop (neurological)",
            "slurred speech": "slurred speech (neurological)",
            "weakness on one side": "unilateral weakness (neurological)",
            "numb on one side": "unilateral sensory change",
            "sudden weakness": "sudden focal weakness",
            "seizure": "possible seizure activity",
            "fit": "possible seizure activity",
            "fainted": "loss of consciousness",
            "passed out": "loss of consciousness",
            "blackout": "loss of consciousness",
        }

        triggered_flags: List[str] = []
        for phrase, clinical_flag in high_risk_triggers.items():
            if phrase in text:
                triggered_flags.append(clinical_flag)

        if triggered_flags:
            # Deterministic override: enforce HIGH risk
            if "high" not in risk_level:
                risk_level = "high"
            # Ensure urgency score is at least 0.8 when high-risk triggers present
            urgency_score = max(urgency_score, 0.8)

            # Merge red flags and mark that escalation was rule-based
            for flag in triggered_flags:
                if flag not in red_flags:
                    red_flags.append(flag)

            escalation_note = "Deterministic safety override: high-risk symptom(s) detected in patient narrative."
            if escalation_note not in red_flags:
                red_flags.append(escalation_note)

            if "deterministic_override" not in rationale.lower():
                rationale = (rationale + " " if rationale else "") + "Deterministic_override: high-risk language present; risk not downgraded below HIGH."

        risk_result["risk_level"] = risk_level
        risk_result["urgency_score"] = urgency_score
        risk_result["red_flags"] = red_flags
        risk_result["rationale"] = rationale.strip()

        return risk_result
    
    def run_what_if(self, baseline_text: str, hypothetical_text: str) -> Dict[str, Any]:
        """Run baseline + hypothetical CLARIFY.MD and compare them.

        This is used ONLY in the patient What-If simulator; results
        are not stored and never linked to a doctor.
        """
        baseline = self.run_clarify(baseline_text)
        hypothetical = self.run_clarify(hypothetical_text)

        # Build a compact context for the WhatIfAgent
        context = {
            "baseline": {
                "metaphor": baseline.get("metaphor", {}),
                "emotions": baseline.get("emotions", {}),
                "risk": baseline.get("risk", {}),
                "summary": baseline.get("summary", {}),
            },
            "hypothetical": {
                "metaphor": hypothetical.get("metaphor", {}),
                "emotions": hypothetical.get("emotions", {}),
                "risk": hypothetical.get("risk", {}),
                "summary": hypothetical.get("summary", {}),
            },
        }
        comparison = self.what_if_agent.execute(context)

        return {
            "baseline": baseline,
            "hypothetical": hypothetical,
            "comparison": comparison,
        }

    def run_clarify(self, patient_text: str) -> Dict[str, Any]:
        """
        Run the full agentic pipeline:
        1. Parallel agent execution with reasoning
        2. Agent collaboration
        3. Synthesis with integrated context

        IMPORTANT SAFETY NOTE:
        - High-risk escalation is never solely dependent on Gemini.
        - After the RiskAgent (Gemini-powered reasoning) runs, CLARIFY.MD
          applies deterministic overrides for critical symptoms.
        """
        
        # Step 1: Parallel agent execution (with reasoning)
        print("🔍 Analyzing patient narrative with agentic agents...")
        
        metaphor_result = self.metaphor_agent.execute(patient_text)
        emotion_result = self.emotion_agent.execute(patient_text)
        risk_result = self.risk_agent.execute(patient_text)

        # Apply small, rule-based high-risk overrides WITHOUT changing agent APIs
        risk_result = self._apply_deterministic_risk_overrides(patient_text, risk_result)
        
        # Step 2: Agent collaboration (optional enhancement)
        # Each agent can refine based on others' findings
        collaboration_context = {
            "metaphor": metaphor_result,
            "emotion": emotion_result,
            "risk": risk_result
        }
        
        # Step 3: Synthesis with full context
        synthesis_context = {
            "patient_text": patient_text,
            "metaphor": {
                "translation": metaphor_result.get("clinical_translation", ""),
                "metaphors": metaphor_result.get("metaphors", []),
                "confidence": metaphor_result.get("confidence", "medium"),
                "uncertainties": metaphor_result.get("uncertainties", [])
            },
            "emotion": {
                "emotions": emotion_result.get("emotions", []),
                "summary": emotion_result.get("summary", ""),
                "significant_count": len(emotion_result.get("emotions", []))
            },
            "risk": {
                "risk_level": risk_result.get("risk_level", "low"),
                "confidence": risk_result.get("confidence", "medium"),
                "red_flags": risk_result.get("red_flags", []),
                "missing_info": risk_result.get("missing_info", []),
                "rationale": risk_result.get("rationale", "")
            }
        }
        
        synthesis_result = self.synthesis_agent.execute(synthesis_context)
        
        # Step 4: Compile final result
        # Extract reasoning strings (reason() returns dict with "reasoning" key)
        def extract_reasoning(reasoning_data):
            """Extract reasoning text from reasoning data (can be dict or string).

            This maintains transparency by exposing **agent reasoning**
            separately from system-level orchestration and guardrails.
            """
            if isinstance(reasoning_data, dict):
                return reasoning_data.get("reasoning", str(reasoning_data))
            elif isinstance(reasoning_data, str):
                return reasoning_data
            else:
                return str(reasoning_data) if reasoning_data else ""
        
        result = {
            "patient_voice": patient_text,
            "metaphor": metaphor_result,
            "emotions": emotion_result,
            "risk": risk_result,
            "summary": synthesis_result,
            "agent_reasoning": {
                "metaphor": extract_reasoning(metaphor_result.get("reasoning", "")),
                "emotion": extract_reasoning(emotion_result.get("reasoning", "")),
                "risk": extract_reasoning(risk_result.get("reasoning", "")),
                "synthesis": extract_reasoning(synthesis_result.get("reasoning", ""))
            },
            "processing_metadata": {
                "agents_used": 4,
                "rag_enabled": True,
                "collaboration_enabled": True,
                # Flag that deterministic safety overrides were applied at system level
                "deterministic_risk_overrides": True
            }
        }
        
        # Step 5: Apply safety guardrails (deterministic, CLARIFY.MD-owned)
        result = apply_safety_guardrails(result)
        
        return result


# Singleton instance
_orchestrator = None

def get_orchestrator() -> AgenticOrchestrator:
    """Get singleton orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgenticOrchestrator()
    return _orchestrator

def run_clarify(patient_text: str) -> Dict[str, Any]:
    """Main entry point for CLARIFY.MD"""
    orchestrator = get_orchestrator()
    return orchestrator.run_clarify(patient_text)


# Convenience function
def run_what_if(baseline_text: str, hypothetical_text: str) -> Dict[str, Any]:
    orchestrator = get_orchestrator()
    return orchestrator.run_what_if(baseline_text, hypothetical_text)